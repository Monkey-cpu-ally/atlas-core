"""ATLAS Autonomous Knowledge Engine routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import autonomous_knowledge_engine as ake

router = APIRouter(prefix="/api/autonomous-knowledge", tags=["ATLAS Autonomous Knowledge"])


class CreateKnowledgeMissionRequest(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    goal: str = Field(min_length=10, max_length=5000)
    owner_ai: str = Field(description="Ajani | Hermes | Minerva | Council")
    subject_tags: List[str] = Field(default_factory=list)
    related_projects: List[str] = Field(default_factory=list)
    priority: str = "normal"
    source_limit: int = Field(default=6, ge=1, le=20)
    council_review_required: bool = True


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "autonomous_knowledge_engine",
        "persistence_enabled": ake.persistence_enabled(),
        "jobs": len(ake.list_jobs()),
    }


@router.get("/sources/choose")
async def choose_sources(
    owner_ai: Optional[str] = None,
    subject: Optional[str] = Query(None, description="Single subject tag to match"),
    limit: int = Query(6, ge=1, le=20),
):
    try:
        items = ake.choose_sources(
            subject_tags=[subject] if subject else [],
            preferred_ai=owner_ai,
            limit=limit,
        )
        return {"count": len(items), "items": items}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(422, str(exc)) from exc


@router.post("/missions")
async def create_knowledge_mission(req: CreateKnowledgeMissionRequest):
    try:
        result = ake.create_knowledge_mission(**req.model_dump())
        await ake.persist_job(result["job"])
        # Research Lab mission persistence is handled here because this route created it.
        from services import research_lab_engine as labs
        await labs.persist_mission(result["mission"])
        return result
    except ake.AutonomousKnowledgeError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/jobs")
async def list_jobs(owner_ai: Optional[str] = None, status: Optional[str] = None):
    try:
        items = ake.list_jobs(owner_ai=owner_ai, status=status)
        return {"count": len(items), "items": items}
    except ake.AutonomousKnowledgeError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = ake.get_job(job_id)
    if not job:
        raise HTTPException(404, f"job not found: {job_id}")
    return job


@router.post("/jobs/{job_id}/draft-graph")
async def draft_graph(job_id: str):
    try:
        result = ake.draft_graph_from_mission(job_id)
        await ake.persist_job(result["job"])
        await ake.persist_all_graph(result)
        return result
    except ake.AutonomousKnowledgeError as exc:
        raise HTTPException(422, str(exc)) from exc
