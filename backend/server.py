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