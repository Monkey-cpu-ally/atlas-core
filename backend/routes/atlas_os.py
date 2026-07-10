"""AtlasOS control-plane API routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from services import atlas_os_control_plane as control_plane

router = APIRouter(prefix="/atlas-os", tags=["AtlasOS"])


@router.get("/health")
async def health():
    validation = control_plane.validate_registry()
    return {
        "status": "ok" if validation["valid"] else "degraded",
        "platform": "AtlasOS",
        "registry_valid": validation["valid"],
        "service_count": validation["service_count"],
    }


@router.get("/summary")
async def summary():
    return control_plane.platform_summary()


@router.get("/services")
async def list_services(
    owner_ai: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    items = control_plane.list_services(
        owner_ai=owner_ai,
        category=category,
        status=status,
    )
    return {"count": len(items), "items": items}


@router.get("/services/{service_id}")
async def get_service(service_id: str):
    service = control_plane.get_service(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail=f"AtlasOS service not found: {service_id}")
    return service


@router.get("/startup-order")
async def startup_order():
    return {"items": control_plane.dependency_order()}


@router.get("/validate")
async def validate():
    return control_plane.validate_registry()
