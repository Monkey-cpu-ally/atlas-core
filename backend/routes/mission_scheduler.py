"""ATLAS Mission Scheduler routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import mission_scheduler as scheduler

router = APIRouter(prefix="/api/mission-scheduler", tags=["ATLAS Mission Scheduler"])


class ScheduleMissionRequest(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    goal: str = Field(min_length=10, max_length=5000)
    subject_tags: List[str] = Field(default_factory=list)
    related_projects: List[str] = Field(default_factory=list)
    owner_ai: Optional[str] = Field(default=None, description="Optional override: Ajani | Hermes | Minerva | Council")
    priority: str = "normal"
    source_limit: int = Field(default=6, ge=1, le=20)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "mission_scheduler",
        "persistence_enabled": scheduler.persistence_enabled(),
        "scheduled": len(scheduler.list_scheduled()),
    }


@router.post("/classify")
async def classify(req: ScheduleMissionRequest):
    return scheduler.classify_goal(req.goal, req.subject_tags)


@router.post("/schedule")
async def schedule(req: ScheduleMissionRequest):
    try:
        result = scheduler.schedule_mission(**req.model_dump())
        await scheduler.persist_schedule(result["scheduled"])
        from services import autonomous_knowledge_engine as ake
        from services import research_lab_engine as labs
        await ake.persist_job(result["knowledge_job"])
        await labs.persist_mission(result["mission"])
        return result
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(422, str(exc)) from exc


@router.get("/scheduled")
async def list_scheduled(owner_ai: Optional[str] = None, status: Optional[str] = None):
    items = scheduler.list_scheduled(owner_ai=owner_ai, status=status)
    return {"count": len(items), "items": items}


@router.get("/scheduled/{schedule_id}")
async def get_scheduled(schedule_id: str):
    item = scheduler.get_scheduled(schedule_id)
    if not item:
        raise HTTPException(404, f"schedule not found: {schedule_id}")
    return item
