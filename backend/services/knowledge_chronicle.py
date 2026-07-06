"""ATLAS Knowledge Chronicle.

Versioned, reviewable knowledge records for the Global Knowledge Network.
V1 records claims, evidence metadata, confidence, review status, versions,
and contradiction flags without scraping external sources.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_RECORDS: Dict[str, Dict[str, Any]] = {}
_EVENTS: Dict[str, Dict[str, Any]] = {}

REVIEW_STATUSES = {"draft", "collected", "evidence_review", "engineering_review", "council_review", "approved", "rejected", "superseded", "needs_review"}
EVIDENCE_LEVELS = {"unknown", "community", "industry", "academic", "official", "standard", "peer_reviewed", "multi_source_verified"}
AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_record(
    *,
    title: str,
    claim: str,
    source_name: str,
    source_type: str,
    evidence_level: str,
    confidence_score: int,
    ai_owner: str,
    project_ids: Optional[List[str]] = None,
    technology_ids: Optional[List[str]] = None,
    institution_ids: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    review_status: str = "draft",
) -> Dict[str, Any]:
    if review_status not in REVIEW_STATUSES:
        raise ValueError(f"invalid review_status: {review_status}")
    if evidence_level not in EVIDENCE_LEVELS:
        raise ValueError(f"invalid evidence_level: {evidence_level}")
    if ai_owner not in AI_OWNERS:
        raise ValueError(f"invalid ai_owner: {ai_owner}")
    record_id = f"KREC-{str(uuid4())[:8]}"
    now = _utc_now()
    record = {
        "record_id": record_id,
        "title": title,
        "claim": claim,
        "source_name": source_name,
        "source_type": source_type,
        "evidence_level": evidence_level,
        "confidence_score": max(0, min(100, int(confidence_score))),
        "ai_owner": ai_owner,
        "project_ids": sorted(set(project_ids or [])),
        "technology_ids": sorted(set(technology_ids or [])),
        "institution_ids": sorted(set(institution_ids or [])),
        "tags": sorted(set(tags or [])),
        "review_status": review_status,
        "version": 1,
        "contradiction_status": "none",
        "created_at": now,
        "updated_at": now,
        "history": [
            {"version": 1, "event": "created", "timestamp": now, "note": "Initial knowledge record created."}
        ],
    }
    _RECORDS[record_id] = record
    _record_event(record_id=record_id, event_type="created", note="Knowledge record created.")
    return record


def get_record(record_id: str) -> Optional[Dict[str, Any]]:
    return _RECORDS.get(record_id)


def list_records(
    *,
    project_id: Optional[str] = None,
    technology_id: Optional[str] = None,
    institution_id: Optional[str] = None,
    ai_owner: Optional[str] = None,
    review_status: Optional[str] = None,
    evidence_level: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 250,
) -> List[Dict[str, Any]]:
    items = list(_RECORDS.values())
    if project_id:
        items = [item for item in items if project_id in item.get("project_ids", [])]
    if technology_id:
        items = [item for item in items if technology_id in item.get("technology_ids", [])]
    if institution_id:
        items = [item for item in items if institution_id in item.get("institution_ids", [])]
    if ai_owner:
        items = [item for item in items if item["ai_owner"].lower() == ai_owner.lower()]
    if review_status:
        items = [item for item in items if item["review_status"] == review_status]
    if evidence_level:
        items = [item for item in items if item["evidence_level"] == evidence_level]
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)[:limit]


def update_review_status(*, record_id: str, review_status: str, reviewer: str, note: str) -> Dict[str, Any]:
    record = _require_record(record_id)
    if review_status not in REVIEW_STATUSES:
        raise ValueError(f"invalid review_status: {review_status}")
    record["review_status"] = review_status
    record["updated_at"] = _utc_now()
    record["history"].append({"version": record["version"], "event": "review_status_changed", "timestamp": record["updated_at"], "reviewer": reviewer, "note": note, "status": review_status})
    _record_event(record_id=record_id, event_type="review_status_changed", note=note, actor=reviewer)
    return record


def revise_record(*, record_id: str, claim: str, note: str, reviewer: str, confidence_score: Optional[int] = None) -> Dict[str, Any]:
    record = _require_record(record_id)
    record["version"] += 1
    record["claim"] = claim
    if confidence_score is not None:
        record["confidence_score"] = max(0, min(100, int(confidence_score)))
    record["updated_at"] = _utc_now()
    record["history"].append({"version": record["version"], "event": "revised", "timestamp": record["updated_at"], "reviewer": reviewer, "note": note})
    _record_event(record_id=record_id, event_type="revised", note=note, actor=reviewer)
    return record


def flag_contradiction(*, record_id: str, conflicting_record_id: str, note: str, reviewer: str) -> Dict[str, Any]:
    record = _require_record(record_id)
    _require_record(conflicting_record_id)
    record["contradiction_status"] = "flagged"
    record.setdefault("conflicts", []).append({"conflicting_record_id": conflicting_record_id, "note": note, "reviewer": reviewer, "timestamp": _utc_now()})
    record["review_status"] = "needs_review"
    record["updated_at"] = _utc_now()
    record["history"].append({"version": record["version"], "event": "contradiction_flagged", "timestamp": record["updated_at"], "reviewer": reviewer, "note": note})
    _record_event(record_id=record_id, event_type="contradiction_flagged", note=note, actor=reviewer)
    return record


def chronicle_summary() -> Dict[str, Any]:
    by_status = {status: 0 for status in sorted(REVIEW_STATUSES)}
    by_evidence = {level: 0 for level in sorted(EVIDENCE_LEVELS)}
    by_ai = {owner: 0 for owner in sorted(AI_OWNERS)}
    contradiction_count = 0
    for record in _RECORDS.values():
        by_status[record["review_status"]] = by_status.get(record["review_status"], 0) + 1
        by_evidence[record["evidence_level"]] = by_evidence.get(record["evidence_level"], 0) + 1
        by_ai[record["ai_owner"]] = by_ai.get(record["ai_owner"], 0) + 1
        if record.get("contradiction_status") == "flagged":
            contradiction_count += 1
    return {
        "title": "ATLAS Knowledge Chronicle Summary",
        "generated_at": _utc_now(),
        "record_count": len(_RECORDS),
        "event_count": len(_EVENTS),
        "contradiction_count": contradiction_count,
        "review_statuses": by_status,
        "evidence_levels": by_evidence,
        "ai_owners": by_ai,
    }


def list_events(*, record_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_EVENTS.values())
    if record_id:
        items = [item for item in items if item["record_id"] == record_id]
    if event_type:
        items = [item for item in items if item["event_type"] == event_type]
    return sorted(items, key=lambda item: item["timestamp"], reverse=True)[:limit]


def seed_foundation_records() -> Dict[str, Any]:
    created = 0
    for seed in _foundation_seed_data():
        rec = create_record(**seed)
        if rec["record_id"]:
            created += 1
    return {"created_or_updated": created, "items": list_records(limit=1000)}


def reset_in_memory_state() -> None:
    _RECORDS.clear()
    _EVENTS.clear()


async def persist_records(items: List[Dict[str, Any]]) -> None:
    if _DB is None:
        return
    for item in items:
        await _DB.knowledge_chronicle_records.update_one({"record_id": item["record_id"]}, {"$set": item}, upsert=True)


async def persist_events(items: List[Dict[str, Any]]) -> None:
    if _DB is None:
        return
    for item in items:
        await _DB.knowledge_chronicle_events.update_one({"event_id": item["event_id"]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"knowledge_chronicle_records": 0, "knowledge_chronicle_events": 0}
    records = await _DB.knowledge_chronicle_records.find({}, {"_id": 0}).to_list(10000)
    events = await _DB.knowledge_chronicle_events.find({}, {"_id": 0}).to_list(10000)
    _RECORDS.clear(); _EVENTS.clear()
    for record in records:
        _RECORDS[record["record_id"]] = record
    for event in events:
        _EVENTS[event["event_id"]] = event
    return {"knowledge_chronicle_records": len(_RECORDS), "knowledge_chronicle_events": len(_EVENTS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.knowledge_chronicle_records.create_index("record_id", unique=True)
    await _DB.knowledge_chronicle_records.create_index("review_status")
    await _DB.knowledge_chronicle_records.create_index("ai_owner")
    await _DB.knowledge_chronicle_records.create_index("evidence_level")
    await _DB.knowledge_chronicle_events.create_index("event_id", unique=True)
    await _DB.knowledge_chronicle_events.create_index("record_id")
    await _DB.knowledge_chronicle_events.create_index("event_type")


def _require_record(record_id: str) -> Dict[str, Any]:
    record = _RECORDS.get(record_id)
    if not record:
        raise ValueError(f"unknown record_id: {record_id}")
    return record


def _record_event(*, record_id: str, event_type: str, note: str, actor: str = "system") -> Dict[str, Any]:
    event_id = f"KEVT-{str(uuid4())[:8]}"
    event = {"event_id": event_id, "record_id": record_id, "event_type": event_type, "note": note, "actor": actor, "timestamp": _utc_now()}
    _EVENTS[event_id] = event
    return event


def _foundation_seed_data() -> List[Dict[str, Any]]:
    return [
        {"title": "Official standards sources are highest priority", "claim": "ATLAS should treat recognized standards bodies and official agencies as high-trust sources while still tracking date, scope, and applicability.", "source_name": "ATLAS GKN Policy", "source_type": "internal_policy", "evidence_level": "official", "confidence_score": 90, "ai_owner": "Council", "project_ids": ["project:atlas"], "tags": ["source_quality", "standards"]},
        {"title": "Weaver requires robotics and manufacturing references", "claim": "The Weaver project should prioritize robotics, manufacturing, digital twin, materials, and safety references before prototype planning.", "source_name": "ATLAS Project Knowledge Linker", "source_type": "internal_registry", "evidence_level": "multi_source_verified", "confidence_score": 85, "ai_owner": "Hermes", "project_ids": ["project:weaver"], "tags": ["robotics", "manufacturing", "weaver"]},
        {"title": "Plant library needs ecological safety review", "claim": "Plant and restoration knowledge should include toxicity, invasive species risk, soil context, climate context, and ecological impact before use in ATLAS projects.", "source_name": "ATLAS Minerva Policy", "source_type": "internal_policy", "evidence_level": "official", "confidence_score": 88, "ai_owner": "Minerva", "project_ids": ["project:minerva_plant_library", "project:green_robotics"], "tags": ["botany", "safety", "ecology"]},
    ]
