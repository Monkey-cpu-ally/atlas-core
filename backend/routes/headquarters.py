"""ATLAS Headquarters routes.

These routes provide polished ATLAS-facing command surfaces for the HUD and
future division chats. They do not replace existing subsystem APIs yet; they
present a premium, organized identity layer above them.
"""
from __future__ import annotations

from fastapi import APIRouter

from services import headquarters_engine

router = APIRouter(prefix="/api/headquarters", tags=["ATLAS Headquarters"])


@router.get("/status")
async def status():
    return headquarters_engine.headquarters_status()


@router.get("/quality-gates")
async def quality_gates():
    return headquarters_engine.quality_gate_report()


@router.get("/atlas-standard")
async def atlas_standard():
    return headquarters_engine.atlas_standard()


@router.get("/mission-control")
async def mission_control():
    return headquarters_engine.mission_control()


@router.get("/knowledge-gate")
async def knowledge_gate():
    return headquarters_engine.knowledge_gate()


@router.get("/source-clearance")
async def source_clearance():
    return headquarters_engine.source_clearance()


@router.get("/project-briefing")
async def project_briefing():
    return headquarters_engine.project_briefing()


@router.get("/refinement")
async def refinement():
    return headquarters_engine.refinement()


@router.get("/technical-debt")
async def technical_debt(status: str | None = None, severity: str | None = None):
    return headquarters_engine.technical_debt_register(status=status, severity=severity)
