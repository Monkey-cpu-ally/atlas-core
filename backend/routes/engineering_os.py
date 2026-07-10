"""ATLAS Engineering Operating System routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from routes.atlas_os import router as atlas_os_router
from services import engineering_operating_system as aeos

router = APIRouter(prefix="/api/engineering-os", tags=["ATLAS Engineering OS"])


class MissionRequest(BaseModel):
    title: str = Field(min_length=3, max_length=250)
    project_id: str = Field(min_length=3, max_length=180)
    objective: str = Field(min_length=10, max_length=3000)
    lead_ai: str
    council_members: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    status: str = "planned"
    workflow_phase: str = "idea"
    constraints: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


class AdvanceMissionRequest(BaseModel):
    workflow_phase: str
    note: str = Field(min_length=3, max_length=1000)
    actor: str = "system"


class TaskRequest(BaseModel):
    mission_id: str
    title: str = Field(min_length=3, max_length=250)
    owner_ai: str
    phase: str
    priority: str = "medium"
    status: str = "todo"
    evidence_required: bool = True


class TaskStatusRequest(BaseModel):
    status: str
    note: str = Field(min_length=3, max_length=1000)
    actor: str = "system"


class RiskRequest(BaseModel):
    mission_id: str
    title: str = Field(min_length=3, max_length=250)
    severity: str = "medium"
    mitigation: str = Field(min_length=3, max_length=1000)
    owner_ai: str
    status: str = "open"


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "engineering_operating_system",
        "persistence_enabled": aeos.persistence_enabled(),
        "mission_count": aeos.dashboard_summary()["mission_count"],
    }


@router.post("/seed")
async def seed_foundation_missions():
    result = aeos.seed_foundation_missions()
    await aeos.persist_all()
    return {"created_or_updated": result["created_or_updated"], "summary": aeos.dashboard_summary()}


@router.get("/dashboard")
async def dashboard():
    return aeos.dashboard_summary()


@router.post("/missions")
async def create_mission(req: MissionRequest):
    try:
        mission = aeos.create_mission(**req.model_dump())
        await aeos.persist_all()
        return mission
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/missions")
async def list_missions(
    project_id: Optional[str] = None,
    lead_ai: Optional[str] = None,
    status: Optional[str] = None,
    phase: Optional[str] = None,
    limit: int = 250,
):
    items = aeos.list_missions(project_id=project_id, lead_ai=lead_ai, status=status, phase=phase, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/missions/{mission_id}")
async def get_mission(mission_id: str):
    item = aeos.get_mission(mission_id)
    if not item:
        raise HTTPException(404, f"mission not found: {mission_id}")
    return item


@router.post("/missions/{mission_id}/advance")
async def advance_mission(mission_id: str, req: AdvanceMissionRequest):
    try:
        mission = aeos.advance_mission(mission_id=mission_id, **req.model_dump())
        await aeos.persist_all()
        return mission
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/tasks")
async def create_task(req: TaskRequest):
    try:
        task = aeos.create_task(**req.model_dump())
        await aeos.persist_all()
        return task
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/tasks")
async def list_tasks(mission_id: Optional[str] = None, status: Optional[str] = None, owner_ai: Optional[str] = None, limit: int = 250):
    items = aeos.list_tasks(mission_id=mission_id, status=status, owner_ai=owner_ai, limit=limit)
    return {"count": len(items), "items": items}


@router.post("/tasks/{task_id}/status")
async def update_task_status(task_id: str, req: TaskStatusRequest):
    try:
        task = aeos.update_task_status(task_id=task_id, **req.model_dump())
        await aeos.persist_all()
        return task
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/risks")
async def create_risk(req: RiskRequest):
    try:
        risk = aeos.create_risk(**req.model_dump())
        await aeos.persist_all()
        return risk
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/risks")
async def list_risks(mission_id: Optional[str] = None, status: Optional[str] = None, limit: int = 250):
    items = aeos.list_risks(mission_id=mission_id, status=status, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/events")
async def list_events(mission_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 250):
    items = aeos.list_events(mission_id=mission_id, event_type=event_type, limit=limit)
    return {"count": len(items), "items": items}


router.include_router(atlas_os_router)
