"""ATLAS Knowledge Record Writer.

Creates approved Knowledge Bank records from reviewed discoveries. Records store
ATLAS's summary and citation metadata, not full copyrighted source content.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_RECORDS: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


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
    summary: str,
    owner_ai: str,
    source_refs: Optional[List[Dict[str, Any]]] = None,
    evidence_score: Optional[Dict[str, Any]] = None,
    related_subjects: Optional[List[str]] = None,
    related_projects: Optional[List[str]] = None,
    discovery_id: Optional[str] = None,
    council_decision: str = "approved",
) -> Dict[str, Any]:
    record_id = f"KR-{str(uuid4())[:8]}"
    record = {
        "knowledge_record_id": record_id,
        "title": title,
        "summary": summary,
        "owner_ai": owner_ai,
        "discovery_id": discovery_id,
        "source_refs": source_refs or [],
        "evidence_score": evidence_score or {},
        "related_subjects": related_subjects or [],
        "related_projects": related_projects or [],
        "council_decision": council_decision,
        "version": 1,
        "content_stored": "atlas_summary_only",
        "copyright_rule": "Stores ATLAS summary and citation metadata only; no full source copy.",
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _RECORDS[record_id] = record
    return record


def get_record(record_id: str) -> Optional[Dict[str, Any]]:
    return _RECORDS.get(record_id)


def list_records(owner_ai: Optional[str] = None, project_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    items = list(_RECORDS.values())
    if owner_ai:
        items = [item for item in items if item["owner_ai"].lower() == owner_ai.lower()]
    if project_id:
        items = [item for item in items if project_id in item.get("related_projects", [])]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)[:limit]


async def persist_record(record: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.knowledge_records.update_one({"knowledge_record_id": record["knowledge_record_id"]}, {"$set": record}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"knowledge_records": 0}
    records = await _DB.knowledge_records.find({}, {"_id": 0}).to_list(10000)
    _RECORDS.clear()
    for record in records:
        _RECORDS[record["knowledge_record_id"]] = record
    return {"knowledge_records": len(_RECORDS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.knowledge_records.create_index("knowledge_record_id", unique=True)
    await _DB.knowledge_records.create_index("owner_ai")
    await _DB.knowledge_records.create_index("related_projects")


def reset_in_memory_state() -> None:
    _RECORDS.clear()
