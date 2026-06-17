"""
Weaver routes — Phase 6.

POST   /api/weaver/parts                       → add a part to the library
GET    /api/weaver/parts                       → list / search the library
GET    /api/weaver/parts/{id}                  → fetch one
DELETE /api/weaver/parts/{id}                  → remove one
GET    /api/weaver/parts/categories            → enum introspection
POST   /api/weaver/parts/seed                  → idempotent starter seed

POST   /api/weaver/analyze                     → parse blueprint, no twin spawned
POST   /api/weaver/plan                        → full pipeline → WeaverPlan
GET    /api/weaver/plans                       → list plans
GET    /api/weaver/plans/{id}                  → fetch one
DELETE /api/weaver/plans/{id}?drop_twin=…      → delete a plan (optional cascade)
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from models.weaver_models import (
    BlueprintInput,
    Part,
    PartCategory,
)
from services import blueprint_parser, parts_db, weaver

router = APIRouter(prefix="/api/weaver", tags=["Weaver"])


# --- Parts library --------------------------------------------------------
@router.post("/parts/seed")
async def seed():
    inserted = await parts_db.ensure_seeded()
    return {"seeded": inserted}


@router.get("/parts/categories")
async def part_categories():
    return {"categories": [c.value for c in PartCategory]}


@router.post("/parts")
async def add_part(part: Part):
    return await parts_db.add_part(part)


@router.get("/parts")
async def list_parts(
    category: Optional[PartCategory] = None,
    q: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
):
    rows = await parts_db.list_parts(
        category=category.value if category else None, q=q, limit=limit,
    )
    return {"count": len(rows), "items": rows}


@router.get("/parts/{part_id}")
async def get_part(part_id: str):
    p = await parts_db.get_part(part_id)
    if not p:
        raise HTTPException(404, "part not found")
    return p


@router.delete("/parts/{part_id}")
async def delete_part(part_id: str):
    if not await parts_db.delete_part(part_id):
        raise HTTPException(404, "part not found")
    return {"deleted": part_id}


# --- Blueprint analyze ----------------------------------------------------
class AnalyzeRequest(BaseModel):
    blueprint: BlueprintInput


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """Parse a blueprint and enrich parts via the library — without
    spawning a twin or running simulations. Useful for previewing what
    Weaver sees before committing to a full plan."""
    parts, relations = await blueprint_parser.parse(req.blueprint)
    parts = await blueprint_parser.match_against_library(parts)
    return {
        "parts": [p.model_dump() for p in parts],
        "relations": [r.model_dump() for r in relations],
        "library_match_count": sum(1 for p in parts if p.library_part_id),
        "unknown_count": sum(1 for p in parts if not p.library_part_id),
    }


# --- Plan (full pipeline) -------------------------------------------------
class PlanRequest(BaseModel):
    title: str = Field(min_length=2, max_length=140)
    description: Optional[str] = None
    owner_agent: str = "ajani"
    related_project_id: Optional[str] = None
    blueprint: BlueprintInput
    deliberate: bool = True


@router.post("/plan")
async def plan(req: PlanRequest):
    try:
        result = await weaver.plan_from_blueprint(
            title=req.title,
            description=req.description,
            owner_agent=req.owner_agent,
            related_project_id=req.related_project_id,
            blueprint=req.blueprint,
            deliberate=req.deliberate,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return result.model_dump()


@router.get("/plans")
async def list_plans(
    owner_agent: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    rows = await weaver.list_plans(
        owner_agent=owner_agent, project_id=project_id, limit=limit,
    )
    return {"count": len(rows), "items": rows}


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str):
    p = await weaver.get_plan(plan_id)
    if not p:
        raise HTTPException(404, "plan not found")
    return p


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, drop_twin: bool = False):
    if not await weaver.delete_plan(plan_id, drop_twin=drop_twin):
        raise HTTPException(404, "plan not found")
    return {"deleted": plan_id, "twin_dropped": bool(drop_twin)}
