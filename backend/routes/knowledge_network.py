"""ATLAS Knowledge Network routes.

Unified read/plan layer for the World Knowledge Network. These endpoints expose
registered sources and dry-run sync planning without breaking existing
research_sources, kbase, youtube, or memory routes.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import world_knowledge_connector as wkc

router = APIRouter(prefix="/api/knowledge-network", tags=["ATLAS Knowledge Network"])


@router.get("/health")
async def health():
    try:
        s = wkc.stats()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"Knowledge Network unavailable: {exc}") from exc
    return {"status": "ok", "engine": "world_knowledge_connector", "stats": s}


@router.get("/sources")
async def sources(
    ai_owner: Optional[str] = Query(None, description="Ajani | Hermes | Minerva | Council"),
    country: Optional[str] = None,
    region: Optional[str] = None,
    subject: Optional[str] = None,
    trust_tier: Optional[str] = None,
    auto_sync: Optional[bool] = None,
):
    items = wkc.list_sources(
        ai_owner=ai_owner,
        country=country,
        region=region,
        subject=subject,
        trust_tier=trust_tier,
        auto_sync=auto_sync,
    )
    return {"count": len(items), "items": items}


@router.get("/sources/{source_id}")
async def source_detail(source_id: str):
    source = wkc.get_source(source_id)
    if not source:
        raise HTTPException(404, f"source not found: {source_id}")
    return source


@router.get("/stats")
async def stats():
    return wkc.stats()


@router.get("/by-agent/{ai_owner}")
async def by_agent(ai_owner: str):
    items = wkc.list_sources(ai_owner=ai_owner)
    return {"ai_owner": ai_owner, "count": len(items), "items": items}


@router.get("/by-country/{country}")
async def by_country(country: str):
    items = wkc.list_sources(country=country)
    return {"country": country, "count": len(items), "items": items}


@router.get("/trust-levels")
async def trust_levels():
    return wkc.load_trust_levels()


class SyncPlanRequest(BaseModel):
    mission: Optional[str] = Field(
        None,
        description="Optional mission statement for this source sync plan.",
    )


@router.post("/sync/{source_id}/plan")
async def plan_sync(source_id: str, req: SyncPlanRequest | None = None):
    try:
        return wkc.plan_sync_job(source_id, mission=req.mission if req else None)
    except wkc.WorldKnowledgeError as exc:
        raise HTTPException(404, str(exc)) from exc


class KnowledgeRecordTemplateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    summary_in_own_words: str = Field(min_length=10, max_length=5000)


@router.post("/records/template/{source_id}")
async def knowledge_record_template(source_id: str, req: KnowledgeRecordTemplateRequest):
    try:
        return wkc.build_knowledge_record_template(
            source_id,
            title=req.title,
            summary=req.summary_in_own_words,
        )
    except wkc.WorldKnowledgeError as exc:
        raise HTTPException(404, str(exc)) from exc
