"""Read-only ATLAS Digital Campus API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from services import campus_engine

router = APIRouter(prefix="/api/campus", tags=["ATLAS Digital Campus"])


@router.get("/health")
async def health() -> dict:
    return campus_engine.campus_health()


@router.get("")
async def campus_summary() -> dict:
    health_report = campus_engine.campus_health()
    return {
        "id": "atlas-digital-engineering-campus",
        "name": "ATLAS Digital Engineering Campus",
        "version": health_report["version"],
        "status": health_report["status"],
        "buildings": campus_engine.list_buildings(),
    }


@router.get("/buildings")
async def buildings() -> list[dict]:
    return campus_engine.list_buildings()


@router.get("/buildings/{building_id}")
async def building(building_id: str) -> dict:
    result = campus_engine.get_building(building_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Campus building not found")
    return result


@router.get("/rooms/{room_id}")
async def room(room_id: str) -> dict:
    result = campus_engine.get_room(room_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Campus room not found")
    return result


@router.get("/search")
async def search(q: str = Query(min_length=1, max_length=120)) -> dict:
    results = campus_engine.search_campus(q)
    return {"query": q, "count": len(results), "results": results}
