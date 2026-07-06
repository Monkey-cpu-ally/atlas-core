"""ATLAS Project Knowledge Linker routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import project_knowledge_linker as pkl

router = APIRouter(prefix="/api/project-knowledge", tags=["ATLAS Project Knowledge Linker"])


class ProjectProfileRequest(BaseModel):
    project_id: str = Field(min_length=3, max_length=180)
    name: str = Field(min_length=2, max_length=250)
    mission: str = Field(min_length=10, max_length=2500)
    domains: List[str] = Field(default_factory=list)
    lead_ai: str
    status: str = "research"
    required_capabilities: List[str] = Field(default_factory=list)
    safety_focus: List[str] = Field(default_factory=list)


class ProjectLinkRequest(BaseModel):
    project_id: str
    target_type: str
    target_id: str
    relationship_type: str = Field(min_length=2, max_length=120)
    rationale: str = Field(min_length=3, max_length=2000)
    confidence_score: int = Field(default=50, ge=0, le=100)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "project_knowledge_linker",
        "persistence_enabled": pkl.persistence_enabled(),
        "registered_projects": pkl.project_knowledge_summary()["project_count"],
    }


@router.post("/seed")
async def seed_project_profiles():
    result = pkl.seed_project_profiles()
    await pkl.persist_projects(result["items"])
    return {"created_or_updated": result["created_or_updated"], "summary": pkl.project_knowledge_summary()}


@router.get("/summary")
async def summary():
    return pkl.project_knowledge_summary()


@router.post("/projects")
async def create_project_profile(req: ProjectProfileRequest):
    try:
        profile = pkl.create_project_profile(**req.model_dump())
        await pkl.persist_projects([profile])
        return profile
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/projects")
async def list_project_profiles(lead_ai: Optional[str] = None, domain: Optional[str] = None, status: Optional[str] = None, limit: int = 250):
    items = pkl.list_project_profiles(lead_ai=lead_ai, domain=domain, status=status, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/projects/{project_id:path}")
async def get_project_profile(project_id: str):
    item = pkl.get_project_profile(project_id)
    if not item:
        raise HTTPException(404, f"project not found: {project_id}")
    return item


@router.get("/projects/{project_id:path}/brief")
async def project_brief(project_id: str):
    try:
        return pkl.build_project_brief(project_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/links")
async def create_project_link(req: ProjectLinkRequest):
    try:
        link = pkl.link_project_to_target(**req.model_dump())
        await pkl.persist_links([link])
        return link
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/links")
async def list_project_links(project_id: Optional[str] = None, target_type: Optional[str] = None, limit: int = 250):
    items = pkl.list_project_links(project_id=project_id, target_type=target_type, limit=limit)
    return {"count": len(items), "items": items}
