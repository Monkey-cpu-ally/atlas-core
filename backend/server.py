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

# Make /app importable so we can find the atlas_core sibling package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import file routes
from routes.files import router as files_router
# Import chat routes
from routes.chat import router as chat_router
# Import knowledge core routes
from routes.knowledge import router as knowledge_router
# Import AI services (TTS / Minerva / Hermes / Blueprint)
from routes.ai_services import router as ai_services_router
# Sandbox — save/replay configs, mastery curve, AI-suggested tweaks
from routes.sandbox import router as sandbox_router
# Council — topic routing + tri-AI deliberation
from routes.council import router as council_router
# HUD surfaces — Memory feed, Manual sections, Settings
from routes.hud_surfaces import router as hud_surfaces_router
# YouTube / external knowledge intake → routed lesson + quiz
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
# Watchers — GitHub link-list ingester + lessons + self-improvement
from routes.watchers import router as watchers_router, kbase_helper_router
from routes.lessons import router as lessons_router
from routes.self_improve import router as self_improve_router
# YouTube channel-RSS resolver + manual transcript ingest + dashboard
from routes.youtube import router as youtube_router
# ATLAS V2: World Watch + Self-Code + Adaptation + Style + Themes
from routes.atlas_v2 import router as atlas_v2_router
# Autonomous Research Orchestrator (Phase 9)
from routes.research_orchestrator import router as research_orch_router
# ATLAS Knowledge Network — World Sources registry + dry-run sync planning
from routes.knowledge_network import router as knowledge_network_router
# ATLAS Research Labs — Ajani/Hermes/Minerva/Council mission queues
from routes.research_labs import router as research_labs_router
# Import ATLAS Core v1 — three cognitive cores, council, teaching, blueprint, shield
from atlas_core import atlas_router as atlas_core_router


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)
app.include_router(files_router)  # File upload and management routes
app.include_router(chat_router)  # AI chat routes
app.include_router(knowledge_router)  # Knowledge core routes
app.include_router(ai_services_router)  # TTS, Minerva, Hermes, Blueprint
app.include_router(sandbox_router)  # Sandbox: save/replay, mastery curve, AI suggest
app.include_router(council_router)  # Topic routing + tri-AI deliberation
app.include_router(hud_surfaces_router)  # Memory feed, Manual, Settings
app.include_router(intake_router)  # YouTube intake → routed lesson + quiz
app.include_router(learning_router)  # Full learning pipeline (lessons/projects/mastery)
app.include_router(llm_router)  # Phase 1: multi-provider LLM (emergent + ollama + lmstudio)
app.include_router(memory_router)  # Phase 2: memory bank + vector search + graph triples
app.include_router(research_router)  # Phase 3: research pipeline (web + pdf + patent)
app.include_router(twins_router)  # Phase 5: digital twin engine (registry + 6 simulators + council)
app.include_router(weaver_router)  # Phase 6: weaver (parts library + blueprint planner + manufacturing)
app.include_router(kbase_router)  # Knowledge Ingestion: distill external sources → MemoryRecords
app.include_router(robot_router)  # Phase 7: robot control layer (devices + telemetry + sim-first command pipeline)
app.include_router(persona_router)  # Phase 8a: persona chat (Ajani · Minerva · Hermes · Council)
app.include_router(watchers_router)  # Knowledge Watcher (GitHub link-list ingester)
app.include_router(kbase_helper_router)  # /api/kbase/sources/github helper
app.include_router(lessons_router)  # Lesson plans generated from watcher runs
app.include_router(self_improve_router)  # ATLAS Self-Improvement Watcher
app.include_router(youtube_router)  # YouTube Learning subsystem (resolver + manual transcript + dashboard)
app.include_router(atlas_v2_router)  # ATLAS V2: worldwatch + self-code + learning + style + themes
app.include_router(research_orch_router)  # Autonomous Research Orchestrator (Phase 9)
app.include_router(knowledge_network_router)  # ATLAS Knowledge Network: sources + dry-run sync planning
app.include_router(research_labs_router)  # ATLAS Research Labs: missions + discoveries + Council review
from routes.environments import router as environments_router  # Phase D2
app.include_router(environments_router)
from routes.nir import router as nir_router  # Phase D4: NIR Scanner
app.include_router(nir_router)
from routes.subjects import router as subjects_router  # Knowledge Bank Phase A
app.include_router(subjects_router)
from routes.research_sources import router as research_sources_router  # Knowledge Bank Phase C
app.include_router(research_sources_router)
# ATLAS Core v1 — mounted at /api/atlas/* so the HUD can talk to the new
# cognition stack (council, mental simulation, teaching, identity anchor).
app.include_router(atlas_core_router, prefix="/api")


# --- Exports — let the architect download the AI architecture zip --------
EXPORTS_DIR = Path("/app/exports")


@app.get("/api/exports/atlas-ai-architecture.zip")
async def download_architecture_zip():
    """Serve the bundled AI architecture zip for download."""
    path = EXPORTS_DIR / "atlas-ai-architecture.zip"
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(404, "architecture zip not yet built")
    return FileResponse(
        path=str(path),
        filename="atlas-ai-architecture.zip",
        media_type="application/zip",
    )


