"""Unified Knowledge Network layer.

A read-mostly aggregator that wraps five existing subsystems under a
single `/api/knowledge-network/*` namespace. Nothing is deleted — the
underlying routers (`/api/research-sources`, `/api/kbase`,
`/api/youtube`, `/api/subjects`, `/api/membank/research`) stay live so
the HUD keeps working.

New surface:
    GET   /api/knowledge-network/dashboard
    GET   /api/knowledge-network/sources                  (proxy + metadata)
    GET   /api/knowledge-network/sources/stats
    GET   /api/knowledge-network/sources/{source_id}
    PATCH /api/knowledge-network/sources/{source_id}/metadata
    GET   /api/knowledge-network/subjects
    GET   /api/knowledge-network/subjects/stats
    GET   /api/knowledge-network/youtube/dashboard
    GET   /api/knowledge-network/youtube/channels
    GET   /api/knowledge-network/kbase/search
    POST  /api/knowledge-network/kbase/ingest
    POST  /api/knowledge-network/research-memory   (alias of /api/membank/research)

Plus deep alias mounts (see `packet_aliases.mount_alias`) for every other
verb on the wrapped routers, so a client that only knows the packet
prefix has full parity with the originals.

Metadata fields exposed on every source row (new):
    country, region, source_type, trust_level, ai_owner,
    update_frequency, access_method, auto_sync, private_source
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

from services import research_sources as rs_svc

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


router = APIRouter(
    prefix="/api/knowledge-network",
    tags=["Knowledge Network"],
)


# ---------------------------------------------------------------------------
# Dashboard — aggregate counts across every wrapped subsystem.
# ---------------------------------------------------------------------------
@router.get("/dashboard")
async def dashboard() -> Dict[str, Any]:
    """One-shot overview of the whole knowledge network."""
    db = _db()
    source_stats = await rs_svc.stats()
    items = await rs_svc.list_sources(enabled_only=False)

    # Fan out metadata roll-ups so the HUD can render facet chips.
    by_country: Dict[str, int] = {}
    by_region: Dict[str, int] = {}
    by_trust: Dict[str, int] = {}
    by_ai_owner: Dict[str, int] = {}
    auto_sync_on = 0
    private_count = 0
    for row in items:
        c = row.get("country") or "unknown"
        r = row.get("region") or "unknown"
        t = row.get("trust_level") or "unverified"
        o = row.get("ai_owner") or "unassigned"
        by_country[c] = by_country.get(c, 0) + 1
        by_region[r] = by_region.get(r, 0) + 1
        by_trust[t] = by_trust.get(t, 0) + 1
        by_ai_owner[o] = by_ai_owner.get(o, 0) + 1
        if row.get("auto_sync"):
            auto_sync_on += 1
        if row.get("private_source"):
            private_count += 1

    counts = {
        "sources": source_stats.get("by_kind", {}),
        "subjects": await db["subjects"].count_documents({}),
        "youtube_channels": await db["youtube_channels"].count_documents({}),
        "knowledge_records": await db["knowledge_records"].count_documents({}),
        "research_memories": await db["memory_bank"].count_documents(
            {"category": "research"}
        ),
        "transcripts": await db["transcripts"].count_documents({}),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
        "sources_by_country": by_country,
        "sources_by_region": by_region,
        "sources_by_trust": by_trust,
        "sources_by_ai_owner": by_ai_owner,
        "auto_sync_enabled": auto_sync_on,
        "private_sources": private_count,
        "subsystems": {
            "research_sources": "/api/research-sources",
            "kbase":            "/api/kbase",
            "youtube":          "/api/youtube",
            "subjects":         "/api/subjects",
            "research_memory":  "/api/membank/research",
        },
    }


# ---------------------------------------------------------------------------
# Sources — proxy + extended metadata patch.
# ---------------------------------------------------------------------------
@router.get("/sources")
async def kn_list_sources(
    kind: Optional[str] = Query(None, description="rss|patent|web|git|youtube_channel"),
    agent: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    trust_level: Optional[str] = Query(None),
    auto_sync: Optional[bool] = Query(None),
    private_source: Optional[bool] = Query(None),
    enabled_only: bool = Query(True),
) -> Dict[str, Any]:
    items = await rs_svc.list_sources(kind=kind, agent=agent, enabled_only=enabled_only)
    if country is not None:
        items = [i for i in items if (i.get("country") or "") == country]
    if region is not None:
        items = [i for i in items if (i.get("region") or "") == region]
    if trust_level is not None:
        items = [i for i in items if (i.get("trust_level") or "") == trust_level]
    if auto_sync is not None:
        items = [i for i in items if bool(i.get("auto_sync")) == auto_sync]
    if private_source is not None:
        items = [i for i in items if bool(i.get("private_source")) == private_source]
    return {"count": len(items), "items": items}


@router.get("/sources/stats")
async def kn_source_stats() -> Dict[str, Any]:
    return await rs_svc.stats()


@router.get("/sources/{source_id}")
async def kn_get_source(source_id: str) -> Dict[str, Any]:
    row = await rs_svc.find_source(source_id)
    if not row:
        raise HTTPException(404, f"source '{source_id}' not found")
    return row


class SourceMetadataPatch(BaseModel):
    """Partial update — any subset of the 9 KN metadata fields."""
    country:          Optional[str]  = Field(default=None, max_length=80)
    region:           Optional[str]  = Field(default=None, max_length=80)
    source_type:      Optional[str]  = Field(default=None, max_length=80)
    trust_level:      Optional[str]  = Field(default=None, max_length=40)
    ai_owner:         Optional[str]  = Field(default=None, max_length=40)
    update_frequency: Optional[str]  = Field(default=None, max_length=40)
    access_method:    Optional[str]  = Field(default=None, max_length=40)
    auto_sync:        Optional[bool] = None
    private_source:   Optional[bool] = None


@router.patch("/sources/{source_id}/metadata")
async def kn_patch_source_metadata(
    source_id: str,
    patch: SourceMetadataPatch,
) -> Dict[str, Any]:
    payload = {k: v for k, v in patch.model_dump().items() if v is not None}
    if not payload:
        raise HTTPException(400, "no metadata fields supplied")
    updated = await rs_svc.update_source_metadata(source_id, payload)
    if not updated:
        raise HTTPException(404, f"source '{source_id}' not found")
    return updated


# ---------------------------------------------------------------------------
# Convenience proxies — thin wrappers so a client living entirely inside the
# /api/knowledge-network namespace can drive the wrapped subsystems without
# hard-coding the legacy prefixes. The bulk of the surface is provided via
# `mount_alias()` (see routes/packet_aliases.py::register_knowledge_network_aliases).
# ---------------------------------------------------------------------------
@router.get("/subjects")
async def kn_subjects_root() -> Dict[str, Any]:
    from routes.subjects import list_subjects  # type: ignore
    return await list_subjects()


@router.get("/youtube/dashboard")
async def kn_youtube_dashboard() -> Dict[str, Any]:
    from routes.youtube import dashboard as _yt_dashboard  # type: ignore
    return await _yt_dashboard()


class ResearchMemoryProxy(BaseModel):
    content: str = Field(min_length=1)
    persona: str = Field(default="hermes")
    source_id: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("/research-memory")
async def kn_store_research_memory(req: ResearchMemoryProxy) -> Dict[str, Any]:
    from routes.memory import store_research_memory, ResearchMemoryRequest  # type: ignore
    return await store_research_memory(ResearchMemoryRequest(**req.model_dump()))


# ---------------------------------------------------------------------------
# Health — quick liveness ping for the unified layer specifically.
# ---------------------------------------------------------------------------
@router.get("/health")
async def kn_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "layer": "knowledge-network",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "wraps": [
            "/api/research-sources",
            "/api/kbase",
            "/api/youtube",
            "/api/subjects",
            "/api/membank/research",
        ],
    }
