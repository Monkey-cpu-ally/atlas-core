"""ATLAS Technology Atlas routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import technology_atlas

router = APIRouter(prefix="/api/technology-atlas", tags=["ATLAS Technology Atlas"])


class TechnologyRequest(BaseModel):
    name: str = Field(min_length=2, max_length=250)
    category: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    disciplines: List[str] = Field(default_factory=list)
    primary_ai_owner: str
    maturity_level: str = "research"
    related_atlas_projects: List[str] = Field(default_factory=list)
    safety_considerations: List[str] = Field(default_factory=list)
    standards_needed: List[str] = Field(default_factory=list)


class RelationshipRequest(BaseModel):
    institution_id: str
    technology_id: str
    relationship_type: str = Field(min_length=2, max_length=120)
    evidence_note: str = Field(min_length=3, max_length=2000)
    confidence_score: int = Field(default=50, ge=0, le=100)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "technology_atlas",
        "persistence_enabled": technology_atlas.persistence_enabled(),
        "registered_technologies": technology_atlas.technology_summary()["technology_count"],
    }


@router.post("/seed")
async def seed_foundation_technologies():
    result = technology_atlas.seed_foundation_technologies()
    await technology_atlas.persist_technologies(result["items"])
    return {"created_or_updated": result["created_or_updated"], "summary": technology_atlas.technology_summary()}


@router.get("/summary")
async def summary():
    return technology_atlas.technology_summary()


@router.post("/technologies")
async def create_technology(req: TechnologyRequest):
    try:
        technology = technology_atlas.create_technology(**req.model_dump())
        await technology_atlas.persist_technologies([technology])
        return technology
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/technologies")
async def list_technologies(
    category: Optional[str] = None,
    discipline: Optional[str] = None,
    owner: Optional[str] = None,
    maturity_level: Optional[str] = None,
    project: Optional[str] = None,
    limit: int = 250,
):
    items = technology_atlas.list_technologies(
        category=category,
        discipline=discipline,
        owner=owner,
        maturity_level=maturity_level,
        project=project,
        limit=limit,
    )
    return {"count": len(items), "items": items}


@router.get("/technologies/{technology_id}")
async def get_technology(technology_id: str):
    item = technology_atlas.get_technology(technology_id)
    if not item:
        raise HTTPException(404, f"technology not found: {technology_id}")
    return item


@router.post("/relationships")
async def create_relationship(req: RelationshipRequest):
    try:
        relationship = technology_atlas.link_institution_to_technology(**req.model_dump())
        await technology_atlas.persist_relationships([relationship])
        return relationship
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/relationships")
async def list_relationships(technology_id: Optional[str] = None, institution_id: Optional[str] = None, limit: int = 250):
    items = technology_atlas.list_relationships(technology_id=technology_id, institution_id=institution_id, limit=limit)
    return {"count": len(items), "items": items}
