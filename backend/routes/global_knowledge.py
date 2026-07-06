"""ATLAS Global Knowledge Network routes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import global_knowledge_network as gkn

router = APIRouter(prefix="/api/global-knowledge", tags=["ATLAS Global Knowledge Network"])


class InstitutionRequest(BaseModel):
    name: str = Field(min_length=2, max_length=250)
    country: str = Field(min_length=2, max_length=120)
    region: str
    organization_type: str
    primary_disciplines: List[str] = Field(default_factory=list)
    research_strengths: List[str] = Field(default_factory=list)
    trust_tier: str
    evidence_level: str
    primary_ai_owner: str
    website: Optional[str] = None
    open_data: bool = False
    related_atlas_projects: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "global_knowledge_network",
        "persistence_enabled": gkn.persistence_enabled(),
        "registered_institutions": gkn.global_summary()["institution_count"],
    }


@router.post("/seed")
async def seed_foundation_registry():
    result = gkn.seed_foundation_registry()
    await gkn.persist_all(result["items"])
    return {"created_or_updated": result["created_or_updated"], "summary": gkn.global_summary()}


@router.get("/summary")
async def summary():
    return gkn.global_summary()


@router.post("/institutions")
async def create_institution(req: InstitutionRequest):
    try:
        institution = gkn.create_institution(**req.model_dump())
        await gkn.persist_all([institution])
        return institution
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/institutions")
async def list_institutions(
    region: Optional[str] = None,
    country: Optional[str] = None,
    discipline: Optional[str] = None,
    owner: Optional[str] = None,
    trust_tier: Optional[str] = None,
    limit: int = 250,
):
    items = gkn.list_institutions(region=region, country=country, discipline=discipline, owner=owner, trust_tier=trust_tier, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/institutions/{institution_id}")
async def get_institution(institution_id: str):
    item = gkn.get_institution(institution_id)
    if not item:
        raise HTTPException(404, f"institution not found: {institution_id}")
    return item
