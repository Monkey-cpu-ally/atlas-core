"""ATLAS Research Lab Engine.

This service gives Ajani, Hermes, Minerva, and the Council a stable mission
queue model. It supports deterministic in-memory behavior for tests and optional
MongoDB persistence when the backend attaches a database on startup.

Next layer: connect approved discoveries to Knowledge Bank write-through and
World Knowledge source previews.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

VALID_AIS = {
    "Ajani": "Chief Engineer",
    "Hermes": "Chief Robotics & Design",
    "Minerva": "Chief Scientist",
    "Council": "Executive Board",
}

VALID_STATUSES = {"queued", "running", "blocked", "council_review", "completed", "archived"}
VALID_PRIORITIES = {"low", "normal", "high", "critical"}

_MISSIONS: Dict[str, Dict[str, Any]] = {}
_DISCOVERIES: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class ResearchLabError(RuntimeError):
    """Raised when a Research Lab request is invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_mongo_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = dict(doc)
    cleaned.pop("_id", None)
    return cleaned


def normalize_ai(owner_ai: str) -> str:
    for name in VALID_AIS:
        if name.lower() == owner_ai.lower():
            return name
    raise ResearchLabError(f"unknown owner_ai: {owner_ai}")


def labs() -> Dict[str, Any]:
    """Return the ATLAS research lab roster."""
    return {
        "labs": [
            {
                "ai": ai,
                "role": role,
                "queued": len([m for m in _MISSIONS.values() if m["owner_ai"] == ai and m["status"] == "queued"]),
                "running": len([m for m in _MISSIONS.values() if m["owner_ai"] == ai and m["status"] == "running"]),
                "completed": len([m for m in _MISSIONS.values() if m["owner_ai"] == ai and m["status"] == "completed"]),
            }
            for ai, role in VALID_AIS.items()
        ]
    }


def create_mission(
    *,
    title: str,
    owner_ai: str,
    goal: str,
    source_ids: Optional[List[str]] = None,
    subject_tags: Optional[List[str]] = None,
    related_projects: Optional[List[str]] = None,
    priority: str = "normal",
    council_review_required: bool = False,
) -> Dict[str, Any]:
    """Create a research mission for one ATLAS AI lab."""
    ai = normalize_ai(owner_ai)
    if priority not in VALID_PRIORITIES:
        raise ResearchLabError(f"invalid priority: {priority}")

    mission_id = f"{ai.upper()}-{str(uuid4())[:8]}"
    mission = {
        "mission_id": mission_id,
        "title": title,
        "owner_ai": ai,
        "owner_role": VALID_AIS[ai],
        "status": "queued",
        "priority": priority,
        "goal": goal,
        "source_ids": source_ids or [],
        "subject_tags": subject_tags or [],
        "related_projects": related_projects or [],
        "created_at": _utc_now(),
        "started_at": None,
        "completed_at": None,
        "progress_percent": 0,
        "knowledge_records_created": 0,
        "discoveries_created": 0,
        "council_review_required": council_review_required,
        "open_questions": [],
        "next_actions": [],
    }
    _MISSIONS[mission_id] = mission
    return mission


