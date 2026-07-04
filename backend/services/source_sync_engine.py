"""ATLAS Source Sync Engine.

V1 performs safe source preview and discovery drafting for approved World
Knowledge sources. It does not store full copyrighted source content. It stores
metadata, AI-written summaries, citations, and traceable sync records.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services import world_knowledge_connector as registry
from services import world_knowledge_live as live
from services import research_lab_engine as labs

_SYNC_RUNS: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class SourceSyncError(RuntimeError):
    """Raised when a source sync cannot complete safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def _summary_from_preview(preview: Dict[str, Any]) -> str:
    title = preview.get("title") or preview.get("source_name") or "Untitled source"
    description = preview.get("description") or "No description was available from the metadata preview."
    headings = preview.get("headings") or []
    if headings:
        return f"{title}: {description} Notable public headings include: {', '.join(headings[:5])}."
    items = preview.get("items") or []
    if items:
        item_titles = [item.get("title") for item in items if item.get("title")]
        return f"{title}: latest feed preview includes {', '.join(item_titles[:5])}."
    return f"{title}: {description}"


async def sync_source_preview(
    *,
    source_id: str,
    mission_id: Optional[str] = None,
    create_discovery: bool = True,
    limit: int = 5,
) -> Dict[str, Any]:
    """Preview one approved source and optionally create a discovery draft."""
    source = registry.get_source(source_id)
    if not source:
        raise SourceSyncError(f"unknown source_id: {source_id}")

    run_id = f"SYNC-{str(uuid4())[:8]}"
    run = {
        "run_id": run_id,
        "source_id": source_id,
        "source_name": source.get("name"),
        "ai_owner": source.get("ai_owner"),
        "mission_id": mission_id,
        "status": "running",
        "started_at": _utc_now(),
        "completed_at": None,
        "preview": None,
        "discovery": None,
        "errors": [],
        "content_stored": False,
    }
    _SYNC_RUNS[run_id] = run

    try:
        preview = await live.preview_source(source_id, limit=limit)
        run["preview"] = preview
        if create_discovery and mission_id:
            mission = labs.get_mission(mission_id)
            if not mission:
                raise SourceSyncError(f"unknown mission_id: {mission_id}")
            summary = _summary_from_preview(preview)
            discovery = labs.create_discovery(
                mission_id=mission_id,
                title=f"Source preview: {source.get('name')}",
                summary_in_own_words=summary,
                why_it_matters="This source preview gives ATLAS a traceable starting point for deeper research and Council review.",
                evidence=["Metadata/snippet preview from approved source."],
                citations=[{"source_id": source_id, "url": source.get("url"), "title": source.get("name")}],
                confidence_score=int(source.get("trust_score") or 50),
                risks_and_limits=["This is metadata/snippet-level preview only, not a full paper or article analysis."],
                recommendation="Use this as a starting discovery draft, then verify with deeper source-specific connectors.",
            )
            run["discovery"] = discovery
        run["status"] = "completed"
    except Exception as exc:  # noqa: BLE001
        run["status"] = "failed"
        run["errors"].append(str(exc))
    finally:
        run["completed_at"] = _utc_now()
    return run


def list_sync_runs(source_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    runs = list(_SYNC_RUNS.values())
    if source_id:
        runs = [run for run in runs if run["source_id"] == source_id]
    if status:
        runs = [run for run in runs if run["status"] == status]
    return sorted(runs, key=lambda run: run["started_at"], reverse=True)


def get_sync_run(run_id: str) -> Optional[Dict[str, Any]]:
    return _SYNC_RUNS.get(run_id)


async def persist_run(run: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.source_sync_runs.update_one({"run_id": run["run_id"]}, {"$set": run}, upsert=True)
    if run.get("discovery"):
        await labs.persist_discovery(run["discovery"])
        mission = labs.get_mission(run["discovery"]["mission_id"])
        if mission:
            await labs.persist_mission(mission)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"sync_runs": 0}
    runs = await _DB.source_sync_runs.find({}, {"_id": 0}).to_list(5000)
    _SYNC_RUNS.clear()
    for run in runs:
        _SYNC_RUNS[run["run_id"]] = run
    return {"sync_runs": len(_SYNC_RUNS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.source_sync_runs.create_index("run_id", unique=True)
    await _DB.source_sync_runs.create_index([("source_id", 1), ("status", 1)])


def reset_in_memory_state() -> None:
    _SYNC_RUNS.clear()
