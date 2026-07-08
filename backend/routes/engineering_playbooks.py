"""ATLAS Engineering Playbook Engine routes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import engineering_playbooks

router = APIRouter(prefix="/api/engineering-playbooks", tags=["ATLAS Engineering Playbooks"])


class PlaybookRequest(BaseModel):
    title: str = Field(min_length=3, max_length=250)
    playbook_type: str
    owner_ai: str
    domains: List[str] = Field(default_factory=list)
    summary: str = Field(min_length=10, max_length=3000)
    related_project_ids: List[str] = Field(default_factory=list)
    related_technology_ids: List[str] = Field(default_factory=list)
    status: str = "draft"


class SectionRequest(BaseModel):
    section_type: str
    title: str = Field(min_length=3, max_length=250)
    content: str = Field(min_length=10, max_length=8000)
    evidence_level: str = "internal"
    confidence_score: int = Field(default=50, ge=0, le=100)


class ComponentRequest(BaseModel):
    name: str = Field(min_length=2, max_length=250)
    component_type: str
    function: str = Field(min_length=5, max_length=2000)
    key_specs: Dict[str, Any] = Field(default_factory=dict)
    risks: List[str] = Field(default_factory=list)


class MaterialRequest(BaseModel):
    name: str = Field(min_length=2, max_length=250)
    material_family: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    applications: List[str] = Field(default_factory=list)
    sustainability_notes: Optional[str] = None


class FailureRequest(BaseModel):
    title: str = Field(min_length=3, max_length=250)
    root_cause: str = Field(min_length=3, max_length=2000)
    severity: str
    corrective_action: str = Field(min_length=3, max_length=2000)
    preventive_action: str = Field(min_length=3, max_length=2000)
    evidence: Optional[str] = None


class PatternRequest(BaseModel):
    name: str = Field(min_length=3, max_length=250)
    pattern_type: str
    intent: str = Field(min_length=5, max_length=2000)
    structure: List[str] = Field(default_factory=list)
    tradeoffs: List[str] = Field(default_factory=list)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "engineering_playbooks",
        "persistence_enabled": engineering_playbooks.persistence_enabled(),
        "playbook_count": engineering_playbooks.playbook_summary()["playbook_count"],
    }


@router.post("/seed")
async def seed_foundation_playbooks():
    result = engineering_playbooks.seed_foundation_playbooks()
    await engineering_playbooks.persist_all()
    return {"created_or_updated": result["created_or_updated"], "summary": engineering_playbooks.playbook_summary()}


@router.get("/summary")
async def summary():
    return engineering_playbooks.playbook_summary()


@router.post("/playbooks")
async def create_playbook(req: PlaybookRequest):
    try:
        playbook = engineering_playbooks.create_playbook(**req.model_dump())
        await engineering_playbooks.persist_all()
        return playbook
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/playbooks")
async def list_playbooks(playbook_type: Optional[str] = None, owner_ai: Optional[str] = None, domain: Optional[str] = None, status: Optional[str] = None, project_id: Optional[str] = None, limit: int = 500):
    items = engineering_playbooks.list_playbooks(playbook_type=playbook_type, owner_ai=owner_ai, domain=domain, status=status, project_id=project_id, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/playbooks/{playbook_id}")
async def get_playbook(playbook_id: str):
    item = engineering_playbooks.get_playbook(playbook_id)
    if not item:
        raise HTTPException(404, f"playbook not found: {playbook_id}")
    return item


@router.get("/playbooks/{playbook_id}/detail")
async def playbook_detail(playbook_id: str):
    try:
        return engineering_playbooks.playbook_detail(playbook_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/playbooks/{playbook_id}/sections")
async def add_section(playbook_id: str, req: SectionRequest):
    try:
        section = engineering_playbooks.add_section(playbook_id=playbook_id, **req.model_dump())
        await engineering_playbooks.persist_all()
        return section
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/playbooks/{playbook_id}/components")
async def add_component(playbook_id: str, req: ComponentRequest):
    try:
        component = engineering_playbooks.add_component(playbook_id=playbook_id, **req.model_dump())
        await engineering_playbooks.persist_all()
        return component
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/playbooks/{playbook_id}/materials")
async def add_material(playbook_id: str, req: MaterialRequest):
    try:
        material = engineering_playbooks.add_material(playbook_id=playbook_id, **req.model_dump())
        await engineering_playbooks.persist_all()
        return material
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/playbooks/{playbook_id}/failures")
async def add_failure(playbook_id: str, req: FailureRequest):
    try:
        failure = engineering_playbooks.add_failure(playbook_id=playbook_id, **req.model_dump())
        await engineering_playbooks.persist_all()
        return failure
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/playbooks/{playbook_id}/patterns")
async def add_pattern(playbook_id: str, req: PatternRequest):
    try:
        pattern = engineering_playbooks.add_design_pattern(playbook_id=playbook_id, **req.model_dump())
        await engineering_playbooks.persist_all()
        return pattern
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
