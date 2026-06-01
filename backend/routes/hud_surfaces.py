"""
Memory + Manual + Settings routes — backing the MEMORY, MANUAL, and
CUSTOMIZATION HUD tiles.

These are intentionally small. atlas_events is already populated by other
routes (council, archive, teaching); we just expose a feed.
"""
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["HUD Surfaces"])

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client = AsyncIOMotorClient(MONGO_URL)
db = _client[DB_NAME]
events_col = db["atlas_events"]
settings_col = db["atlas_settings"]


# ---------------------------------------------------------------------------
# /api/memory/feed — live Atlas events
# ---------------------------------------------------------------------------
@router.get("/memory/feed")
async def memory_feed(limit: int = Query(40, ge=1, le=200)):
    cursor = events_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"count": len(rows), "events": rows}


# ---------------------------------------------------------------------------
# /api/manual/sections — static Atlas operator manual
# ---------------------------------------------------------------------------
MANUAL = [
    {
        "id": "hard-rules",
        "title": "Hard Rules",
        "body": (
            "1. **Ajani**: never an energy or kinetic system you cannot safely shut down.\n"
            "2. **Minerva**: no irreversible harm in the name of optimisation.\n"
            "3. **Hermes**: never design nanobots capable of self-replication.\n"
            "4. **Council**: cross-domain decisions require all three voices."
        ),
    },
    {
        "id": "personas",
        "title": "AI Personas",
        "body": (
            "**AJANI** · Builder · Strategist · Engineer — Zulu warrior cadence, "
            "answers in physics and structure.\n\n"
            "**MINERVA** · Wisdom Keeper · Reflector · Ethicist — Yoruba narrative, "
            "answers in living systems and human impact.\n\n"
            "**HERMES** · Pattern Hunter · Code · Systems — Maasai precision, "
            "answers in patterns, edge cases, data."
        ),
    },
    {
        "id": "rings",
        "title": "Ring Architecture",
        "body": (
            "**Inner ring** — the four AIs (Ajani · Minerva · Hermes · Council).\n\n"
            "**Middle ring** — system surfaces (Manual · Cyclopedia · Memory · Systems · Customization).\n\n"
            "**Outer ring** — operations (Subjects · Lab · Projects · Blueprints · Archive · Explore)."
        ),
    },
    {
        "id": "lab",
        "title": "Hands-on Lab",
        "body": (
            "Six labs live in the LAB tile: Power · Bridge · Code · Ecosystem · "
            "Nanoswarm · Resonance. Each failure mode maps to the lead persona's "
            "Hard Rule, so failing the design teaches the doctrine. AI Suggest "
            "calls Claude Sonnet 4.5 in the lead's voice for a single slider tweak."
        ),
    },
    {
        "id": "voice",
        "title": "Voice / Multi-language TTS",
        "body": (
            "Each AI has a native language: Ajani · isiZulu · Minerva · Yorùbá · "
            "Hermes · Maa. Toggle via the EN/ZU/YO/MAA picker in the chat header. "
            "If ElevenLabs is configured with `text_to_speech` scope, voices use "
            "ElevenLabs multilingual; otherwise OpenAI TTS fallback."
        ),
    },
]


@router.get("/manual/sections")
async def manual_sections():
    return {"count": len(MANUAL), "sections": MANUAL}


# ---------------------------------------------------------------------------
# /api/settings — TTS provider, default language, accent theme, etc.
# ---------------------------------------------------------------------------
class Settings(BaseModel):
    tts_provider: Optional[str] = Field(None, pattern="^(auto|openai|elevenlabs)$")
    default_language: Optional[str] = Field(None, pattern="^(en|zu|yo|maa)$")
    voice_enabled: Optional[bool] = None
    accent_theme: Optional[str] = Field(None, pattern="^(crimson|teal|silver|violet|auto)$")


SETTINGS_KEY = "user_settings_singleton"
DEFAULT_SETTINGS = {
    "tts_provider": "auto",
    "default_language": "en",
    "voice_enabled": True,
    "accent_theme": "auto",
}


@router.get("/settings")
async def get_settings():
    doc = await settings_col.find_one({"_id": SETTINGS_KEY}, {"_id": 0})
    if not doc:
        return DEFAULT_SETTINGS
    return {**DEFAULT_SETTINGS, **doc}


@router.put("/settings")
async def put_settings(s: Settings):
    patch = {k: v for k, v in s.model_dump().items() if v is not None}
    if not patch:
        raise HTTPException(400, "nothing to update")
    patch["updated_at"] = datetime.now(timezone.utc).isoformat()
    await settings_col.update_one(
        {"_id": SETTINGS_KEY},
        {"$set": patch},
        upsert=True,
    )
    doc = await settings_col.find_one({"_id": SETTINGS_KEY}, {"_id": 0})
    return {**DEFAULT_SETTINGS, **doc}
