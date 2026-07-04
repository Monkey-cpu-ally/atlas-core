"""Transcripts — source-agnostic storage + LLM summarisation.

The existing `youtube_transcripts_private` collection is kept for
backward compat (consent-gated, YouTube-specific). This module adds a
new `transcripts` collection that stores transcripts from ANY source:
YouTube, uploaded audio, meeting recordings, podcasts, lectures.

Two operations:

    store(transcript)     → persist row, return doc
    summarise(id)         → call Claude via emergentintegrations,
                            produce structured summary, persist to
                            `transcript_summaries` + write a
                            knowledge_record + memory_bank row.

All writes are real MongoDB rows. LLM calls use the Emergent LLM key
already present in /app/backend/.env. No placeholder / mock data.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

from services import memory_bank as mb

logger = logging.getLogger("atlas.transcripts")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
SUMMARY_MODEL = os.environ.get("TRANSCRIPT_SUMMARY_MODEL", "claude-sonnet-4-6")

_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _transcripts():   return _db()["transcripts"]
def _summaries():     return _db()["transcript_summaries"]
def _knowledge():     return _db()["knowledge_records"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class TranscriptSource(str, Enum):
    YOUTUBE           = "youtube"
    AUDIO_UPLOAD      = "audio_upload"
    MEETING           = "meeting"
    PODCAST           = "podcast"
    LECTURE           = "lecture"
    MANUAL_PASTE      = "manual_paste"
    OTHER             = "other"


class Transcript(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    source: TranscriptSource = TranscriptSource.OTHER
    source_url: Optional[str] = None
    author_or_channel: Optional[str] = None
    duration_seconds: Optional[float] = None
    language: str = "en"

    # Full transcript text (chunked at ingest if very long)
    text: str
    word_count: Optional[int] = None

    # Optional linkage
    youtube_channel_id: Optional[str] = None
    subject_slug: Optional[str] = None
    agent: str = "minerva"
    tags: List[str] = Field(default_factory=list)

    # Bookkeeping
    summary_id: Optional[str] = None
    captured_at: str = Field(default_factory=_now)


class TranscriptSummary(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    transcript_id: str
    model: str
    one_line: str
    key_points: List[str]
    identified_subjects: List[str]        # from 22-subject taxonomy
    concepts: List[str]
    tokens_in_estimated: int
    tokens_out_estimated: int
    knowledge_record_id: Optional[str] = None
    memory_bank_id: Optional[str] = None
    generated_at: str = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
async def store(transcript: Transcript) -> Dict[str, Any]:
    """Persist a transcript. Idempotent by (source_url) — repeat calls
    with the same url overwrite the text + word_count but keep the id."""
    doc = transcript.model_dump()
    doc["word_count"] = doc["word_count"] or len(transcript.text.split())

    if transcript.source_url:
        existing = await _transcripts().find_one({"source_url": transcript.source_url})
        if existing:
            update = {k: v for k, v in doc.items()
                      if k not in ("id", "captured_at", "summary_id")}
            await _transcripts().update_one({"_id": existing["_id"]}, {"$set": update})
            return await _transcripts().find_one(
                {"_id": existing["_id"]}, {"_id": 0},
            )

    await _transcripts().insert_one(doc.copy())
    return doc


async def get(transcript_id: str) -> Optional[Dict[str, Any]]:
    return await _transcripts().find_one({"id": transcript_id}, {"_id": 0})


async def list_transcripts(
    source: Optional[str] = None,
    subject_slug: Optional[str] = None,
    agent: Optional[str] = None,
    limit: int = 40,
) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if source: q["source"] = source
    if subject_slug: q["subject_slug"] = subject_slug
    if agent: q["agent"] = agent
    cur = _transcripts().find(q, {"_id": 0, "text": 0}).sort("captured_at", -1).limit(limit)
    return [d async for d in cur]


# ---------------------------------------------------------------------------
# Summarisation (real LLM via Emergent key)
# ---------------------------------------------------------------------------
_SUMMARY_SYSTEM = (
    "You are Atlas · a research analyst. You receive a transcript and MUST reply "
    "with a single JSON object (no prose, no code fences, no commentary) that has "
    "these exact keys:\n"
    "  one_line              (string ≤ 220 chars)\n"
    "  key_points            (list of 5-7 short strings, each ≤ 200 chars)\n"
    "  identified_subjects   (list of slugs from the provided taxonomy; empty list if none apply)\n"
    "  concepts              (list of 5-12 short concept phrases)\n"
    "If the transcript is very short or empty, still return the shape with empty lists."
)


def _valid_subjects(taxonomy: List[str], picked: List[str]) -> List[str]:
    """Whitelist against the 22-subject taxonomy — no hallucinated slugs."""
    allow = set(taxonomy)
    return [s for s in picked if s in allow]


def _extract_json(raw: str) -> Optional[Dict[str, Any]]:
    """Model sometimes wraps JSON in ``` or trailing prose — recover it."""
    if not raw:
        return None
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:                          # noqa: BLE001
        return None


async def summarise(transcript_id: str) -> Dict[str, Any]:
    """Generate + persist a summary. Uses the real Emergent LLM key."""
    if not EMERGENT_LLM_KEY:
        return {"ok": False, "reason": "EMERGENT_LLM_KEY not set"}

    doc = await get(transcript_id)
    if not doc:
        return {"ok": False, "reason": "transcript not found"}
    text = (doc.get("text") or "").strip()
    if not text:
        return {"ok": False, "reason": "transcript has no text"}

    # Load the 22-subject taxonomy (canonical whitelist)
    from services import subjects as subj_svc
    subjects = await subj_svc.list_subjects(enabled_only=True)
    taxonomy = [s["slug"] for s in subjects]

    # Chunk very long transcripts to keep the request under safe budget
    MAX_CHARS = 40_000
    excerpt = text[:MAX_CHARS]
    truncated = len(text) > MAX_CHARS

    user_prompt = (
        f"TRANSCRIPT TITLE: {doc.get('title')}\n"
        f"SOURCE: {doc.get('source')}\n"
        f"URL: {doc.get('source_url') or '-'}\n"
        f"LANGUAGE: {doc.get('language')}\n"
        f"WORD COUNT: {doc.get('word_count') or len(text.split())}\n"
        f"TRUNCATED: {truncated}\n\n"
        f"AVAILABLE SUBJECT SLUGS (whitelist; only these are valid):\n"
        f"  {', '.join(taxonomy)}\n\n"
        f"TRANSCRIPT:\n{excerpt}"
    )

    # Real LLM call via Emergent key
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"transcript-summary-{transcript_id}",
        system_message=_SUMMARY_SYSTEM,
    ).with_model("anthropic", SUMMARY_MODEL)

    try:
        raw = await chat.send_message(UserMessage(text=user_prompt))
    except Exception as exc:                    # noqa: BLE001
        logger.exception("LLM summarisation failed")
        return {"ok": False, "reason": f"LLM call failed: {exc}"}

    if not isinstance(raw, str):
        raw = str(raw)

    parsed = _extract_json(raw)
    if not parsed:
        return {"ok": False,
                "reason": "model did not return parseable JSON",
                "raw_preview": raw[:400]}

    # Sanitise
    one_line = (parsed.get("one_line") or "")[:220]
    key_points = [str(p)[:200] for p in (parsed.get("key_points") or [])][:8]
    picked_subjects = [str(s) for s in (parsed.get("identified_subjects") or [])]
    subjects_out = _valid_subjects(taxonomy, picked_subjects)
    concepts = [str(c)[:80] for c in (parsed.get("concepts") or [])][:16]

    # Rough token estimate (4 chars ≈ 1 token)
    tokens_in = max(1, (len(_SUMMARY_SYSTEM) + len(user_prompt)) // 4)
    tokens_out = max(1, len(raw) // 4)

    # Write to memory_bank for recall
    mb_body = (
        f"TRANSCRIPT SUMMARY · {doc.get('title')}\n"
        f"one line: {one_line}\n\n"
        f"key points:\n- " + "\n- ".join(key_points) + "\n\n"
        f"subjects: {', '.join(subjects_out) or '-'}\n"
        f"concepts: {', '.join(concepts) or '-'}"
    )
    subject_tags = [f"subject:{s}" for s in subjects_out]
    try:
        mb_row = await mb.auto_store(
            mb_body,
            persona=doc.get("agent", "minerva"),
            category="research",
            source_type="transcript_summary",
            source_id=transcript_id,
            tags=["transcript", "summary", doc.get("source", "other")] + subject_tags,
        )
        mb_id = (mb_row or {}).get("id")
    except Exception as exc:                    # noqa: BLE001
        logger.warning("MB write failed: %s", exc)
        mb_id = None

    # Write to knowledge_records (long-form)
    kr_id = uuid4().hex
    await _knowledge().insert_one({
        "id":              kr_id,
        "title":           (doc.get("title") or "")[:280],
        "summary":         one_line,
        "key_points":      key_points,
        "tags":            ["transcript", "summary"] + subject_tags,
        "source_type":     "transcript",
        "source_url":      doc.get("source_url"),
        "source_hash":     f"transcript:{transcript_id}",
        "concepts":        concepts,
        "confidence_score": 0.65,
        "related_agents":  [doc.get("agent", "minerva")],
        "memory_bank_id":  mb_id,
        "created_at":      _now(),
    })

    summary = TranscriptSummary(
        transcript_id=transcript_id,
        model=SUMMARY_MODEL,
        one_line=one_line,
        key_points=key_points,
        identified_subjects=subjects_out,
        concepts=concepts,
        tokens_in_estimated=tokens_in,
        tokens_out_estimated=tokens_out,
        knowledge_record_id=kr_id,
        memory_bank_id=mb_id,
    )
    summary_doc = summary.model_dump()
    await _summaries().insert_one(summary_doc.copy())
    await _transcripts().update_one(
        {"id": transcript_id}, {"$set": {"summary_id": summary.id}},
    )
    return {"ok": True, "summary": summary_doc}


async def get_summary(transcript_id: str) -> Optional[Dict[str, Any]]:
    """Return the newest summary for a transcript."""
    cur = _summaries().find(
        {"transcript_id": transcript_id}, {"_id": 0},
    ).sort("generated_at", -1).limit(1)
    async for d in cur:
        return d
    return None


async def stats() -> Dict[str, Any]:
    total = await _transcripts().count_documents({})
    summarised = await _summaries().count_documents({})
    by_source: Dict[str, int] = {}
    cur = _transcripts().aggregate([{"$group": {"_id": "$source", "n": {"$sum": 1}}}])
    async for r in cur:
        by_source[r["_id"] or "other"] = r["n"]
    return {
        "transcripts_total":     total,
        "summaries_total":       summarised,
        "unsummarised":          max(0, total - summarised),
        "by_source":             by_source,
    }
