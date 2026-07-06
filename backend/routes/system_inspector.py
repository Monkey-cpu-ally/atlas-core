"""ATLAS System Inspector routes."""
from __future__ import annotations

from fastapi import APIRouter

from services import system_inspector

router = APIRouter(prefix="/api/system-inspector", tags=["ATLAS System Inspector"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "system_inspector",
        "purpose": "Repository and engineering quality inspection.",
    }


@router.get("/report")
async def report():
    return system_inspector.inspect_repository()


@router.get("/technical-debt")
async def technical_debt():
    return system_inspector.technical_debt_register()


@router.get("/certification")
async def certification():
    return system_inspector.certification_report()
