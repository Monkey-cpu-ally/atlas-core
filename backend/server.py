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
from routes.system_inspector import router as system_inspector_router
from routes.global_knowledge import router as global_knowledge_router
from routes.technology_atlas import router as technology_atlas_router
from routes.project_knowledge import router as project_knowledge_router
from routes.knowledge_chronicle import router as knowledge_chronicle_router
from routes.engineering_os import router as engineering_os_router
from routes.global_sources import router as global_sources_router
from routes.world_knowledge_graph import router as world_knowledge_graph_router
from routes.engineering_playbooks import router as engineering_playbooks_router
from routes.github_pulse import router as github_pulse_router
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
app.include_router(system_inspector_router)
app.include_router(global_knowledge_router)
app.include_router(technology_atlas_router)
app.include_router(project_knowledge_router)
app.include_router(knowledge_chronicle_router)
app.include_router(engineering_os_router)
app.include_router(global_sources_router)
app.include_router(world_knowledge_graph_router)
app.include_router(engineering_playbooks_router)
app.include_router(github_pulse_router)
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
