"""
Personal Learning Adaptation + Visual Style Memory.

Two small companion services kept together because they share the same
"observation → preference" shape.

Learning profile (`user_learning_profile` collection, single document
with id="default"):
  - preferred_explanation_level: '6-9grade' | 'intermediate' | 'advanced'
  - hands_on_examples: bool
  - preferred_lesson_format: 'lego_steps' | 'qa' | 'reading' | 'video_summary'
  - favorite_project_types: [str]
  - preferred_visual_style: str
  - confusing_topics: [str]
  - successful_lesson_patterns: [{lesson_id, pattern}]
  - repeated_questions: [{q, count}]
  - coding_mistakes: [{kind, count}]

Visual style memory (`visual_style_memory` collection):
  - preferred_themes: [theme_id]
  - rejected_themes: [theme_id]
  - color_preferences: {accent, surface, etc.}
  - layout_preferences: {density, ring_motion, etc.}
  - animation_preferences: {snap_back, breathing, etc.}
  - reference_image_notes: [{note, ts}]
  - too_plain_warnings: int
  - too_messy_warnings: int

Both collections are single-document by default (id="default") so reads
are O(1). Multi-user support is a future P2 step.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("atlas.adaptation")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _learning(): return _db()["user_learning_profile"]
def _style():    return _db()["visual_style_memory"]


def _utc(): return datetime.now(timezone.utc).isoformat()


_DEFAULT_LEARNING = {
    "id": "default",
    "preferred_explanation_level": "6-9grade",  # the user's stated default
    "hands_on_examples": True,
    "preferred_lesson_format": "lego_steps",
    "favorite_project_types": [],
    "preferred_visual_style": "futuristic-holographic",
    "confusing_topics": [],
    "successful_lesson_patterns": [],
    "repeated_questions": [],
    "coding_mistakes": [],
    "explanation_rules": [
        "Explain hard topics at 6th-9th grade level first",
        "Then give the deeper advanced explanation",
        "Use hands-on Lego-style steps",
        "Include wrong/right examples",
        "Include mini quizzes",
        "Connect lessons to ATLAS projects",
    ],
    "updated_at": _utc(),
}


_DEFAULT_STYLE = {
    "id": "default",
    "preferred_themes": ["atlas_hud_v2"],
    "rejected_themes": [],
    "color_preferences": {
        "ajani": "#E63946",     # crimson
        "minerva": "#2EC4B6",   # teal
        "hermes": "#F4EFE4",    # white
        "council": "#9B6BD8",   # purple
    },
    "layout_preferences": {
        "density": "spacious",
        "ring_motion": "slow_with_snap_back",
        "panel_position": "right_dock",
    },
    "animation_preferences": {
        "snap_back": True,
        "breathing": True,
        "ring_idle_drift_seconds": 24,
    },
    "reference_image_notes": [],
    "too_plain_warnings": 0,
    "too_messy_warnings": 0,
    "updated_at": _utc(),
}


# --- Learning profile -----------------------------------------------------
async def get_learning_profile() -> Dict[str, Any]:
    doc = await _learning().find_one({"id": "default"}, {"_id": 0})
    if not doc:
        await _learning().insert_one(_DEFAULT_LEARNING.copy())
        doc = _DEFAULT_LEARNING.copy()
    return doc


async def update_learning_profile(patch: Dict[str, Any]) -> Dict[str, Any]:
    await get_learning_profile()        # ensure exists
    safe = {k: v for k, v in patch.items()
            if k in _DEFAULT_LEARNING and k != "id"}
    safe["updated_at"] = _utc()
    await _learning().update_one({"id": "default"}, {"$set": safe})
    return await get_learning_profile()


async def log_confusion(topic: str, *, weight: int = 1) -> Dict[str, Any]:
    doc = await get_learning_profile()
    confs = doc.get("confusing_topics") or []
    found = next((c for c in confs if c.get("topic") == topic), None)
    if found:
        found["count"] = (found.get("count") or 0) + weight
        found["last_seen"] = _utc()
    else:
        confs.append({"topic": topic, "count": weight, "last_seen": _utc()})
    await _learning().update_one(
        {"id": "default"},
        {"$set": {"confusing_topics": confs, "updated_at": _utc()}},
    )
    return await get_learning_profile()


async def log_successful_lesson(lesson_id: str, pattern: str) -> Dict[str, Any]:
    doc = await get_learning_profile()
    pats = doc.get("successful_lesson_patterns") or []
    pats.append({"lesson_id": lesson_id, "pattern": pattern, "ts": _utc()})
    await _learning().update_one(
        {"id": "default"},
        {"$set": {"successful_lesson_patterns": pats[-50:],
                  "updated_at": _utc()}},
    )
    return await get_learning_profile()


# --- Visual style memory --------------------------------------------------
async def get_visual_style() -> Dict[str, Any]:
    doc = await _style().find_one({"id": "default"}, {"_id": 0})
    if not doc:
        await _style().insert_one(_DEFAULT_STYLE.copy())
        doc = _DEFAULT_STYLE.copy()
    return doc


async def update_visual_style(patch: Dict[str, Any]) -> Dict[str, Any]:
    await get_visual_style()
    safe = {k: v for k, v in patch.items()
            if k in _DEFAULT_STYLE and k != "id"}
    safe["updated_at"] = _utc()
    await _style().update_one({"id": "default"}, {"$set": safe})
    return await get_visual_style()


async def add_style_note(note: str) -> Dict[str, Any]:
    doc = await get_visual_style()
    notes = doc.get("reference_image_notes") or []
    notes.append({"note": note, "ts": _utc()})
    await _style().update_one(
        {"id": "default"},
        {"$set": {"reference_image_notes": notes[-100:],
                  "updated_at": _utc()}},
    )
    return await get_visual_style()


async def increment_warning(kind: str) -> Dict[str, Any]:
    """kind ∈ {'too_plain', 'too_messy'}"""
    if kind not in {"too_plain", "too_messy"}:
        raise ValueError("kind must be 'too_plain' or 'too_messy'")
    field = f"{kind}_warnings"
    await get_visual_style()
    await _style().update_one(
        {"id": "default"},
        {"$inc": {field: 1}, "$set": {"updated_at": _utc()}},
    )
    return await get_visual_style()
