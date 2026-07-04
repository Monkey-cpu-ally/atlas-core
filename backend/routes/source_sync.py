"""ATLAS Source Sync routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import source_sync_engine as sync

router = APIRouter(prefix="/api/source-sync", tags=["ATLAS Source Sync"])


class SyncSourceRequest(BaseModel):
    mission_id: Optional[str] = None
    create_discovery: bool = True
    limit: int = Field(default=5, ge=1, le=20)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "source_sync_engine",
        "persistence_enabled": sync.persistence_enabled(),
        "runs": len(sync.list_sync_runs()),
    }


@router.post("/sources/{source_id}/preview")
async def sync_source(source_id: str, req: SyncSourceRequest):
    run = await sync.sync_source_preview(
        source_id=source_id,
        mission_id=req.mission_id,
        create_discovery=req.create_discovery,
        limit=req.limit,
    )
    await sync.persist_run(run)
    if run["status"] == "failed":
        raise HTTPException(422, run["errors"])
    return run


@router.get("/runs")
async def list_runs(source_id: Optional[str] = None, status: Optional[str] = Query(None)):
    items = sync.list_sync_runs(source_id=source_id, status=status)
    return {"count": len(items), "items": items}


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    run = sync.get_sync_run(run_id)
    if not run:
        raise HTTPException(404, f"sync run not found: {run_id}")
    return run
