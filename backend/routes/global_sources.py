"""ATLAS Global Source Library routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import global_source_library as gsl
from services import source_reliability

router = APIRouter(prefix="/api/global-sources", tags=["ATLAS Global Source Library"])


class SourceRequest(BaseModel):
    name: str = Field(min_length=2, max_length=250)
    source_type: str
    trust_tier: str
    domains: List[str] = Field(default_factory=list)
    country: str = "International"
    region: str = "International"
    website: Optional[str] = None
    access_method: str = "website"
    owner_ai: str = "Council"
    ingestion_status: str = "candidate"
    notes: Optional[str] = None


class SourceReviewRequest(BaseModel):
    reviewer: str = Field(min_length=2, max_length=120)
    ingestion_status: str
    notes: str = Field(min_length=3, max_length=1500)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "global_source_library",
        "persistence_enabled": gsl.persistence_enabled(),
        "source_count": gsl.source_summary()["source_count"],
    }


@router.post("/seed")
async def seed_foundation_sources():
    result = gsl.seed_foundation_sources()
    await gsl.persist_all(result["items"])
    return {"created_or_updated": result["created_or_updated"], "summary": gsl.source_summary()}


@router.get("/summary")
async def summary():
    return gsl.source_summary()


@router.post("/sources")
async def register_source(req: SourceRequest):
    try:
        source = gsl.register_source(**req.model_dump())
        await gsl.persist_all([source])
        return source
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/sources")
async def list_sources(
    domain: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    trust_tier: Optional[str] = None,
    source_type: Optional[str] = None,
    owner_ai: Optional[str] = None,
    ingestion_status: Optional[str] = None,
    limit: int = 500,
):
    items = gsl.list_sources(
        domain=domain,
        country=country,
        region=region,
        trust_tier=trust_tier,
        source_type=source_type,
        owner_ai=owner_ai,
        ingestion_status=ingestion_status,
        limit=limit,
    )
    return {"count": len(items), "items": items}


@router.get("/sources/{source_id}")
async def get_source(source_id: str):
    item = gsl.get_source(source_id)
    if not item:
        raise HTTPException(404, f"source not found: {source_id}")
    return item


@router.post("/sources/{source_id}/review")
async def mark_reviewed(source_id: str, req: SourceReviewRequest):
    try:
        source = gsl.mark_reviewed(source_id=source_id, **req.model_dump())
        await gsl.persist_all([source])
        return source
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/sources/{source_id}/reliability")
async def source_reliability_report(source_id: str, domain: Optional[str] = None):
    source = gsl.get_source(source_id)
    if not source:
        raise HTTPException(404, f"source not found: {source_id}")
    return source_reliability.assess_source(source, domain=domain)


@router.get("/reliability-rankings")
async def reliability_rankings(
    domain: Optional[str] = None,
    minimum_score: int = 0,
    limit: int = 100,
):
    sources = gsl.list_sources(limit=10000)
    return source_reliability.rank_sources(
        sources,
        domain=domain,
        minimum_score=minimum_score,
        limit=limit,
    )
