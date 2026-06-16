"""
External knowledge intake — YouTube transcripts → routed lesson + quiz.

Flow:
    1. Extract video ID from a YouTube URL
    2. Fetch the transcript (youtube_transcript_api)
    3. Route the topic via topic_router.route_topic → lead AI
    4. Build a styled lesson + quick quiz
    5. Persist into atlas_archive so the architect can revisit / teach
       this lesson again later from the Teaching engine.
"""
import logging
import os
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from youtube_transcript_api import YouTubeTranscriptApi

from routing.topic_router import AI_DISPLAY, route_topic
from routes.learning import persist_pipeline

logger = logging.getLogger("atlas.intake")

router = APIRouter(prefix="/api/intake", tags=["Intake"])

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client = AsyncIOMotorClient(MONGO_URL)
db = _client[DB_NAME]
archive_col = db["atlas_archive"]


# ---------------------------------------------------------------------------
# YouTube transcript fetch
# ---------------------------------------------------------------------------
def _extract_video_id(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if host in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        # /watch?v=ID  OR  /shorts/ID
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]
        vid = parse_qs(parsed.query).get("v", [None])[0]
        if not vid:
            raise ValueError("missing `v` query parameter")
        return vid
    if host == "youtu.be":
        return parsed.path.strip("/")
    raise ValueError("not a YouTube URL")


def _get_transcript(url: str) -> str:
    vid = _extract_video_id(url)
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(vid)
    except Exception as exc:
        msg = str(exc) or exc.__class__.__name__
        # YouTube blocks cloud-provider IPs. Surface a clean 503 so the UI
        # can offer the "paste transcript" fallback instead of a stack trace.
        if "IpBlocked" in msg or "blocking requests" in msg or "cloud provider" in msg:
            raise HTTPException(
                503,
                "YouTube is blocking requests from this server's IP. "
                "Paste the transcript manually using /api/intake/transcript.",
            ) from exc
        # Keep the first non-empty line so error responses are never blank.
        first = next((ln for ln in msg.splitlines() if ln.strip()), exc.__class__.__name__)
        raise HTTPException(502, f"transcript fetch failed: {first}") from exc
    # Each item exposes .text on v1.x
    return " ".join(getattr(item, "text", "") for item in fetched).strip()


# ---------------------------------------------------------------------------
# Lesson + quiz builders (pure functions)
# ---------------------------------------------------------------------------
KEYWORD_DICT = [
    "energy", "force", "cell", "dna", "robot", "code", "algorithm",
    "architecture", "physics", "biology", "engineering", "chemistry",
    "ecosystem", "nano", "swarm", "circuit", "neural", "data", "history",
    "culture", "wisdom", "resonance", "kinetic", "structure",
]


def _extract_keywords(text: str) -> list[str]:
    lower = text.lower()
    return [k for k in KEYWORD_DICT if k in lower]


LESSON_STYLE = {
    "ajani":   "Strategic, structured, blueprint-focused.",
    "minerva": "Reflective, nurturing, story-based.",
    "hermes":  "Technical, fast, code-and-systems focused.",
    "council": "Balanced multi-AI teaching mode.",
}


def _build_lesson(transcript: str, ai_owner: str) -> dict:
    # Take first ~120 words as a quick-read summary; richer summarisation
    # happens via the LLM teaching engine when the architect taps
    # "Teach this" — keeping intake fast/cheap.
    words = transcript.split()
    short_summary = " ".join(words[:160])
    return {
        "ai_owner": ai_owner,
        "summary": short_summary,
        "key_concepts": _extract_keywords(transcript),
        "lesson_style": LESSON_STYLE.get(ai_owner, LESSON_STYLE["council"]),
        "word_count": len(words),
    }