@app.get("/api/exports/atlas-hud-architecture.zip")
async def download_hud_zip():
    """Serve the bundled HUD frontend architecture zip for download."""
    path = EXPORTS_DIR / "atlas-hud-architecture.zip"
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(404, "HUD architecture zip not yet built")
    return FileResponse(
        path=str(path),
        filename="atlas-hud-architecture.zip",
        media_type="application/zip",
    )


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

# Wire ATLAS memory to MongoDB on startup so archive entries, conversations,
# and audit events persist across restarts.
from atlas_core.memory.memory import attach_mongo_on_startup as _atlas_attach_mongo

@app.on_event("startup")
async def _wire_atlas_memory():
    await _atlas_attach_mongo()


# Research Labs — attach MongoDB so missions/discoveries persist across restarts.
@app.on_event("startup")
async def _wire_research_labs():
    try:
        from services import research_lab_engine as _research_labs
        _research_labs.attach_mongo(db)
        await _research_labs.create_indexes()
        counts = await _research_labs.hydrate_from_mongo()
        logging.getLogger(__name__).info(
            "Research Labs hydrated: %s missions · %s discoveries",
            counts["missions"], counts["discoveries"],
        )
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Research Lab persistence skipped: %s", exc)


# Phase 7 — Seed POSEIDON-BUOY / AETHER-STATION / SOIL-WATCH on first boot
# (each auto-bound to its own Digital Twin via services/robot.py).
from services import robot as _robot_service

@app.on_event("startup")
async def _seed_phase7_devices():
    try:
        inserted = await _robot_service.seed_if_needed()
        if inserted:
            logging.getLogger(__name__).info(
                "Phase 7: seeded %d robot devices + twins", inserted
            )
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning(
            "Phase 7 seed skipped: %s", exc
        )


# Phase 8h — Sentinel Autonomic Watcher (loops at SENTINEL_AUTONOMIC_INTERVAL_S
# seconds, fires Council on every newly-detected anomaly).
@app.on_event("startup")
async def _start_sentinel_watcher():
    try:
        from services import sentinel_watcher
        await sentinel_watcher.start()
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning(
            "Sentinel autonomic watcher failed to start: %s", exc
        )


# Phase D2 — Twin Environments: seed 5 realistic environments (lab,
# outdoor, aerial, aquatic, lunar) on first boot. Idempotent.
@app.on_event("startup")
async def _seed_twin_environments():
    try:
        from services import environments as env_svc
        n = await env_svc.seed_if_needed()
        if n:
            logging.getLogger(__name__).info("Twin environments seeded: %s new", n)
    except Exception as exc:    # noqa: BLE001
        logging.getLogger(__name__).warning("environment seed failed: %s", exc)


# Phase D4 — NIR Scanner: seed a 12-entry NIR library (plastics, agri,
# materials) on first boot. Idempotent.
@app.on_event("startup")
async def _seed_nir_library():
    try:
        from services import nir as nir_svc
        n = await nir_svc.seed_library_if_needed()
        if n:
            logging.getLogger(__name__).info("NIR library seeded: %s new entries", n)
    except Exception as exc:    # noqa: BLE001
        logging.getLogger(__name__).warning("NIR seed failed: %s", exc)


# Knowledge Bank Phase A — Seed 22 subjects on first boot. Idempotent.
@app.on_event("startup")
async def _seed_subjects():
    try:
        from services import subjects as subj_svc
        n = await subj_svc.seed_if_needed()
        if n:
            logging.getLogger(__name__).info("Subjects seeded: %s new", n)
    except Exception as exc:    # noqa: BLE001
        logging.getLogger(__name__).warning("subject seed failed: %s", exc)


# Phases D5 + D6 — Reference twins: AGRI-ROVER-01 (Green Robot),
# ATLAS-CELL-V1 (Li-ion power cell), ATLAS-CELL-SS-V1 (Solid-state).
# Each twin is also mirrored as a reference blueprint stub.
@app.on_event("startup")
async def _seed_reference_twins():
    try:
        from services import reference_twins
        r = await reference_twins.seed_if_needed()
        if r["inserted_twins"]:
            logging.getLogger(__name__).info(
                "Reference twins seeded: %s · blueprints: %s",
                r["inserted_twins"], r["inserted_blueprints"],
            )
    except Exception as exc:    # noqa: BLE001
        logging.getLogger(__name__).warning("reference twin seed failed: %s", exc)


# Phase 8c.2 — MQTT bidirectional bridge: capture the running event loop
# and wire the device→Atlas telemetry uplink subscriber. Dormant if
# MQTT_BROKER_HOST is unset.
@app.on_event("startup")
async def _start_mqtt_uplink():
    try:
        import asyncio as _asyncio
        from services import mqtt_bridge
        mqtt_bridge.set_loop(_asyncio.get_running_loop())
        if mqtt_bridge.is_enabled():
            status = mqtt_bridge.enable_uplink()
            logging.getLogger(__name__).info("MQTT uplink: %s", status)
    except Exception as exc:    # noqa: BLE001
        logging.getLogger(__name__).warning("MQTT uplink wire failed: %s", exc)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    # Phase 8c — clean MQTT bridge shutdown (no-op when dormant)
    try:
        from services import mqtt_bridge
        mqtt_bridge.shutdown()
    except Exception:    # noqa: BLE001
        pass
    # Phase 8h — stop the Sentinel autonomic loop
    try:
        from services import sentinel_watcher
        await sentinel_watcher.stop()
    except Exception:    # noqa: BLE001
        pass
