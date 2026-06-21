"""Unified Research Sources REST API — Knowledge Bank Phase C.

Mounted at `/api/research-sources/*` (read-only).
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from services import research_sources as rs_svc

router = APIRouter(prefix="/api/research-sources",
                   tags=["Knowledge Bank · Research Sources"])


@router.get("")
async def list_sources(
    kind: Optional[str] = Query(None, description="rss|patent|web|git|youtube_channel"),
    agent: Optional[str] = Query(None),
    enabled_only: bool = Query(True),
):
    items = await rs_svc.list_sources(kind=kind, agent=agent, enabled_only=enabled_only)
    return {"count": len(items), "items": items}


@router.get("/stats")
async def stats():
    return await rs_svc.stats()