def _build_quiz(lesson: dict) -> list[dict]:
    """Generate up to 10 short-answer questions from the lesson's key
    concepts. Concept list is expanded by combining the original keyword
    detector with the lesson's transcript-derived nouns when available."""
    concepts = list(lesson.get("key_concepts", []))[:10]
    # Pad to 10 questions with generic but useful prompts.
    fillers = [
        "Explain the underlying mechanism in your own words.",
        "Where could this concept appear in everyday life?",
        "What is one common misconception about this topic?",
        "Describe a real-world experiment that could test this idea.",
        "Who benefits most when this knowledge spreads?",
    ]
    qs = [{"question": f"What role does {c} play in this material?", "answer_type": "short_answer"}
          for c in concepts]
    while len(qs) < 10:
        qs.append({"question": fillers[(len(qs) - len(concepts)) % len(fillers)], "answer_type": "short_answer"})
    return qs[:10]


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
class VideoIntake(BaseModel):
    url: str = Field(min_length=8)
    topic: str = Field(min_length=1, max_length=200)
    persist: bool = True


class TranscriptIntake(BaseModel):
    transcript: str = Field(min_length=20)
    topic: str = Field(min_length=1, max_length=200)
    source_url: Optional[str] = None     # for traceability
    persist: bool = True


def _intake_from_transcript(transcript: str, topic: str, source_url: Optional[str], persist: bool) -> dict:
    ai_id, kw = route_topic(topic)
    if ai_id == "council":
        ai_id, kw = route_topic(transcript[:600])
    lesson = _build_lesson(transcript, ai_id)
    quiz = _build_quiz(lesson)
    record = {
        "id": str(uuid4()),
        "kind": "youtube" if source_url else "transcript",
        "url": source_url,
        "topic": topic,
        "routed_to": ai_id,
        "matched_keyword": kw,
        "display": AI_DISPLAY[ai_id],
        "transcript_preview": transcript[:1200],
        "transcript_full": transcript,    # carried through to persist_pipeline
        "lesson": lesson,
        "quiz": quiz,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return record


async def _persist_full_pipeline(record: dict) -> dict:
    """Run the full Atlas pipeline (knowledge → lesson → project) and
    return the persisted IDs + generated artefacts."""
    return await persist_pipeline(
        topic=record["topic"],
        source=record.get("url") or "pasted-transcript",
        transcript=record.get("transcript_full") or record["transcript_preview"],
        summary=record["lesson"].get("summary", ""),
        persona=record["routed_to"],
        quiz=record["quiz"],
        title=record["topic"],
    )


@router.post("/youtube")
async def intake_youtube(req: VideoIntake):
    transcript = _get_transcript(req.url)
    if not transcript:
        raise HTTPException(404, "transcript was empty")
    record = _intake_from_transcript(transcript, req.topic, req.url, req.persist)
    pipeline = await _persist_full_pipeline(record) if req.persist else None
    if req.persist:
        # legacy `atlas_archive` row kept for the existing archive panel
        record_for_archive = {k: v for k, v in record.items() if k != "transcript_full"}
        await archive_col.insert_one(record_for_archive.copy())
    return {
        "topic": req.topic,
        "assigned_to": record["routed_to"],
        "matched_keyword": record["matched_keyword"],
        "display": record["display"],
        "lesson": record["lesson"],
        "quiz": record["quiz"],
        "archive_id": record["id"] if req.persist else None,
        "pipeline": pipeline,
    }


@router.post("/transcript")
async def intake_transcript(req: TranscriptIntake):
    """Manual-paste fallback for environments where YouTube blocks the
    server IP (most cloud providers). Same downstream routing + lesson +
    quiz as /youtube; the architect just supplies the transcript."""
    record = _intake_from_transcript(req.transcript, req.topic, req.source_url, req.persist)
    pipeline = await _persist_full_pipeline(record) if req.persist else None
    if req.persist:
        record_for_archive = {k: v for k, v in record.items() if k != "transcript_full"}
        await archive_col.insert_one(record_for_archive.copy())
    return {
        "topic": req.topic,
        "assigned_to": record["routed_to"],
        "matched_keyword": record["matched_keyword"],
        "display": record["display"],
        "lesson": record["lesson"],
        "quiz": record["quiz"],
        "archive_id": record["id"] if req.persist else None,
        "pipeline": pipeline,
    }


@router.get("/list")
async def list_intakes(limit: int = 20, kind: Optional[str] = None):
    """List intake entries. Defaults to all kinds; pass ?kind=youtube or
    ?kind=transcript to filter."""
    q = {"kind": kind} if kind else {"kind": {"$in": ["youtube", "transcript"]}}
    cursor = archive_col.find(q, {"_id": 0}).sort("created_at", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"count": len(rows), "items": rows}