def list_missions(owner_ai: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List missions filtered by AI owner and/or status."""
    ai = normalize_ai(owner_ai) if owner_ai else None
    if status and status not in VALID_STATUSES:
        raise ResearchLabError(f"invalid status: {status}")

    missions = list(_MISSIONS.values())
    if ai:
        missions = [m for m in missions if m["owner_ai"] == ai]
    if status:
        missions = [m for m in missions if m["status"] == status]
    return sorted(missions, key=lambda m: m["created_at"], reverse=True)


def get_mission(mission_id: str) -> Optional[Dict[str, Any]]:
    return _MISSIONS.get(mission_id)


def update_mission_status(mission_id: str, status: str, progress_percent: Optional[int] = None) -> Dict[str, Any]:
    """Move a mission through the queue lifecycle."""
    if status not in VALID_STATUSES:
        raise ResearchLabError(f"invalid status: {status}")
    mission = get_mission(mission_id)
    if not mission:
        raise ResearchLabError(f"unknown mission_id: {mission_id}")

    mission["status"] = status
    if status == "running" and mission.get("started_at") is None:
        mission["started_at"] = _utc_now()
    if status == "completed":
        mission["completed_at"] = _utc_now()
        mission["progress_percent"] = 100
    if progress_percent is not None:
        mission["progress_percent"] = max(0, min(100, int(progress_percent)))
    return mission


def create_discovery(
    *,
    mission_id: str,
    title: str,
    summary_in_own_words: str,
    why_it_matters: str,
    evidence: Optional[List[str]] = None,
    citations: Optional[List[Dict[str, Any]]] = None,
    confidence_score: int = 50,
    risks_and_limits: Optional[List[str]] = None,
    recommendation: str = "Council review recommended.",
) -> Dict[str, Any]:
    """Create a discovery report from a mission."""
    mission = get_mission(mission_id)
    if not mission:
        raise ResearchLabError(f"unknown mission_id: {mission_id}")

    discovery_id = f"DISC-{str(uuid4())[:8]}"
    discovery = {
        "discovery_id": discovery_id,
        "mission_id": mission_id,
        "title": title,
        "owner_ai": mission["owner_ai"],
        "summary_in_own_words": summary_in_own_words,
        "why_it_matters": why_it_matters,
        "evidence": evidence or [],
        "source_ids": mission.get("source_ids", []),
        "citations": citations or [],
        "confidence_score": max(0, min(100, int(confidence_score))),
        "verification_status": "single_source" if citations else "unverified",
        "risks_and_limits": risks_and_limits or [],
        "related_projects": mission.get("related_projects", []),
        "recommendation": recommendation,
        "created_at": _utc_now(),
        "reviewed_by_council": False,
        "council_decision": "pending",
    }
    _DISCOVERIES[discovery_id] = discovery
    mission["discoveries_created"] += 1
    if mission.get("council_review_required"):
        mission["status"] = "council_review"
    return discovery


def list_discoveries(owner_ai: Optional[str] = None, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
    ai = normalize_ai(owner_ai) if owner_ai else None
    discoveries = list(_DISCOVERIES.values())
    if ai:
        discoveries = [d for d in discoveries if d["owner_ai"] == ai]
    if mission_id:
        discoveries = [d for d in discoveries if d["mission_id"] == mission_id]
    return sorted(discoveries, key=lambda d: d["created_at"], reverse=True)


def council_review(discovery_id: str, decision: str, notes: str = "") -> Dict[str, Any]:
    """Apply a Council decision to a discovery report."""
    if decision not in {"approved", "rejected", "needs_more_evidence"}:
        raise ResearchLabError("decision must be approved, rejected, or needs_more_evidence")
    discovery = _DISCOVERIES.get(discovery_id)
    if not discovery:
        raise ResearchLabError(f"unknown discovery_id: {discovery_id}")
    discovery["reviewed_by_council"] = True
    discovery["council_decision"] = decision
    discovery["council_notes"] = notes
    discovery["reviewed_at"] = _utc_now()
    if decision == "approved":
        discovery["verification_status"] = "council_verified"
    return discovery


def attach_mongo(db: Any) -> None:
    """Attach a MongoDB database for persistence.

    The in-memory API remains available for tests and local operation. When a
    DB is attached, async persistence helpers mirror data into MongoDB.
    """
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


async def hydrate_from_mongo() -> Dict[str, int]:
    """Load persisted missions and discoveries into the in-memory queues."""
    if _DB is None:
        return {"missions": 0, "discoveries": 0}

    missions = await _DB.research_lab_missions.find({}, {"_id": 0}).to_list(5000)
    discoveries = await _DB.research_lab_discoveries.find({}, {"_id": 0}).to_list(5000)

    _MISSIONS.clear()
    _DISCOVERIES.clear()
    for mission in missions:
        _MISSIONS[mission["mission_id"]] = _strip_mongo_id(mission)
    for discovery in discoveries:
        _DISCOVERIES[discovery["discovery_id"]] = _strip_mongo_id(discovery)
    return {"missions": len(_MISSIONS), "discoveries": len(_DISCOVERIES)}


async def persist_mission(mission: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.research_lab_missions.update_one(
        {"mission_id": mission["mission_id"]},
        {"$set": mission},
        upsert=True,
    )


async def persist_discovery(discovery: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.research_lab_discoveries.update_one(
        {"discovery_id": discovery["discovery_id"]},
        {"$set": discovery},
        upsert=True,
    )


async def persist_all() -> None:
    if _DB is None:
        return
    for mission in _MISSIONS.values():
        await persist_mission(mission)
    for discovery in _DISCOVERIES.values():
        await persist_discovery(discovery)


async def create_indexes() -> None:
    """Create MongoDB indexes for Research Lab lookups."""
    if _DB is None:
        return
    await _DB.research_lab_missions.create_index("mission_id", unique=True)
    await _DB.research_lab_missions.create_index([("owner_ai", 1), ("status", 1)])
    await _DB.research_lab_discoveries.create_index("discovery_id", unique=True)
    await _DB.research_lab_discoveries.create_index([("owner_ai", 1), ("mission_id", 1)])


def reset_in_memory_state() -> None:
    """Testing helper. Do not expose through production routes."""
    _MISSIONS.clear()
    _DISCOVERIES.clear()
