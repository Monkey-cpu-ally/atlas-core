"""Atlas command-center routes for hybrid frontend/backend flow."""

from fastapi import APIRouter

from atlas_core_new.atlas_orchestrator.knowledge import (
    ACADEMIC_FIELDS,
    ACTIVE_PROTOTYPE,
    ATLAS_CAPABILITY_BOUNDARIES,
    ATLAS_VISION,
    FIELD_TEACHING_REQUIREMENTS,
    LONG_TERM_EVOLUTION_PLAN,
)
from atlas_core_new.atlas_orchestrator.models import (
    AtlasOrchestrateRequest,
    AtlasOrchestrateResponse,
    ProjectMemorySnapshot,
    ProjectSummary,
)
from atlas_core_new.atlas_orchestrator.service import AtlasOrchestratorService


router = APIRouter(prefix="/atlas", tags=["atlas-command-center"])
public_router = APIRouter(tags=["atlas-command-center"])
atlas_service = AtlasOrchestratorService()


@router.post("/orchestrate", response_model=AtlasOrchestrateResponse)
def orchestrate(req: AtlasOrchestrateRequest) -> AtlasOrchestrateResponse:
    return atlas_service.orchestrate(req)


@router.post("/route", response_model=AtlasOrchestrateResponse)
def orchestrate_route(req: AtlasOrchestrateRequest) -> AtlasOrchestrateResponse:
    return atlas_service.orchestrate(req)


@public_router.post("/route", response_model=AtlasOrchestrateResponse)
def root_route(req: AtlasOrchestrateRequest) -> AtlasOrchestrateResponse:
    """MVP route endpoint alias requested in PRD."""
    return atlas_service.orchestrate(req)


@router.get("/vision")
def get_atlas_vision() -> dict:
    return {
        "vision": ATLAS_VISION,
        "capability_boundaries": ATLAS_CAPABILITY_BOUNDARIES,
        "evolution_plan": LONG_TERM_EVOLUTION_PLAN,
    }


@router.get("/domains")
def get_atlas_domains() -> dict:
    return {
        "domains": ACADEMIC_FIELDS,
        "teaching_requirements": FIELD_TEACHING_REQUIREMENTS,
    }


@router.get("/prototypes/active")
def get_active_prototype() -> dict:
    return {"prototype": ACTIVE_PROTOTYPE}


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects() -> list[ProjectSummary]:
    return atlas_service.list_projects()


@router.get("/projects/{project}/memory", response_model=ProjectMemorySnapshot)
def get_project_memory(project: str) -> ProjectMemorySnapshot:
    return atlas_service.get_project_memory(project)


@router.post("/projects/{project}/reset", response_model=ProjectMemorySnapshot)
def reset_project_memory(project: str) -> ProjectMemorySnapshot:
    return atlas_service.reset_project(project)

