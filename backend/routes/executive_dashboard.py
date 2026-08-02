"""AtlasOS Executive Dashboard API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services import campus_engine
from services import knowledge_governance_engine
from services import service_health_registry as registry


router = APIRouter(prefix="/api/executive-dashboard", tags=["Executive Dashboard"])


def _register_default_probes() -> None:
    registry.register_probe("campus-service", campus_engine.campus_health)
    registry.register_probe("knowledge-service", knowledge_governance_engine.governance_health)


_register_default_probes()


@router.get("/health")
async def health():
    return await registry.executive_summary()


@router.get("/services")
async def services():
    return await registry.all_service_health()


@router.get("/services/{service_id}")
async def service(service_id: str):
    result = await registry.service_health(service_id)
    if result is None:
        raise HTTPException(status_code=404, detail="AtlasOS service not found")
    return result


@router.get("/registry")
async def registry_manifest():
    return registry.registry_manifest()


@router.get("/overview")
async def overview():
    system = await registry.executive_summary()
    campus = campus_engine.campus_health()
    knowledge = knowledge_governance_engine.governance_health()
    return {
        "status": system["status"],
        "system": system,
        "campus": campus,
        "knowledge_bank": knowledge,
        "ai_color_standards": campus.get("ai_standards", {}),
        "next_actions": _next_actions(system),
    }


def _next_actions(system: dict) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for service_id in system.get("v1_blockers", []):
        actions.append({"priority": "critical", "service_id": service_id, "action": "Implement or restore this Version 1 service."})
    for service_id in system.get("v1_uncertain", []):
        actions.append({"priority": "high", "service_id": service_id, "action": "Register a truthful runtime health probe."})
    for service_id in system.get("v1_degraded", []):
        actions.append({"priority": "high", "service_id": service_id, "action": "Inspect degraded health details and repair the failing dependency."})
    if not actions:
        actions.append({"priority": "normal", "service_id": "atlas-os", "action": "Continue implementation and regression testing."})
    return actions
