"""ATLAS Research Lab routes.

Mission queue and discovery report API for Ajani, Hermes, Minerva, and Council.
This v1 is in-memory and deterministic; MongoDB persistence comes next.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import research_lab_engine as labs

router = APIRouter(prefix="/api/research-labs", tags=["ATLAS Research Labs"])


class CreateMissionRequest(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    owner_ai: str = Field(description="Ajani | Hermes | Minerva | Council")
    goal: str = Field(min_length=10, max_length=5000)
    source_ids: List[str] = Field(default_factory=list)
    subject_tags: List[str] = Field(default_factory=list)
    related_projects: List[str] = Field(default_factory=list)
    priority: str = Field(default="normal")
    council_review_required: bool = False


class UpdateMissionStatusRequest(BaseModel):
    status: str
    progress_percent: Optional[int] = Field(default=None, ge=0, le=100)


class CreateDiscoveryRequest(BaseModel):
    mission_id: str
    title: str = Field(min_length=3, max_length=300)
    summary_in_own_words: str = Field(min_length=10, max_length=8000)
    why_it_matters: str = Field(min_length=5, max_length=5000)
    evidence: List[str] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: int = Field(default=50, ge=0, le=100)
    risks_and_limits: List[str] = Field(default_factory=list)
    recommendation: str = Field(default="Council review recommended.")


class CouncilReviewRequest(BaseModel):
    decision: str = Field(description="approved | rejected | needs_more_evidence")
    notes: str = ""


@router.get("/health")
async def health():
    return {"status": "ok", "engine": "research_lab_engine", "labs": labs.labs()}


@router.get("/labs")
async def list_labs():
    return labs.labs()


@router.post("/missions")
async def create_mission(req: CreateMissionRequest):
    try:
        return labs.create_mission(**req.model_dump())
    except labs.ResearchLabError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/missions")
async def list_missions(
    owner_ai: Optional[str] = Query(None, description="Ajani | Hermes | Minerva | Council"),
    status: Optional[str] = None,
):
    try:
        items = labs.list_missions(owner_ai=owner_ai, status=status)
        return {"count": len(items), "items": items}
    except labs.ResearchLabError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/missions/{mission_id}")
async def get_mission(mission_id: str):
    mission = labs.get_mission(mission_id)
    if not mission:
        raise HTTPException(404, f"mission not found: {mission_id}")
    return mission


@router.patch("/missions/{mission_id}/status")
async def update_status(mission_id: str, req: UpdateMissionStatusRequest):
    try:
        return labs.update_mission_status(
            mission_id,
            status=req.status,
            progress_percent=req.progress_percent,
        )
    except labs.ResearchLabError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/discoveries")
async def create_discovery(req: CreateDiscoveryRequest):
    try:
        return labs.create_discovery(**req.model_dump())
    except labs.ResearchLabError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/discoveries")
async def list_discoveries(
    owner_ai: Optional[str] = Query(None, description="Ajani | Hermes | Minerva | Council"),
    mission_id: Optional[str] = None,
):
    try:
        items = labs.list_discoveries(owner_ai=owner_ai, mission_id=mission_id)
        return {"count": len(items), "items": items}
    except labs.ResearchLabError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.patch("/discoveries/{discovery_id}/council-review")
async def review_discovery(discovery_id: str, req: CouncilReviewRequest):
    try:
        return labs.council_review(discovery_id, decision=req.decision, notes=req.notes)
    except labs.ResearchLabError as exc:
        raise HTTPException(422, str(exc)) from exc
