"""ATLAS Chronicle Engine.

Records important ATLAS decisions as a traceable timeline. Chronicle entries are
not raw source storage; they are ATLAS's own audit trail of what changed, why,
and which systems were affected.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_ENTRIES: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_entry(
    *,
    title: str,
    event_type: str,
    summary: str,
    actor: str = "Council",
    related_ids: Optional[Dict[str, str]] = None,
    affected_systems: Optional[List[str]] = None,
) -> Dict[str, Any]:
    entry_id = f"CHR-{str(uuid4())[:8]}"
    entry = {
        "chronicle_id": entry_id,
        "title": title,
        "event_type": event_type,
        "summary": summary,
        "actor": actor,
        "related_ids": related_ids or {},
        "affected_systems": affected_systems or [],
        "created_at": _utc_now(),
    }
    _ENTRIES[entry_id] = entry
    return entry


def get_entry(chronicle_id: str) -> Optional[Dict[str, Any]]:
    return _ENTRIES.get(chronicle_id)


def list_entries(event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    items = list(_ENTRIES.values())
    if event_type:
        items = [item for item in items if item["event_type"] == event_type]
    return sorted(items, key=lambda item: item["created_at"], reverse=True)[:limit]


async def persist_entry(entry: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.chronicle_entries.update_one({"chronicle_id": entry["chronicle_id"]}, {"$set": entry}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"chronicle_entries": 0}
    entries = await _DB.chronicle_entries.find({}, {"_id": 0}).to_list(10000)
    _ENTRIES.clear()
    for entry in entries:
        _ENTRIES[entry["chronicle_id"]] = entry
    return {"chronicle_entries": len(_ENTRIES)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.chronicle_entries.create_index("chronicle_id", unique=True)
    await _DB.chronicle_entries.create_index("event_type")
    await _DB.chronicle_entries.create_index("created_at")


def reset_in_memory_state() -> None:
    _ENTRIES.clear()
