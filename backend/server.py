from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from routes.files import router as files_router
from routes.chat import router as chat_router
from routes.knowledge import router as knowledge_router
from routes.ai_services import router as ai_services_router
from routes.sandbox import router as sandbox_router
from routes.council import router as council_router
from routes.hud_surfaces import router as hud_surfaces_router
from routes.intake import router as intake_router
from routes.learning import router as learning_router
from routes.llm import router as llm_router
from routes.memory import router as memory_router
from routes.research import router as research_router
from routes.twins import router as twins_router
from routes.weaver import router as weaver_router
from routes.kbase import router as kbase_router
from routes.robot import router as robot_router
from routes.persona import router as persona_router
from routes.watchers import router as watchers_router, kbase_helper_router
from routes.lessons import router as lessons_router
from routes.self_improve import router as self_improve_router
from routes.youtube import router as youtube_router
from routes.atlas_v2 import router as atlas_v2_router
from routes.research_orchestrator import router as research_orch_router
from routes.knowledge_network import router as knowledge_network_router
from routes.research_labs import router as research_labs_router
from routes.knowledge_graph import router as knowledge_graph_router
from routes.autonomous_knowledge import router as autonomous_knowledge_router
from routes.source_sync import router as source_sync_router
from routes.mission_scheduler import router as mission_scheduler_router
from routes.project_intelligence import router as project_intelligence_router
from routes.external_access import router as external_access_router
from routes.discovery_approval import router as discovery_approval_router
from routes.discovery_engine import router as discovery_engine_router
from routes.headquarters import router as headquarters_router
from routes.system_inspector import router as system_inspector_router
from routes.global_knowledge import router as global_knowledge_router
from routes.technology_atlas import router as technology_atlas_router
from routes.project_knowledge import router as project_knowledge_router
from routes.knowledge_chronicle import router as knowledge_chronicle_router
from routes.engineering_os import router as engineering_os_router
from routes.global_sources import router as global_sources_router
from routes.world_knowledge_graph import router as world_knowledge_graph_router
from routes.engineering_playbooks import router as engineering_playbooks_router
from routes.campus import router as campus_router
from routes.executive_dashboard import router as executive_dashboard_router
from routes.creative_studio import router as creative_studio_router
from atlas_core import atlas_router as atlas_core_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')
mongo_url = os.environ['MONGO_URL']; client = AsyncIOMotorClient(mongo_url); db = client[os.environ['DB_NAME']]
app = FastAPI(); api_router = APIRouter(prefix="/api")
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore"); id: str = Field(default_factory=lambda: str(uuid.uuid4())); client_name: str; timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
class StatusCheckCreate(BaseModel): client_name: str
@api_router.get("/")
async def root(): return {"message":"Hello World"}
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj=StatusCheck(**input.model_dump()); doc=status_obj.model_dump(); doc['timestamp']=doc['timestamp'].isoformat(); await db.status_checks.insert_one(doc); return status_obj
@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks=await db.status_checks.find({}, {"_id":0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'],str): check['timestamp']=datetime.fromisoformat(check['timestamp'])
    return status_checks
app.include_router(api_router)
for _router in [files_router,chat_router,knowledge_router,ai_services_router,sandbox_router,council_router,hud_surfaces_router,intake_router,learning_router,llm_router,memory_router,research_router,twins_router,weaver_router,kbase_router,robot_router,persona_router,watchers_router,kbase_helper_router,lessons_router,self_improve_router,youtube_router,atlas_v2_router,research_orch_router,knowledge_network_router,research_labs_router,knowledge_graph_router,autonomous_knowledge_router,source_sync_router,mission_scheduler_router,project_intelligence_router,external_access_router,discovery_approval_router,discovery_engine_router,headquarters_router,system_inspector_router,global_knowledge_router,technology_atlas_router,project_knowledge_router,knowledge_chronicle_router,engineering_os_router,global_sources_router,world_knowledge_graph_router,engineering_playbooks_router,campus_router,executive_dashboard_router,creative_studio_router]: app.include_router(_router)
from routes.environments import router as environments_router
from routes.nir import router as nir_router
from routes.subjects import router as subjects_router
from routes.research_sources import router as research_sources_router
app.include_router(environments_router); app.include_router(nir_router); app.include_router(subjects_router); app.include_router(research_sources_router); app.include_router(atlas_core_router,prefix="/api")
EXPORTS_DIR=Path("/app/exports")
@app.get("/api/exports/atlas-ai-architecture.zip")
async def download_architecture_zip():
    path=EXPORTS_DIR/"atlas-ai-architecture.zip"
    if not path.exists():
        from fastapi import HTTPException; raise HTTPException(404,"architecture zip not yet built")
    return FileResponse(path=str(path),filename="atlas-ai-architecture.zip",media_type="application/zip")
@app.get("/api/exports/atlas-hud-architecture.zip")
async def download_hud_zip():
    path=EXPORTS_DIR/"atlas-hud-architecture.zip"
    if not path.exists():
        from fastapi import HTTPException; raise HTTPException(404,"HUD architecture zip not yet built")
    return FileResponse(path=str(path),filename="atlas-hud-architecture.zip",media_type="application/zip")
@app.get("/api/exports/README.md")
async def download_readme():
    path=EXPORTS_DIR/"README.md"
    if not path.exists():
        from fastapi import HTTPException; raise HTTPException(404,"readme not found")
    return FileResponse(path=str(path),filename="atlas-architecture-README.md",media_type="text/markdown")
@app.get("/api/exports/README-HUD.md")
async def download_hud_readme():
    path=EXPORTS_DIR/"README-HUD.md"
    if not path.exists():
        from fastapi import HTTPException; raise HTTPException(404,"readme not found")
    return FileResponse(path=str(path),filename="atlas-hud-README.md",media_type="text/markdown")
from atlas_core.memory.memory import attach_mongo_on_startup as _atlas_attach_mongo
@app.on_event("startup")
async def _wire_atlas_memory(): await _atlas_attach_mongo()
@app.on_event("startup")
async def _seed_runtime_catalogs():
    from services import environments as e,nir as n,reference_twins as r,robot as rb,subjects as s
    for name,seed in [("subjects",s.seed_if_needed),("environments",e.seed_if_needed),("NIR library",n.seed_library_if_needed),("reference twins",r.seed_if_needed),("robot devices",rb.seed_if_needed)]:
        try: logging.getLogger(__name__).info("Runtime seed %s: %s",name,await seed())
        except Exception as exc: logging.getLogger(__name__).error("Runtime seed %s failed: %s",name,exc)
@app.on_event("startup")
async def _wire_research_labs():
    try:
        from services import research_lab_engine as x; x.attach_mongo(db); await x.create_indexes(); counts=await x.hydrate_from_mongo(); logging.getLogger(__name__).info("Research Labs hydrated: %s missions · %s discoveries",counts["missions"],counts["discoveries"])
    except Exception as exc: logging.getLogger(__name__).warning("Research Lab persistence skipped: %s",exc)
@app.on_event("startup")
async def _wire_discovery_engine():
    try:
        from services import discovery_approval_pipeline as a, discovery_engine as d, invention_ledger as l
        d.attach_mongo(db); a.attach_mongo(db); l.attach_mongo(db)
        await d.create_indexes(); await a.create_indexes(); await l.create_indexes()
        dc=await d.hydrate_from_mongo(); ac=await a.hydrate_from_mongo(); lc=await l.hydrate_from_mongo()
        logging.getLogger(__name__).info("Discovery Engine hydrated: %s investigations · %s approval drafts · %s invention ledgers",dc["investigations"],ac["discovery_drafts"],lc["ledgers"])
    except Exception as exc: logging.getLogger(__name__).warning("Discovery Engine persistence skipped: %s",exc)
@app.on_event("startup")
async def _wire_knowledge_graph():
    try:
        from services import knowledge_graph_engine as x; x.attach_mongo(db); await x.create_indexes(); counts=await x.hydrate_from_mongo(); logging.getLogger(__name__).info("Knowledge Graph hydrated: %s nodes · %s edges",counts["nodes"],counts["edges"])
    except Exception as exc: logging.getLogger(__name__).warning("Knowledge Graph persistence skipped: %s",exc)
@app.on_event("startup")
async def _wire_autonomous_knowledge():
    try:
        from services import autonomous_knowledge_engine as x; x.attach_mongo(db); await x.create_indexes(); counts=await x.hydrate_from_mongo(); logging.getLogger(__name__).info("Autonomous Knowledge hydrated: %s jobs",counts["jobs"])
    except Exception as exc: logging.getLogger(__name__).warning("Autonomous Knowledge persistence skipped: %s",exc)
@app.on_event("startup")
async def _wire_source_sync():
    try:
        from services import source_sync_engine as x; x.attach_mongo(db); await x.create_indexes(); counts=await x.hydrate_from_mongo(); logging.getLogger(__name__).info("Source Sync hydrated: %s runs",counts["sync_runs"])
    except Exception as exc: logging.getLogger(__name__).warning("Source Sync persistence skipped: %s",exc)
@app.on_event("startup")
async def _wire_mission_scheduler():
    try:
        from services import mission_scheduler as x; x.attach_mongo(db); await x.create_indexes()
    except Exception as exc: logging.getLogger(__name__).warning("Mission Scheduler persistence skipped: %s",exc)
