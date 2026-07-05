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
from routes.headquarters import router as headquarters_router
from atlas_core import atlas_router as atlas_core_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


app.include_router(api_router)
app.include_router(files_router)
app.include_router(chat_router)
app.include_router(knowledge_router)
app.include_router(ai_services_router)
app.include_router(sandbox_router)
app.include_router(council_router)
app.include_router(hud_surfaces_router)
app.include_router(intake_router)
app.include_router(learning_router)
app.include_router(llm_router)
app.include_router(memory_router)
app.include_router(research_router)
app.include_router(twins_router)
app.include_router(weaver_router)
app.include_router(kbase_router)
app.include_router(robot_router)
app.include_router(persona_router)
app.include_router(watchers_router)
app.include_router(kbase_helper_router)
app.include_router(lessons_router)
app.include_router(self_improve_router)
app.include_router(youtube_router)
app.include_router(atlas_v2_router)
app.include_router(research_orch_router)
app.include_router(knowledge_network_router)
app.include_router(research_labs_router)
app.include_router(knowledge_graph_router)
app.include_router(autonomous_knowledge_router)
app.include_router(source_sync_router)
app.include_router(mission_scheduler_router)
app.include_router(project_intelligence_router)
app.include_router(external_access_router)
app.include_router(discovery_approval_router)
app.include_router(headquarters_router)
from routes.environments import router as environments_router
app.include_router(environments_router)
from routes.nir import router as nir_router
app.include_router(nir_router)
from routes.subjects import router as subjects_router
app.include_router(subjects_router)
from routes.research_sources import router as research_sources_router
app.include_router(research_sources_router)
app.include_router(atlas_core_router, prefix="/api")

EXPORTS_DIR = Path("/app/exports")


@app.get("/api/exports/atlas-ai-architecture.zip")
async def download_architecture_zip():
    path = EXPORTS_DIR / "atlas-ai-architecture.zip"
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(404, "architecture zip not yet built")
    return FileResponse(path=str(path), filename="atlas-ai-architecture.zip", media_type="application/zip")


@app.get("/api/exports/atlas-hud-architecture.zip")
async def download_hud_zip():
    path = EXPORTS_DIR / "atlas-hud-architecture.zip"
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(404, "HUD architecture zip not yet built")
    return FileResponse(path=str(path), filename="atlas-hud-architecture.zip", media_type="application/zip")


@app.get("/api/exports/README.md")
async def download_readme():
    path = EXPORTS_DIR / "README.md"
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(404, "readme not found")
    return FileResponse(path=str(path), filename="atlas-architecture-README.md", media_type="text/markdown")


@app.get("/api/exports/README-HUD.md")
async def download_hud_readme():
    path = EXPORTS_DIR / "README-HUD.md"
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(404, "HUD readme not found")
    return FileResponse(path=str(path), filename="atlas-hud-README.md", media_type="text/markdown")


from atlas_core.memory.memory import attach_mongo_on_startup as _atlas_attach_mongo


@app.on_event("startup")
async def _wire_atlas_memory():
    await _atlas_attach_mongo()


@app.on_event("startup")
async def _wire_research_labs():
    try:
        from services import research_lab_engine as _research_labs
        _research_labs.attach_mongo(db)
        await _research_labs.create_indexes()
        counts = await _research_labs.hydrate_from_mongo()
        logging.getLogger(__name__).info("Research Labs hydrated: %s missions · %s discoveries", counts["missions"], counts["discoveries"])
    except Exception as exc:
        logging.getLogger(__name__).warning("Research Lab persistence skipped: %s", exc)


@app.on_event("startup")
async def _wire_knowledge_graph():
    try:
        from services import knowledge_graph_engine as _knowledge_graph
        _knowledge_graph.attach_mongo(db)
        await _knowledge_graph.create_indexes()
        counts = await _knowledge_graph.hydrate_from_mongo()
        logging.getLogger(__name__).info("Knowledge Graph hydrated: %s nodes · %s edges", counts["nodes"], counts["edges"])
    except Exception as exc:
        logging.getLogger(__name__).warning("Knowledge Graph persistence skipped: %s", exc)


@app.on_event("startup")
async def _wire_autonomous_knowledge():
    try:
        from services import autonomous_knowledge_engine as _ake
        _ake.attach_mongo(db)
        await _ake.create_indexes()
        counts = await _ake.hydrate_from_mongo()
        logging.getLogger(__name__).info("Autonomous Knowledge hydrated: %s jobs", counts["jobs"])
    except Exception as exc:
        logging.getLogger(__name__).warning("Autonomous Knowledge persistence skipped: %s", exc)


@app.on_event("startup")
async def _wire_source_sync():
    try:
        from services import source_sync_engine as _source_sync
        _source_sync.attach_mongo(db)
        await _source_sync.create_indexes()
        counts = await _source_sync.hydrate_from_mongo()
        logging.getLogger(__name__).info("Source Sync hydrated: %s runs", counts["sync_runs"])
    except Exception as exc:
        logging.getLogger(__name__).warning("Source Sync persistence skipped: %s", exc)


