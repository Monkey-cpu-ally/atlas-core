"""Subject taxonomy — Knowledge Bank Phase A.

A canonical, persisted list of 22 subjects ATLAS reasons over. Used by:
  - intake / worldwatch / youtube ingestion to tag content
  - memory_bank queries for subject-faceted recall
  - lesson generator for curriculum binding
  - HUD panels (Cyclopedia / Learning Hub) for browsing

Idempotent: `seed_if_needed()` only inserts subjects not already present
by name; existing rows are NEVER overwritten so any architect edits
persist across restarts.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

logger = logging.getLogger("atlas.subjects")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _coll():
    return _db()["subjects"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Subject(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    slug: str                                    # snake_case stable handle
    name: str
    description: str
    primary_agent: str                           # ajani | minerva | hermes | council
    family: str                                  # 'science' | 'engineering' | 'humanities' | 'craft' | 'meta'
    accent_color: str                            # HUD hex
    parent_tags: List[str] = Field(default_factory=list)
    enabled: bool = True
    created_at: str = Field(default_factory=_now)


# 22 canonical subjects — keep alphabetised so slugs stay stable.
SEED_SUBJECTS: List[Dict[str, Any]] = [
    {"slug": "aerospace_engineering",  "name": "Aerospace Engineering",
     "description": "Aircraft, spacecraft, propulsion, aerodynamics, GNC.",
     "primary_agent": "ajani",  "family": "engineering",  "accent_color": "#5AA9FF",
     "parent_tags": ["engineering", "physics"]},

    {"slug": "agriculture",  "name": "Agriculture & Agritech",
     "description": "Crops, soil chemistry, precision farming, drones, IoT.",
     "primary_agent": "ajani",  "family": "engineering",  "accent_color": "#7CD992",
     "parent_tags": ["biology", "engineering"]},

    {"slug": "architecture",  "name": "Architecture & Built Environment",
     "description": "Structural design, materials, urban planning.",
     "primary_agent": "ajani",  "family": "craft",  "accent_color": "#C8A268",
     "parent_tags": ["engineering", "design"]},

    {"slug": "artificial_intelligence",  "name": "Artificial Intelligence",
     "description": "Machine learning, deep learning, reasoning systems, agents.",
     "primary_agent": "minerva",  "family": "engineering",  "accent_color": "#C28BFF",
     "parent_tags": ["computer_science", "mathematics"]},

    {"slug": "biology",  "name": "Biology & Life Sciences",
     "description": "Cell biology, genetics, ecology, neuroscience.",
     "primary_agent": "minerva",  "family": "science",  "accent_color": "#3CBA86",
     "parent_tags": ["science"]},

    {"slug": "business",  "name": "Business & Operations",
     "description": "Strategy, finance, supply chain, lean ops.",
     "primary_agent": "hermes",  "family": "humanities",  "accent_color": "#FFB347",
     "parent_tags": ["humanities", "logic"]},

    {"slug": "chemistry",  "name": "Chemistry",
     "description": "Inorganic, organic, materials, electrochemistry.",
     "primary_agent": "minerva",  "family": "science",  "accent_color": "#FF7E7E",
     "parent_tags": ["science"]},

    {"slug": "computer_science",  "name": "Computer Science",
     "description": "Algorithms, systems, languages, distributed computing.",
     "primary_agent": "minerva",  "family": "engineering",  "accent_color": "#8F8FFF",
     "parent_tags": ["mathematics", "engineering"]},

    {"slug": "creative_writing",  "name": "Creative Writing",
     "description": "Storycraft, narrative architecture, prose.",
     "primary_agent": "hermes",  "family": "humanities",  "accent_color": "#E8B845",
     "parent_tags": ["humanities", "design"]},

    {"slug": "earth_climate",  "name": "Earth & Climate Sciences",
     "description": "Geology, atmosphere, oceans, climate models.",
     "primary_agent": "minerva",  "family": "science",  "accent_color": "#6BD3D3",
     "parent_tags": ["science"]},

    {"slug": "electrical_engineering",  "name": "Electrical & Electronics Engineering",
     "description": "Circuits, power electronics, embedded, RF.",
     "primary_agent": "ajani",  "family": "engineering",  "accent_color": "#FFD24A",
     "parent_tags": ["engineering", "physics"]},

    {"slug": "energy_systems",  "name": "Energy & Power Systems",
     "description": "Batteries, fuel cells, photovoltaics, grids.",
     "primary_agent": "ajani",  "family": "engineering",  "accent_color": "#FFC04A",
     "parent_tags": ["engineering", "chemistry", "physics"]},

    {"slug": "game_design",  "name": "Game & Interactive Design",
     "description": "Mechanics, level design, narrative systems, engines.",
     "primary_agent": "hermes",  "family": "craft",  "accent_color": "#FF6BCB",
     "parent_tags": ["design", "computer_science"]},

    {"slug": "history_philosophy",  "name": "History & Philosophy of Science",
     "description": "Epistemology, scientific revolutions, ethics of tech.",
     "primary_agent": "hermes",  "family": "humanities",  "accent_color": "#B79068",
     "parent_tags": ["humanities"]},

    {"slug": "mathematics",  "name": "Mathematics",
     "description": "Algebra, analysis, topology, statistics, discrete.",
     "primary_agent": "minerva",  "family": "science",  "accent_color": "#80E1D9",
     "parent_tags": ["science"]},

    {"slug": "materials_science",  "name": "Materials Science",
     "description": "Metallurgy, polymers, ceramics, composites, nanomaterials.",
     "primary_agent": "minerva",  "family": "engineering",  "accent_color": "#FF9F6B",
     "parent_tags": ["chemistry", "physics", "engineering"]},

    {"slug": "mechanical_engineering",  "name": "Mechanical Engineering",
     "description": "Machine design, manufacturing, fluid + thermal sys.",
     "primary_agent": "ajani",  "family": "engineering",  "accent_color": "#A8A8FF",
     "parent_tags": ["engineering", "physics"]},

    {"slug": "medicine_health",  "name": "Medicine & Health",
     "description": "Physiology, diagnostics, devices, public health.",
     "primary_agent": "minerva",  "family": "science",  "accent_color": "#FF8AB8",
     "parent_tags": ["biology"]},

    {"slug": "physics",  "name": "Physics",
     "description": "Classical, quantum, relativity, condensed matter, astro.",
     "primary_agent": "minerva",  "family": "science",  "accent_color": "#7AC8FF",
     "parent_tags": ["science"]},

    {"slug": "psychology_cognition",  "name": "Psychology & Cognition",
     "description": "Perception, learning, emotion, decision-making.",
     "primary_agent": "hermes",  "family": "humanities",  "accent_color": "#FFAE99",
     "parent_tags": ["humanities", "biology"]},

    {"slug": "robotics",  "name": "Robotics & Autonomous Systems",
     "description": "Manipulators, mobile robots, SLAM, control, HRI.",
     "primary_agent": "ajani",  "family": "engineering",  "accent_color": "#00FFC8",
     "parent_tags": ["engineering", "computer_science"]},

    {"slug": "sustainability",  "name": "Sustainability & Green Tech",
     "description": "Lifecycle, carbon capture, circular economy, eco-design.",
     "primary_agent": "minerva",  "family": "engineering",  "accent_color": "#A6F47A",
     "parent_tags": ["chemistry", "earth_climate", "engineering"]},
]


# --- Public surface --------------------------------------------------------
async def seed_if_needed() -> int:
    """Insert any seed subjects not already present (matched by `slug`)."""
    inserted = 0
    for spec in SEED_SUBJECTS:
        if await _coll().find_one({"slug": spec["slug"]}):
            continue
        await _coll().insert_one(Subject(**spec).model_dump())
        inserted += 1
    if inserted:
        logger.info("subjects seeded · %s new", inserted)
    return inserted


async def list_subjects(
    family: Optional[str] = None, enabled_only: bool = True,
) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if family:
        q["family"] = family
    if enabled_only:
        q["enabled"] = True
    cur = _coll().find(q, {"_id": 0}).sort("name", 1)
    return [d async for d in cur]


async def get_subject(slug_or_id: str) -> Optional[Dict[str, Any]]:
    doc = await _coll().find_one({"slug": slug_or_id}, {"_id": 0})
    if not doc:
        doc = await _coll().find_one({"id": slug_or_id}, {"_id": 0})
    return doc


async def upsert(subject: Subject) -> Dict[str, Any]:
    existing = await _coll().find_one({"slug": subject.slug})
    if existing:
        await _coll().update_one(
            {"_id": existing["_id"]},
            {"$set": {k: v for k, v in subject.model_dump().items()
                      if k not in ("id", "created_at")}},
        )
        return await _coll().find_one({"slug": subject.slug}, {"_id": 0})
    await _coll().insert_one(subject.model_dump().copy())
    return subject.model_dump()


async def stats() -> Dict[str, Any]:
    """Roll-up: how much content (memory_bank rows + knowledge_records +
    lessons) is currently tagged to each subject? Joins on `tags` field
    by the subject's slug."""
    all_subjects = await list_subjects()
    out: List[Dict[str, Any]] = []
    db = _db()
    for s in all_subjects:
        tag = f"subject:{s['slug']}"
        mb = await db["memory_bank"].count_documents({"tags": tag})
        kr = await db["knowledge_records"].count_documents({"tags": tag})
        ls = await db["lessons"].count_documents({"tags": tag})
        out.append({
            "subject_id": s["id"], "slug": s["slug"], "name": s["name"],
            "family": s["family"],
            "memory_bank_count": mb,
            "knowledge_records_count": kr,
            "lesson_count": ls,
            "total": mb + kr + ls,
        })
    out.sort(key=lambda r: r["total"], reverse=True)
    return {"count": len(out), "items": out}
