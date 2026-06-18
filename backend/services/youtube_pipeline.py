"""
YouTube — Manual transcript ingestion + Channel-RSS resolution + Verification dashboard.

Why this is a separate module from `knowledge_watcher.py`:
  * `knowledge_watcher.py` handles GitHub-driven discovery (URL → KB).
  * This module handles YouTube-specific paths that don't depend on GitHub:
      - resolve a channel URL into its latest N video URLs
      - accept a USER-SUPPLIED transcript (sidesteps cloud-IP block) and
        run the full KB → MB → Graph → Lesson chain
      - return a verification dashboard for the entire YouTube subsystem

Strict rule: full transcript bodies are stored ONLY in the private
`youtube_transcripts_private` collection. The `knowledge_records` summary
field receives the LLM distillation only — never the raw transcript text.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

from models.knowledge_models import FetchedSource, SourceType, KnowledgeRecord, url_hash
from services import knowledge_distiller as kd
from services import memory_bank as mb
from services import knowledge_ingestion as ki
from services.lesson_generator import generate_lesson as _generate_lesson
from services.youtube_resolver import (
    latest_video_urls, parse_channel_form, ResolverError,
)

logger = logging.getLogger("atlas.youtube")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _yt_private(): return _db()["youtube_transcripts_private"]
def _records():    return _db()["knowledge_records"]
def _lessons():    return _db()["lessons"]
def _mb_col():     return _db()["memory_bank"]
def _triples():    return _db()["graph_triples"]


def _utc(): return datetime.now(timezone.utc).isoformat()


# --- 1. Channel RSS resolver wrapper (returns a verifiable bundle) ---------
async def resolve_channel(channel_url: str, *, n: int = 3) -> Dict[str, Any]:
    """Resolve a channel URL into its latest n videos and return the full
    bundle: channel_url, resolved_channel_id, channel_title, [video meta]."""
    form, ident = parse_channel_form(channel_url)
    videos = await latest_video_urls(channel_url, n=n)
    channel_id = videos[0]["channel_id"] if videos else None
    channel_title = videos[0]["channel_title"] if videos else None
    return {
        "channel_url": channel_url,
        "channel_url_form": form,            # channel_id | user | custom | handle
        "channel_identifier": ident,
        "resolved_channel_id": channel_id,
        "channel_title": channel_title,
        "videos": videos,
        "videos_returned": len(videos),
        "resolved_at": _utc(),
    }


# --- 2. Manual transcript ingestion -----------------------------------------
async def ingest_manual_transcript(
    *, video_url: str, transcript_text: str,
    video_title: Optional[str] = None,
    channel_name: Optional[str] = None,
    channel_url: Optional[str] = None,
    generate_lesson: bool = True,
    force_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    User-supplied transcript path. Sidesteps cloud-IP block by trusting the
    caller for the raw text. We:
      1. Save the FULL transcript to `youtube_transcripts_private` (mark
         consent=user_supplied). The transcript body never lands in
         knowledge_records or memory_bank — only the LLM distillation does.
      2. Build a FetchedSource and run the existing distill+persist chain.
      3. Optionally generate a lesson.
      4. Return all created IDs for verification.
    """
    if not video_url or not transcript_text or len(transcript_text.strip()) < 40:
        raise ValueError("video_url and transcript_text (≥40 chars) are required")

    # 1. Store full transcript privately
    tr_id = uuid4().hex
    transcript_doc = {
        "id": tr_id,
        "video_url": video_url,
        "video_title": video_title,
        "channel_name": channel_name,
        "channel_url": channel_url,
        "transcript_text": transcript_text,
        "transcript_length": len(transcript_text),
        "consent": "user_supplied",
        "created_at": _utc(),
    }
    await _yt_private().insert_one(transcript_doc)

    # 2. Build a FetchedSource and run distill + persistence
    fetched = FetchedSource(
        source_type=SourceType.YOUTUBE,
        source_url=video_url,
        title=video_title or f"YouTube · {video_url}",
        author=channel_name,
        text=transcript_text[:25_000],   # cap for distill prompt sanity
        extra={
            "transcript_source": "user_supplied",
            "transcript_private_id": tr_id,
            "channel_url": channel_url,
        },
    )
    distilled = await kd.distill(fetched, force_agent=force_agent)
    h = url_hash(fetched.source_url)
    existing = await _records().find_one({"source_hash": h}, {"_id": 0})

    extra_tags = ["youtube", "manual_transcript", "consent:user_supplied"]
    if channel_name:
        extra_tags.append(f"channel:{_slug(channel_name)}")

    if existing and existing.get("transcript_status") != "TRANSCRIPT_UNAVAILABLE":
        # True duplicate of a previously-distilled real ingest → reinforce
        result = await ki._reinforce(existing, distilled, fetched, extra_tags, None)
        record = result["record"]
        memory_bank_id = result["memory_bank_id"]
        reused = True
    else:
        # If there's a TRANSCRIPT_UNAVAILABLE stub for this URL → delete it
        # so we can replace with a real distillation. (Idempotent fresh path.)
        if existing:
            await _records().delete_one({"source_hash": h})
            if existing.get("memory_bank_id"):
                # leave the old MB row in place; it's audit history
                pass

        agent = distilled.suggested_agent
        category = "research"   # YouTube manual ingest → research bucket
        body = ki._compose_body(distilled, fetched)
        mb_row = await mb.auto_store(
            body, persona=agent, category=category,
            source_type="youtube",
            tags=list({*distilled.tags, *extra_tags, "knowledge"}),
        )
        memory_bank_id = (mb_row or {}).get("id")

        rec = KnowledgeRecord(
            title=distilled.title,
            summary=distilled.summary,
            key_points=distilled.key_points,
            tags=list({*distilled.tags, *extra_tags}),
            source_type=SourceType.YOUTUBE,
            source_url=video_url,
            source_hash=h,
            source_author=channel_name,
            confidence_score=distilled.confidence_score,
            related_agents=[agent],
            related_projects=[],
            concepts=distilled.concepts,
            memory_bank_id=memory_bank_id,
        )
        rec_dict = rec.model_dump()
        # Annotate the record as a real manual transcript (NOT a stub)
        rec_dict["transcript_status"] = "MANUAL_PROVIDED"
        rec_dict["transcript_private_id"] = tr_id
        rec_dict["channel_url"] = channel_url
        rec_dict["channel_name"] = channel_name
        await _records().insert_one(rec_dict)
        await ki._wire_graph(rec)
        record = ki._strip(rec_dict)
        reused = False

    # 3. Lesson + extra graph triples
    lesson_doc = None
    lesson_graph_edges_added = 0
    if generate_lesson:
        try:
            lesson_doc = await _generate_lesson(
                knowledge_id=record["id"],
                source_url=video_url,
                title=record["title"],
                concepts=record.get("concepts") or [],
                agent=record.get("related_agents", ["minerva"])[0],
            )
            # Wire lesson → knowledge → concept graph triples
            lesson_id = lesson_doc["id"]
            for concept in (record.get("concepts") or [])[:5]:
                await mb.add_triple(
                    from_node=f"lesson:{lesson_id[:8]}",
                    to_node=concept,
                    relation="teaches",
                    source_id=record["id"], weight=1.5,
                )
                lesson_graph_edges_added += 1
            if channel_name:
                await mb.add_triple(
                    from_node=f"channel:{_slug(channel_name)}",
                    to_node=record["title"][:80],
                    relation="published",
                    source_id=record["id"], weight=1.0,
                )
                lesson_graph_edges_added += 1
        except Exception as exc:    # noqa: BLE001
            logger.warning("lesson stage failed: %s", exc)

    return {
        "ok": True,
        "video_url": video_url,
        "transcript_private_id": tr_id,
        "knowledge_id": record["id"],
        "knowledge_reused": reused,
        "memory_bank_id": memory_bank_id,
        "concepts": record.get("concepts") or [],
        "tags": record.get("tags") or [],
        "agent": record.get("related_agents", [None])[0],
        "title": record["title"],
        "confidence_score": record.get("confidence_score"),
        "lesson_id": (lesson_doc or {}).get("id"),
        "lesson_title": (lesson_doc or {}).get("title"),
        "lesson_graph_edges_added": lesson_graph_edges_added,
    }


