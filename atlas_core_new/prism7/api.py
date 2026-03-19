"""
PRISM-7 API Router
Exposes the reasoning engine via FastAPI endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from .engine import PrismEngine, TaskPacket, new_id

router = APIRouter(prefix="/prism7", tags=["PRISM-7"])

engine = PrismEngine()


class PrismRequest(BaseModel):
    goal: str
    task_type: str = "general"
    constraints: List[str] = []
    urgency: str = "normal"
    emotional_context: str = "neutral"
    use_memory: bool = True


@router.get("/status")
def prism7_status():
    return {
        "engine": "PRISM-7",
        "version": "1.0",
        "pillars": ["origin", "shape", "current", "fracture", "drift", "echo", "paradox"],
        "status": "online",
    }


@router.post("/process")
def prism7_process(req: PrismRequest):
    """Run a goal through the full PRISM-7 pipeline and return structured results."""
    task = TaskPacket(
        id=new_id(),
        user_goal=req.goal,
        task_type=req.task_type,
        constraints=req.constraints,
        urgency=req.urgency,
        emotional_context=req.emotional_context,
        metadata={"use_memory": req.use_memory},
    )
    return engine.process_structured(task)


@router.post("/process/text")
def prism7_process_text(req: PrismRequest):
    """Run a goal through PRISM-7 and return plain-text output."""
    task = TaskPacket(
        id=new_id(),
        user_goal=req.goal,
        task_type=req.task_type,
        constraints=req.constraints,
        urgency=req.urgency,
        emotional_context=req.emotional_context,
        metadata={"use_memory": req.use_memory},
    )
    return {"output": engine.process(task)}
