"""
Autonomous Research Orchestrator routes (prefix /api/research-orch).

Lives at a separate prefix from the older /api/research/{web,pdf,patent}
routes (which are the manual research pipeline). The orchestrator is the
*autonomous* layer on top of the existing primitives.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import research_orchestrator as ro
from services import blueprint_forge as bf
from services import lesson_generator as lg

router = APIRouter(prefix="/api/research-orch", tags=["ResearchOrchestrator"])


@router.get("/queue/status")
async def queue_status():
    return await ro.queue_status()


@router.get("/queue")
async def queue_list(
    state: Optional[str] = None,
    domain: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    items = await ro.queue_list(state=state, domain=domain, limit=limit)
    return {"count": len(items), "items": items}


class CycleReq(BaseModel):
    discover_per_feed: int = Field(1, ge=1, le=5)
    max_investigate: int = Field(5, ge=1, le=25)
    generate_lessons: bool = True
    mode: str = "lego"
    forge_blueprints: bool = False


@router.post("/orchestrator/run")
async def orchestrator_run(req: Optional[CycleReq] = None):
    p = req or CycleReq()
    return await ro.run_cycle(
        discover_per_feed=p.discover_per_feed,
        max_investigate=p.max_investigate,
        generate_lessons=p.generate_lessons,
        mode=p.mode,
        forge_blueprints=p.forge_blueprints,
    )


@router.post("/curiosity/scan")
async def curiosity_scan():
    return await ro.curiosity_scan()


@router.post("/projects/evaluate")
async def projects_evaluate():
    """Project Improvement Loop. Reads `projects_queue` + recent linked
    queue items + asks Council whether each project should be updated."""
    return await ro.evaluate_projects()


@router.get("/projects")
async def projects_list(limit: int = Query(50, ge=1, le=200)):
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    cli = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    db = cli[os.environ.get("DB_NAME", "test_database")]
    items = await db["projects_queue"].find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=limit)
    return {"count": len(items), "items": items}


@router.get("/project-recommendations")
async def project_recommendations(limit: int = Query(50, ge=1, le=200)):
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    cli = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    db = cli[os.environ.get("DB_NAME", "test_database")]
    items = await db["project_recommendations"].find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=limit)
    return {"count": len(items), "items": items}


@router.get("/missions")
async def missions_list(status: Optional[str] = "open"):
    items = await ro.list_missions(status=status)
    return {"count": len(items), "items": items}


class ForgeReq(BaseModel):
    queue_item_id: str


@router.post("/blueprint-forge/run")
async def blueprint_forge_run(req: ForgeReq):
    res = await bf.forge_from_queue(req.queue_item_id)
    if not res.get("ok"):
        raise HTTPException(400, res.get("error", "forge failed"))
    return res


@router.get("/blueprints")
async def blueprints_list(limit: int = Query(50, ge=1, le=200)):
    items = await bf.list_blueprints(limit=limit)
    return {"count": len(items), "items": items}


class LessonModeReq(BaseModel):
    knowledge_id: str
    mode: str = "lego"   # default | adhd | lego | beginner | professional | certification


@router.post("/lesson/regenerate")
async def lesson_regenerate(req: LessonModeReq):
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    cli = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    db = cli[os.environ.get("DB_NAME", "test_database")]
    kb = await db["knowledge_records"].find_one({"id": req.knowledge_id}, {"_id": 0})
    if not kb:
        raise HTTPException(404, "knowledge_id not found")
    lesson = await lg.generate_lesson(
        knowledge_id=kb["id"],
        source_url=kb.get("source_url") or "",
        title=kb.get("title") or "",
        concepts=kb.get("concepts") or [],
        agent=(kb.get("related_agents") or ["minerva"])[0],
        mode=req.mode,
    )
    return lesson
