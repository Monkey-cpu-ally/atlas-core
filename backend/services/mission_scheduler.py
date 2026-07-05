"""ATLAS Mission Scheduler.

Routes user goals to Ajani, Hermes, Minerva, or Council and creates coordinated
Autonomous Knowledge missions. V1 is deterministic and safe: it does not run
background loops yet; it plans and queues work through existing engines.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services import autonomous_knowledge_engine as ake

_SCHEDULED: Dict[str, Dict[str, Any]] = {}
_DB: Any = None

ENGINEERING_TERMS = {
    "engineering", "manufacturing", "battery", "hydrogen", "engine", "aerospace",
    "vehicle", "architecture", "material", "materials", "energy", "power", "infrastructure",
}
ROBOTICS_TERMS = {
    "robot", "robotics", "weaver", "servo", "actuator", "cad", "sensor", "electronics",
    "automation", "blueprint", "design", "motor", "pcb", "drone",
}
SCIENCE_TERMS = {
    "biology", "plant", "plants", "medicine", "medical", "chemistry", "genetics",
    "crispr", "environment", "agriculture", "botany", "cell", "cells", "biomaterial",
}


class MissionSchedulerError(RuntimeError):
    """Raised when a scheduling request is invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def classify_goal(goal: str, subject_tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Classify a goal into an ATLAS AI owner."""
    text = f"{goal} {' '.join(subject_tags or [])}".lower()
    tokens = {token.strip(".,:;!?()[]{}") for token in text.split()}
    scores = {
        "Ajani": len(tokens.intersection(ENGINEERING_TERMS)),
        "Hermes": len(tokens.intersection(ROBOTICS_TERMS)),
        "Minerva": len(tokens.intersection(SCIENCE_TERMS)),
    }
    top_score = max(scores.values()) if scores else 0
    leaders = [ai for ai, score in scores.items() if score == top_score and score > 0]
    owner = leaders[0] if len(leaders) == 1 else "Council"
    if top_score == 0:
        owner = "Council"
    return {"owner_ai": owner, "scores": scores, "reason": "multi-domain" if owner == "Council" else "best subject match"}


def priority_from_goal(goal: str, requested_priority: str = "normal") -> str:
    if requested_priority in {"low", "normal", "high", "critical"}:
        return requested_priority
    text = goal.lower()
    if any(term in text for term in ["urgent", "emergency", "overheating", "failure", "danger"]):
        return "critical"
    if any(term in text for term in ["important", "prototype", "deadline"]):
        return "high"
    return "normal"


def schedule_mission(
    *,
    title: str,
    goal: str,
    subject_tags: Optional[List[str]] = None,
    related_projects: Optional[List[str]] = None,
    owner_ai: Optional[str] = None,
    priority: str = "normal",
    source_limit: int = 6,
) -> Dict[str, Any]:
    classification = classify_goal(goal, subject_tags)
    assigned_ai = owner_ai or classification["owner_ai"]
    chosen_priority = priority_from_goal(goal, priority)

    result = ake.create_knowledge_mission(
        title=title,
        goal=goal,
        owner_ai=assigned_ai,
        subject_tags=subject_tags or [],
        related_projects=related_projects or [],
        priority=chosen_priority,
        source_limit=source_limit,
        council_review_required=True,
    )

    schedule_id = f"SCH-{str(uuid4())[:8]}"
    record = {
        "schedule_id": schedule_id,
        "status": "queued",
        "title": title,
        "goal": goal,
        "assigned_ai": assigned_ai,
        "classification": classification,
        "priority": chosen_priority,
        "ake_job_id": result["job"]["job_id"],
        "mission_id": result["mission"]["mission_id"],
        "source_ids": result["job"].get("source_ids", []),
        "subject_tags": subject_tags or [],
        "related_projects": related_projects or [],
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _SCHEDULED[schedule_id] = record
    return {"scheduled": record, "knowledge_job": result["job"], "mission": result["mission"], "sources": result["sources"]}


def list_scheduled(owner_ai: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    items = list(_SCHEDULED.values())
    if owner_ai:
        items = [item for item in items if item["assigned_ai"].lower() == owner_ai.lower()]
    if status:
        items = [item for item in items if item["status"] == status]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)


def get_scheduled(schedule_id: str) -> Optional[Dict[str, Any]]:
    return _SCHEDULED.get(schedule_id)


async def persist_schedule(record: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.mission_schedules.update_one({"schedule_id": record["schedule_id"]}, {"$set": record}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"schedules": 0}
    records = await _DB.mission_schedules.find({}, {"_id": 0}).to_list(5000)
    _SCHEDULED.clear()
    for record in records:
        _SCHEDULED[record["schedule_id"]] = record
    return {"schedules": len(_SCHEDULED)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.mission_schedules.create_index("schedule_id", unique=True)
    await _DB.mission_schedules.create_index([("assigned_ai", 1), ("status", 1)])
    await _DB.mission_schedules.create_index("subject_tags")


def reset_in_memory_state() -> None:
    _SCHEDULED.clear()
