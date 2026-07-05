"""ATLAS Project Intelligence routes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import project_intelligence as projects

router = APIRouter(prefix="/api/project-intelligence", tags=["ATLAS Project Intelligence"])


class ProjectRequest(BaseModel):
    name: str = Field(min_length=2, max_length=240)
    purpose: str = Field(min_length=5, max_length=5000)
    owner_ai: str = "Council"
    status: str = "idea"
    subject_tags: List[str] = Field(default_factory=list)
    related_projects: List[str] = Field(default_factory=list)
    project_id: Optional[str] = None


class ProjectItemRequest(BaseModel):
    section: str
    item: Dict[str, Any] = Field(default_factory=dict)


class RiskRequest(BaseModel):
    title: str
    severity: str = "medium"
    mitigation: str = ""


class RecommendationRequest(BaseModel):
    title: str
    owner_ai: str
    rationale: str
    confidence_score: int = Field(default=50, ge=0, le=100)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "project_intelligence",
        "persistence_enabled": projects.persistence_enabled(),
        "projects": len(projects.list_projects()),
    }


@router.post("/projects")
async def create_project(req: ProjectRequest):
    try:
        project = projects.upsert_project(**req.model_dump())
        await projects.persist_project(project)
        return project
    except projects.ProjectIntelligenceError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/projects")
async def list_projects(owner_ai: Optional[str] = None, status: Optional[str] = None, tag: Optional[str] = None):
    items = projects.list_projects(owner_ai=owner_ai, status=status, tag=tag)
    return {"count": len(items), "items": items}


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = projects.get_project(project_id)
    if not project:
        raise HTTPException(404, f"project not found: {project_id}")
    return project


@router.get("/projects/{project_id}/brief")
async def project_brief(project_id: str):
    try:
        return projects.project_brief(project_id)
    except projects.ProjectIntelligenceError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/projects/{project_id}/items")
async def add_item(project_id: str, req: ProjectItemRequest):
    try:
        project = projects.add_project_item(project_id, req.section, req.item)
        await projects.persist_project(project)
        return project
    except projects.ProjectIntelligenceError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/projects/{project_id}/risks")
async def add_risk(project_id: str, req: RiskRequest):
    try:
        project = projects.add_risk(project_id, req.title, req.severity, req.mitigation)
        await projects.persist_project(project)
        return project
    except projects.ProjectIntelligenceError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/projects/{project_id}/recommendations")
async def add_recommendation(project_id: str, req: RecommendationRequest):
    try:
        project = projects.add_recommendation(
            project_id,
            title=req.title,
            owner_ai=req.owner_ai,
            rationale=req.rationale,
            confidence_score=req.confidence_score,
        )
        await projects.persist_project(project)
        return project
    except projects.ProjectIntelligenceError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/projects/{project_id}/cross-project-matches")
async def cross_project_matches(project_id: str):
    try:
        return projects.cross_project_matches(project_id)
    except projects.ProjectIntelligenceError as exc:
        raise HTTPException(404, str(exc)) from exc
