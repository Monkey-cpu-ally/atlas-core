"""
Multi-Agent API: REST endpoints for the orchestration system.

Provides:
- /agents/ask - Process a user request through the full pipeline
- /agents/plan - Get Ajani's plan without execution
- /agents/execute - Execute an approved plan
- /agents/memory/search - Search memory for past decisions
- /agents/status - Get system status
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from .orchestrator import AgentOrchestrator, ExecutionStatus
from ..memory.vector_store import DecisionMemory
from ..memory.decision_log import DecisionLog
from ..kernel.checkpoint import checkpoint_system, CheckpointType
from ..memory.decision_log import DecisionType
from ..memory.learning_loop import learning_loop
from ..memory.state_tracker import state_tracker


router = APIRouter(prefix="/agents", tags=["Multi-Agent System"])

orchestrator = AgentOrchestrator()
decision_memory = DecisionMemory()
decision_log = DecisionLog()


class AskRequest(BaseModel):
    request: str
    context: Optional[Dict[str, Any]] = None


class PlanRequest(BaseModel):
    request: str
    context: Optional[Dict[str, Any]] = None


class ExecuteRequest(BaseModel):
    task_id: str
    approve: bool = True


class MemorySearchRequest(BaseModel):
    query: str
    entry_type: Optional[str] = None
    limit: int = 10


@router.post("/ask")
async def ask(req: AskRequest):
    try:
        execution = await orchestrator.execute(req.request, req.context)
        
        if execution.status == ExecutionStatus.COMPLETE:
            decision_memory.store_summary(
                summary=f"Task completed: {req.request[:200]}",
                task_id=execution.task_id,
                agents_involved=[r.agent.value for r in execution.responses]
            )
        elif execution.status == ExecutionStatus.VETOED:
            decision_memory.store_lesson(
                lesson=f"Vetoed: {execution.veto_reason}",
                source_task=execution.task_id,
                failure_type="veto"
            )
        
        return {
            "success": execution.status == ExecutionStatus.COMPLETE,
            "task_id": execution.task_id,
            "status": execution.status.value,
            "responses": [r.to_dict() for r in execution.responses],
            "artifacts": execution.artifacts,
            "veto_reason": execution.veto_reason
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan")
async def plan(req: PlanRequest):
    try:
        from .ajani import AjaniAgent
        from ..kernel.task_router import TaskRouter
        
        router_instance = TaskRouter()
        classification = router_instance.classify(req.request)
        
        context = {
            "intent": classification.intent.value,
            "risk_level": classification.risk_level,
            "keywords": classification.keywords_matched,
            **(req.context or {})
        }
        
        ajani = AjaniAgent()
        response = await ajani.process(req.request, context, [])
        
        return {
            "classification": {
                "intent": classification.intent.value,
                "confidence": classification.confidence,
                "risk_level": classification.risk_level,
                "suggested_pipeline": router_instance.get_pipeline(classification)
            },
            "plan": response.to_dict(),
            "requires_approval": response.requires_approval
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution/{task_id}")
async def get_execution(task_id: str):
    execution = orchestrator.get_execution(task_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution.to_dict()


@router.post("/memory/search")
async def search_memory(req: MemorySearchRequest):
    results = decision_memory.search(
        query=req.query,
        entry_type=req.entry_type,
        limit=req.limit
    )
    
    return {
        "query": req.query,
        "results": [
            {
                "content": entry.content[:500],
                "type": entry.entry_type,
                "similarity": score,
                "agent": entry.agent_source,
                "task_id": entry.task_id
            }
            for entry, score in results
        ]
    }


@router.get("/memory/decisions")
async def get_decisions(task_id: Optional[str] = None, agent: Optional[str] = None):
    if task_id:
        decisions = decision_log.get_task_decisions(task_id)
    elif agent:
        decisions = decision_log.get_agent_decisions(agent)
    else:
        decisions = list(decision_log.decisions.values())
    
    return {
        "count": len(decisions),
        "decisions": [d.to_dict() for d in decisions[-50:]]
    }


@router.get("/memory/lessons")
async def get_lessons(context: Optional[str] = None, limit: int = 10):
    if context:
        lessons = decision_memory.recall_lessons(context, limit)
    else:
        entries = decision_memory.get_by_type("lesson")
        lessons = [
            {
                "lesson": e.content,
                "task_id": e.task_id,
                "similarity": 1.0
            }
            for e in entries[-limit:]
        ]
    
    return {
        "count": len(lessons),
        "lessons": lessons
    }


@router.get("/status")
async def get_status():
    return {
        "orchestrator": orchestrator.get_session_summary(),
        "memory": decision_memory.get_stats(),
        "decisions": decision_log.get_stats(),
        "learning": learning_loop.get_stats(),
        "project_state": state_tracker.get_full_state()
    }


@router.get("/agents")
async def list_agents():
    return {
        "agents": [
            {
                "name": "Ajani",
                "role": "Tactical Planner",
                "capabilities": ["plan", "research", "validate", "review"],
                "description": "First-responder. Breaks down tasks, assigns work, verifies results."
            },
            {
                "name": "Minerva",
                "role": "Ethics Guardian",
                "capabilities": ["review", "veto", "write", "design"],
                "description": "Gatekeeper with veto power. Reviews for safety, ethics, logic."
            },
            {
                "name": "Hermes",
                "role": "Builder & Executor",
                "capabilities": ["execute", "code", "validate"],
                "description": "Executes approved plans. Writes code, runs tools, logs results."
            }
        ],
        "pipeline": [
            "1. User request → Task Router (classify intent)",
            "2. Ajani → Plan & decompose",
            "3. Minerva → Review & approve/veto",
            "4. Hermes → Execute (if approved)",
            "5. Ajani → Verify results",
            "6. Memory → Store lessons learned"
        ]
    }


class CheckpointRequest(BaseModel):
    description: str
    task_id: Optional[str] = "manual"
    create_tag: bool = True


class RollbackRequest(BaseModel):
    target: str


@router.get("/checkpoints")
async def list_checkpoints(limit: int = 10):
    """List recent Git checkpoints."""
    return {
        "status": checkpoint_system.get_status(),
        "checkpoints": checkpoint_system.list_checkpoints(limit=limit)
    }


@router.post("/checkpoints")
async def create_checkpoint(request: CheckpointRequest):
    """Manually create a checkpoint."""
    checkpoint = checkpoint_system.create_checkpoint(
        task_id=request.task_id,
        description=request.description,
        checkpoint_type=CheckpointType.MANUAL,
        agent="user",
        create_tag=request.create_tag
    )
    
    if checkpoint:
        return {
            "success": True,
            "checkpoint": {
                "hash": checkpoint.commit_hash,
                "tag": checkpoint.tag,
                "description": checkpoint.description,
                "files_changed": checkpoint.files_changed,
                "timestamp": checkpoint.timestamp
            }
        }
    else:
        return {
            "success": False,
            "message": "No changes to checkpoint"
        }


@router.post("/checkpoints/rollback")
async def rollback_checkpoint(request: RollbackRequest):
    """Rollback to a previous checkpoint."""
    success, message = checkpoint_system.rollback_to_checkpoint(request.target)
    
    decision_log.log(
        decision_type=DecisionType.ROLLBACK,
        agent="user",
        task_id="rollback",
        description=f"Rollback to {request.target}: {'success' if success else 'failed'}",
        reasoning=message,
        confidence=1.0 if success else 0.0
    )
    
    return {
        "success": success,
        "message": message
    }
