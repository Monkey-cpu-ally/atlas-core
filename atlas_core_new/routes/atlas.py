"""Atlas command-center routes for hybrid frontend/backend flow."""

from fastapi import APIRouter

from atlas_core_new.atlas_orchestrator.knowledge import (
    ACADEMIC_FIELDS,
    ACADEMIC_INTEGRATION_PLAN,
    ACTIVE_PROTOTYPE,
    ATLAS_CAPABILITY_BOUNDARIES,
    ATLAS_PROJECT_REGISTRY,
    ATLAS_VISION,
    CAPABILITY_MATRIX,
    DOCTRINE_FREEZE,
    END_STATE_VISION_GROUNDED,
    FIELD_TEACHING_REQUIREMENTS,
    HYBRID_OPERATIONAL_RULES,
    LONG_TERM_EVOLUTION_PLAN,
    TEACHING_FRAMEWORK_LOCK,
    get_project_registry_entry,
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
        "end_state_grounded": END_STATE_VISION_GROUNDED,
        "project_registry_overview": {
            "count": len(ATLAS_PROJECT_REGISTRY),
            "project_ids": [item["id"] for item in ATLAS_PROJECT_REGISTRY],
        },
        "capability_matrix_summary": CAPABILITY_MATRIX,
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


@router.get("/project-registry")
def get_project_registry() -> dict:
    return {"projects": ATLAS_PROJECT_REGISTRY}


@router.get("/project-registry/{project}")
def get_project_registry_item(project: str) -> dict:
    entry = get_project_registry_entry(project)
    return {"project": project, "entry": entry}


@router.get("/capability-matrix")
def get_capability_matrix() -> dict:
    return {"matrix": CAPABILITY_MATRIX}


@router.get("/teaching-framework")
def get_teaching_framework() -> dict:
    return {
        "framework_lock": TEACHING_FRAMEWORK_LOCK,
        "teaching_requirements": FIELD_TEACHING_REQUIREMENTS,
    }


@router.get("/academic-integration-plan")
def get_academic_integration_plan() -> dict:
    return {"plan": ACADEMIC_INTEGRATION_PLAN}


@router.get("/operational-rules")
def get_operational_rules() -> dict:
    return {"rules": HYBRID_OPERATIONAL_RULES}


@router.get("/doctrine")
def get_doctrine() -> dict:
    return {
        "doctrine_freeze": DOCTRINE_FREEZE,
        "capability_matrix": CAPABILITY_MATRIX,
        "teaching_framework_lock": TEACHING_FRAMEWORK_LOCK,
        "operational_rules": HYBRID_OPERATIONAL_RULES,
    }


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects() -> list[ProjectSummary]:
    return atlas_service.list_projects()


@router.get("/projects/{project}/memory", response_model=ProjectMemorySnapshot)
def get_project_memory(project: str) -> ProjectMemorySnapshot:
    return atlas_service.get_project_memory(project)


@router.post("/projects/{project}/reset", response_model=ProjectMemorySnapshot)
def reset_project_memory(project: str) -> ProjectMemorySnapshot:
    return atlas_service.reset_project(project)

