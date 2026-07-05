"""ATLAS External Access Gateway routes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import external_access_gateway as gateway

router = APIRouter(prefix="/api/external-access", tags=["ATLAS External Access"])


class ConnectionRequest(BaseModel):
    name: str = Field(min_length=2, max_length=240)
    connector_type: str
    purpose: str = Field(min_length=5, max_length=5000)
    owner_ai: str
    allowed_content: List[str] = Field(default_factory=list)
    blocked_content: List[str] = Field(default_factory=list)
    permission_level: str = "metadata_only"
    status: str = "planned"
    connection_config: Dict[str, Any] = Field(default_factory=dict)
    connection_id: Optional[str] = None


class ImportPlanRequest(BaseModel):
    requested_scope: str = Field(min_length=3, max_length=2000)
    destination_bank: str = "knowledge_bank"
    related_projects: List[str] = Field(default_factory=list)
    require_council_review: bool = True


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "external_access_gateway",
        "persistence_enabled": gateway.persistence_enabled(),
        "connections": len(gateway.list_connections()),
        "import_plans": len(gateway.list_import_plans()),
    }


@router.post("/seed-defaults")
async def seed_defaults():
    result = gateway.seed_default_connections()
    await gateway.persist_all(result["items"])
    return result


@router.post("/connections")
async def create_connection(req: ConnectionRequest):
    try:
        record = gateway.upsert_connection(**req.model_dump())
        await gateway.persist_connection(record)
        return record
    except gateway.ExternalAccessError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/connections")
async def list_connections(
    connector_type: Optional[str] = None,
    owner_ai: Optional[str] = None,
    status: Optional[str] = None,
):
    items = gateway.list_connections(connector_type=connector_type, owner_ai=owner_ai, status=status)
    return {"count": len(items), "items": items}


@router.get("/connections/{connection_id}")
async def get_connection(connection_id: str):
    record = gateway.get_connection(connection_id)
    if not record:
        raise HTTPException(404, f"connection not found: {connection_id}")
    return record


@router.post("/connections/{connection_id}/import-plans")
async def create_import_plan(connection_id: str, req: ImportPlanRequest):
    try:
        plan = gateway.create_import_plan(connection_id=connection_id, **req.model_dump())
        await gateway.persist_import_plan(plan)
        record = gateway.get_connection(connection_id)
        if record:
            await gateway.persist_connection(record)
        return plan
    except gateway.ExternalAccessError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/import-plans")
async def list_import_plans(connection_id: Optional[str] = None, status: Optional[str] = None):
    items = gateway.list_import_plans(connection_id=connection_id, status=status)
    return {"count": len(items), "items": items}
