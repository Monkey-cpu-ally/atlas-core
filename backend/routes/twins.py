"""
Digital Twin routes — Phase 5.

POST   /api/twins/register                  → DigitalTwin
GET    /api/twins/{id}                      → DigitalTwin | 404
GET    /api/twins/list                      → list (filter by category/owner/project/status)
PUT    /api/twins/{id}/state                → DigitalTwin (revision++)
DELETE /api/twins/{id}                      → {deleted: id}

POST   /api/twins/{id}/simulate             → SimulationResult        body: {kind}
GET    /api/twins/{id}/simulations          → recent sims (≤20)
GET    /api/twins/simulations/{sim_id}      → SimulationResult

POST   /api/twins/{id}/deliberate           → CouncilDeliberation     body: {simulation_id?}
"""
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field

from models.twin_models import (
    DigitalTwin,
    SimulationKind,
    TwinCategory,
    TwinState,
    TwinStatus,
)
from services import digital_twin as dt

router = APIRouter(prefix="/api/twins", tags=["DigitalTwin"])


# --- Request shapes --------------------------------------------------------
class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: TwinCategory
    owner_agent: str = "council"
    related_project_id: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    state: Optional[TwinState] = None


class SimulateRequest(BaseModel):
    kind: SimulationKind


class DeliberateRequest(BaseModel):
    simulation_id: Optional[str] = None


# --- Registry --------------------------------------------------------------
@router.post("/register")
async def register(req: RegisterRequest):
    twin = DigitalTwin(
        name=req.name,
        category=req.category,
        owner_agent=req.owner_agent,
        related_project_id=req.related_project_id,
        description=req.description,
        tags=req.tags,
        state=req.state or TwinState(),
    )
    return await dt.register_twin(twin)


# Static paths MUST be declared before the dynamic /{id} route — FastAPI
# treats /list as twin_id otherwise.
@router.get("/list")
async def list_twins(
    category: Optional[TwinCategory] = None,
    owner_agent: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[TwinStatus] = None,
    limit: int = Query(50, ge=1, le=200),
):
    rows = await dt.list_twins(
        category=category.value if category else None,
        owner_agent=owner_agent,
        project_id=project_id,
        status=status.value if status else None,
        limit=limit,
    )
    return {"count": len(rows), "items": rows}


@router.get("/categories")
async def categories():
    return {
        "categories": [c.value for c in TwinCategory],
        "statuses": [s.value for s in TwinStatus],
        "simulation_kinds": [k.value for k in SimulationKind],
    }


@router.get("/simulations/{sim_id}")
async def get_simulation(sim_id: str):
    sim = await dt.get_simulation(sim_id)
    if not sim:
        raise HTTPException(404, "simulation not found")
    return sim


@router.get("/{twin_id}")
async def get_twin(twin_id: str):
    twin = await dt.get_twin(twin_id)
    if not twin:
        raise HTTPException(404, "twin not found")
    return twin


@router.put("/{twin_id}/state")
async def put_state(twin_id: str, state: TwinState = Body(...)):
    twin = await dt.update_state(twin_id, state)
    if not twin:
        raise HTTPException(404, "twin not found")
    return twin


@router.delete("/{twin_id}")
async def delete_twin(twin_id: str):
    ok = await dt.delete_twin(twin_id)
    if not ok:
        raise HTTPException(404, "twin not found")
    return {"deleted": twin_id}


# --- Simulation ------------------------------------------------------------
@router.post("/{twin_id}/simulate")
async def simulate(twin_id: str, req: SimulateRequest):
    result = await dt.run_and_persist_simulation(twin_id, req.kind)
    if not result:
        raise HTTPException(404, "twin not found")
    return result.model_dump()


@router.get("/{twin_id}/simulations")
async def list_simulations(twin_id: str, limit: int = Query(20, ge=1, le=100)):
    rows = await dt.list_simulations(twin_id, limit=limit)
    return {"count": len(rows), "items": rows}


# --- Deliberation ----------------------------------------------------------
@router.post("/{twin_id}/deliberate")
async def deliberate(twin_id: str, req: DeliberateRequest):
    delib = await dt.deliberate(twin_id, simulation_id=req.simulation_id)
    if not delib:
        raise HTTPException(404, "twin not found")
    return delib.model_dump()