@app.on_event("startup")
async def _wire_mission_scheduler():
    try:
        from services import mission_scheduler as _mission_scheduler
        _mission_scheduler.attach_mongo(db)
        await _mission_scheduler.create_indexes()
        counts = await _mission_scheduler.hydrate_from_mongo()
        logging.getLogger(__name__).info("Mission Scheduler hydrated: %s schedules", counts["schedules"])
    except Exception as exc:
        logging.getLogger(__name__).warning("Mission Scheduler persistence skipped: %s", exc)


@app.on_event("startup")
async def _wire_project_intelligence():
    try:
        from services import project_intelligence as _project_intelligence
        _project_intelligence.attach_mongo(db)
        await _project_intelligence.create_indexes()
        counts = await _project_intelligence.hydrate_from_mongo()
        logging.getLogger(__name__).info("Project Intelligence hydrated: %s projects", counts["projects"])
    except Exception as exc:
        logging.getLogger(__name__).warning("Project Intelligence persistence skipped: %s", exc)


@app.on_event("startup")
async def _wire_external_access():
    try:
        from services import external_access_gateway as _external_access
        _external_access.attach_mongo(db)
        await _external_access.create_indexes()
        counts = await _external_access.hydrate_from_mongo()
        if counts["connections"] == 0:
            seeded = _external_access.seed_default_connections()
            await _external_access.persist_all(seeded["items"])
            counts = await _external_access.hydrate_from_mongo()
        logging.getLogger(__name__).info("External Access hydrated: %s connections · %s import plans", counts["connections"], counts["import_plans"])
    except Exception as exc:
        logging.getLogger(__name__).warning("External Access persistence skipped: %s", exc)


@app.on_event("startup")
async def _wire_discovery_approval():
    try:
        from services import chronicle_engine as _chronicle
        from services import discovery_approval_pipeline as _dap
        from services import knowledge_record_writer as _krw
        _dap.attach_mongo(db)
        _krw.attach_mongo(db)
        _chronicle.attach_mongo(db)
        await _dap.create_indexes()
        await _krw.create_indexes()
        await _chronicle.create_indexes()
        dcounts = await _dap.hydrate_from_mongo()
        kcounts = await _krw.hydrate_from_mongo()
        ccounts = await _chronicle.hydrate_from_mongo()
        logging.getLogger(__name__).info(
            "Discovery Approval hydrated: %s drafts · %s records · %s chronicle entries",
            dcounts["discovery_drafts"], kcounts["knowledge_records"], ccounts["chronicle_entries"]
        )
    except Exception as exc:
        logging.getLogger(__name__).warning("Discovery Approval persistence skipped: %s", exc)


from services import robot as _robot_service


@app.on_event("startup")
async def _seed_phase7_devices():
    try:
        inserted = await _robot_service.seed_if_needed()
        if inserted:
            logging.getLogger(__name__).info("Phase 7: seeded %d robot devices + twins", inserted)
    except Exception as exc:
        logging.getLogger(__name__).warning("Phase 7 seed skipped: %s", exc)


@app.on_event("startup")
async def _start_sentinel_watcher():
    try:
        from services import sentinel_watcher
        await sentinel_watcher.start()
    except Exception as exc:
        logging.getLogger(__name__).warning("Sentinel autonomic watcher failed to start: %s", exc)


@app.on_event("startup")
async def _seed_twin_environments():
    try:
        from services import environments as env_svc
        n = await env_svc.seed_if_needed()
        if n:
            logging.getLogger(__name__).info("Twin environments seeded: %s new", n)
    except Exception as exc:
        logging.getLogger(__name__).warning("environment seed failed: %s", exc)


@app.on_event("startup")
async def _seed_nir_library():
    try:
        from services import nir as nir_svc
        n = await nir_svc.seed_library_if_needed()
        if n:
            logging.getLogger(__name__).info("NIR library seeded: %s new entries", n)
    except Exception as exc:
        logging.getLogger(__name__).warning("NIR seed failed: %s", exc)


@app.on_event("startup")
async def _seed_subjects():
    try:
        from services import subjects as subj_svc
        n = await subj_svc.seed_if_needed()
        if n:
            logging.getLogger(__name__).info("Subjects seeded: %s new", n)
    except Exception as exc:
        logging.getLogger(__name__).warning("subject seed failed: %s", exc)


@app.on_event("startup")
async def _seed_reference_twins():
    try:
        from services import reference_twins
        r = await reference_twins.seed_if_needed()
        if r["inserted_twins"]:
            logging.getLogger(__name__).info("Reference twins seeded: %s · blueprints: %s", r["inserted_twins"], r["inserted_blueprints"])
    except Exception as exc:
        logging.getLogger(__name__).warning("reference twin seed failed: %s", exc)


@app.on_event("startup")
async def _start_mqtt_uplink():
    try:
        import asyncio as _asyncio
        from services import mqtt_bridge
        mqtt_bridge.set_loop(_asyncio.get_running_loop())
        if mqtt_bridge.is_enabled():
            status = mqtt_bridge.enable_uplink()
            logging.getLogger(__name__).info("MQTT uplink: %s", status)
    except Exception as exc:
        logging.getLogger(__name__).warning("MQTT uplink wire failed: %s", exc)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"]
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    try:
        from services import mqtt_bridge
        mqtt_bridge.shutdown()
    except Exception:
        pass
    try:
        from services import sentinel_watcher
        await sentinel_watcher.stop()
    except Exception:
        pass
