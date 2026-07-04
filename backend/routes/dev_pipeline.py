"""ATLAS Engineering Console / Development Pipeline REST layer.

Adapted from `atlas_development_pipeline_packet/backend/app/routes/
development_pipeline.py`. All routes are additive — nothing else in the
backend touches these paths.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from services.dev_pipeline_service import pipeline_service

router = APIRouter(prefix="/api/dev/pipeline", tags=["ATLAS Engineering Console"])


@router.get("/status")
async def get_pipeline_status() -> Dict[str, Any]:
    """Aggregate engineering-health snapshot for the HUD dev overlay."""
    return await pipeline_service.get_status()


@router.get("/ping")
async def ping() -> Dict[str, str]:
    return {"pong": "ok"}
