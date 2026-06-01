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
    concepts = lesson.get("key_concepts", [])[:5]
    return [
        {"question": f"What role does {c} play in this material?", "answer_type": "short_answer"}
        for c in concepts
    ]


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
        "lesson": lesson,
        "quiz": quiz,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return record


@router.post("/youtube")
async def intake_youtube(req: VideoIntake):
    transcript = _get_transcript(req.url)
    if not transcript:
        raise HTTPException(404, "transcript was empty")
    record = _intake_from_transcript(transcript, req.topic, req.url, req.persist)
    if req.persist:
        await archive_col.insert_one(record.copy())
    return {
        "topic": req.topic,
        "assigned_to": record["routed_to"],
        "matched_keyword": record["matched_keyword"],
        "display": record["display"],
        "lesson": record["lesson"],
        "quiz": record["quiz"],
        "archive_id": record["id"] if req.persist else None,
    }


@router.post("/transcript")
async def intake_transcript(req: TranscriptIntake):
    """Manual-paste fallback for environments where YouTube blocks the
    server IP (most cloud providers). Same downstream routing + lesson +
    quiz as /youtube; the architect just supplies the transcript."""
    record = _intake_from_transcript(req.transcript, req.topic, req.source_url, req.persist)
    if req.persist:
        await archive_col.insert_one(record.copy())
    return {
        "topic": req.topic,
        "assigned_to": record["routed_to"],
        "matched_keyword": record["matched_keyword"],
        "display": record["display"],
        "lesson": record["lesson"],
        "quiz": record["quiz"],
        "archive_id": record["id"] if req.persist else None,
    }


@router.get("/list")
async def list_intakes(limit: int = 20):
    cursor = archive_col.find({"kind": "youtube"}, {"_id": 0}).sort("created_at", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"count": len(rows), "items": rows}