# --- 3. Verification dashboard ---------------------------------------------
async def dashboard() -> Dict[str, Any]:
    """Compute live YouTube subsystem state from Mongo. NO simulation."""
    # 3.a YouTube knowledge entries grouped by status
    yt_total = await _records().count_documents({"source_type": "youtube"})
    by_status: Dict[str, int] = {}
    async for d in _records().aggregate([
        {"$match": {"source_type": "youtube"}},
        {"$group": {"_id": "$transcript_status", "count": {"$sum": 1}}},
    ]):
        by_status[(d["_id"] or "UNKNOWN")] = d["count"]

    # 3.b Connected channels
    channels: Dict[str, Dict[str, Any]] = {}
    async for r in _records().find(
        {"source_type": "youtube"}, {"_id": 0,
         "source_url": 1, "channel_url": 1, "channel_name": 1,
         "transcript_status": 1, "id": 1, "title": 1, "concepts": 1},
    ):
        cu = r.get("channel_url") or r["source_url"]
        if cu not in channels:
            channels[cu] = {
                "channel_url": cu,
                "channel_name": r.get("channel_name"),
                "videos_ingested": 0,
                "transcripts_real": 0,
                "transcripts_unavailable": 0,
                "knowledge_ids": [],
                "concepts_seen": set(),
            }
        c = channels[cu]
        c["videos_ingested"] += 1
        if r.get("transcript_status") == "MANUAL_PROVIDED":
            c["transcripts_real"] += 1
        else:
            c["transcripts_unavailable"] += 1
        c["knowledge_ids"].append(r["id"])
        for cn in (r.get("concepts") or [])[:10]:
            c["concepts_seen"].add(cn)

    # Serialise sets
    channels_out = []
    for cu, c in channels.items():
        c["concepts_seen"] = sorted(c["concepts_seen"])[:15]
        channels_out.append(c)

    # 3.c YouTube-sourced lessons
    yt_knowledge_ids = [r["id"] for r in await _records().find(
        {"source_type": "youtube"}, {"_id": 0, "id": 1},
    ).to_list(length=500)]
    lesson_count = await _lessons().count_documents(
        {"source_knowledge_id": {"$in": yt_knowledge_ids}},
    )
    lessons = await _lessons().find(
        {"source_knowledge_id": {"$in": yt_knowledge_ids}}, {"_id": 0},
    ).to_list(length=50)

    # 3.d Memory bank linkage
    mb_youtube = await _mb_col().count_documents({"source_type": "youtube"})
    mb_manual = await _mb_col().count_documents(
        {"tags": {"$in": ["manual_transcript", "consent:user_supplied"]}},
    )

    # 3.e Graph edges touching anything YouTube
    graph_youtube_edges = await _triples().count_documents(
        {"$or": [
            {"source_id": {"$in": yt_knowledge_ids}},
            {"from_node": {"$regex": "^channel:|^lesson:", "$options": ""}},
        ]},
    )
    teaches_edges = await _triples().count_documents({"relation": "teaches"})

    # 3.f Private transcripts (full body storage, audit only)
    private_count = await _yt_private().count_documents({})

    # 3.g Verification verdict per ATLAS user rule
    verdict = "🔴 Not Verified"
    reasons: List[str] = []
    if by_status.get("MANUAL_PROVIDED", 0) >= 1 and lesson_count >= 1:
        verdict = "🟢 Verified end-to-end via manual transcript ingest"
    else:
        if by_status.get("MANUAL_PROVIDED", 0) == 0:
            reasons.append("no MANUAL_PROVIDED YouTube knowledge entries yet")
        if lesson_count == 0:
            reasons.append("no lessons sourced from YouTube knowledge entries yet")

    return {
        "verdict": verdict,
        "reasons_if_not_verified": reasons,
        "youtube_knowledge_total": yt_total,
        "youtube_knowledge_by_status": by_status,
        "connected_channels_count": len(channels_out),
        "connected_channels": channels_out,
        "lessons_from_youtube_count": lesson_count,
        "lessons_from_youtube": lessons,
        "memory_bank_youtube_rows": mb_youtube,
        "memory_bank_manual_transcript_rows": mb_manual,
        "graph_edges_youtube_related": graph_youtube_edges,
        "graph_teaches_edges_total": teaches_edges,
        "private_transcripts_stored": private_count,
        "generated_at": _utc(),
    }


# --- helpers ---------------------------------------------------------------
def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:48] or "x"
