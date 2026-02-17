"""Atlas command-center routes for hybrid frontend/backend flow."""

from fastapi import APIRouter

from atlas_core_new.atlas_orchestrator.models import (
    AtlasOrchestrateRequest,
    AtlasOrchestrateResponse,
    ProjectMemorySnapshot,
    ProjectSummary,
)
from atlas_core_new.atlas_orchestrator.service import AtlasOrchestratorService


router = APIRouter(prefix="/atlas", tags=["atlas-command-center"])
atlas_service = AtlasOrchestratorService()


@router.post("/orchestrate", response_model=AtlasOrchestrateResponse)
def orchestrate(req: AtlasOrchestrateRequest) -> AtlasOrchestrateResponse:
    return atlas_service.orchestrate(req)


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects() -> list[ProjectSummary]:
    return atlas_service.list_projects()


@router.get("/projects/{project}/memory", response_model=ProjectMemorySnapshot)
def get_project_memory(project: str) -> ProjectMemorySnapshot:
    return atlas_service.get_project_memory(project)


@router.post("/projects/{project}/reset", response_model=ProjectMemorySnapshot)
def reset_project_memory(project: str) -> ProjectMemorySnapshot:
    return atlas_service.reset_project(project)

