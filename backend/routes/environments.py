"""Environments REST API — Phase D2.

Mounted at `/api/twins/environments/*`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from models.environment_models import (
    EnvironmentCategory,
    Obstacle,
    TwinEnvironment,
)
from services import environments as env_svc

router = APIRouter(prefix="/api/environments", tags=["Digital Twin · Environments"])


class CreateEnvReq(BaseModel):
    name: str
    category: EnvironmentCategory
    description: Optional[str] = None
    bounds_m: Optional[List[float]] = None
    obstacles: Optional[List[Obstacle]] = None
    gravity_m_s2: Optional[float] = None
    temp_c_range: Optional[List[float]] = None
    humidity_pct_range: Optional[List[float]] = None
    pressure_kpa: Optional[float] = None
    ambient_lux_range: Optional[List[float]] = None
    wind_m_s_range: Optional[List[float]] = None
    atmo_o2_pct: Optional[float] = None
    atmo_co2_ppm: Optional[float] = None
    tags: Optional[List[str]] = None
    owner_agent: Optional[str] = None


@router.post("")
async def create_environment(req: CreateEnvReq):
    spec = req.model_dump(exclude_none=True)
    # Coerce list-of-floats → tuples (Pydantic will accept tuples for the model fields)
    for k in ("bounds_m", "temp_c_range", "humidity_pct_range",
              "ambient_lux_range", "wind_m_s_range"):
        if k in spec:
            spec[k] = tuple(spec[k])
    env = TwinEnvironment(**spec)
    return await env_svc.register_environment(env)


@router.get("")
async def list_environments(category: Optional[str] = None):
    items = await env_svc.list_environments(category=category)
    return {"count": len(items), "items": items}


@router.get("/{env_id}")
async def get_environment(env_id: str):
    env = await env_svc.get_environment(env_id)
    if not env:
        raise HTTPException(404, "environment not found")
    return env


@router.delete("/{env_id}")
async def delete_environment(env_id: str):
    n = await env_svc.delete_environment(env_id)
    if not n:
        raise HTTPException(404, "environment not found")
    return {"deleted": n}


class BindReq(BaseModel):
    twin_id: str
    force: bool = False


@router.post("/{env_id}/bind")
async def bind_twin(env_id: str, req: BindReq):
    result = await env_svc.bind_twin(req.twin_id, env_id, force=req.force)
    return result.model_dump()


@router.post("/{env_id}/unbind")
async def unbind_twin(env_id: str, req: BindReq):
    return await env_svc.unbind_twin(req.twin_id)


@router.post("/seed")
async def seed():
    n = await env_svc.seed_if_needed()
    items = await env_svc.list_environments()
    return {"inserted": n, "total": len(items)}
