"""
Research routes — Phase 3 + Knowledge Bank bridge.

Public API:
  POST /api/research/web         — search + scrape + summarise + memory store
  POST /api/research/pdf         — multipart pdf upload → chunk + summarise + memory
  POST /api/research/patent      — patent research
  POST /api/research/orchestrate — subject-aware research using the existing pipeline
  GET  /api/research/recent      — list recent 'research' memories
"""
import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from services import memory_bank as mb
from services.patent_client import PatentUnreachable
from services.research_orchestrator_bridge import orchestrate_research
from services.research_pipeline import (
    research_patents,
    research_pdf,
    research_web,
)
from services.web_scraper import ResearchUnreachable

logger = logging.getLogger("atlas.research")
router = APIRouter(prefix="/api/research", tags=["Research"])

MAX_PDF_BYTES = 12 * 1024 * 1024


class WebRequest(BaseModel):
    query: str = Field(min_length=2, max_length=400)
    top_n: int = Field(default=5, ge=1, le=10)
    summarise: bool = True


@router.post("/web")
async def web(req: WebRequest):
    try:
        return await research_web(req.query, top_n=req.top_n, summarise=req.summarise)
    except ResearchUnreachable as exc:
        raise HTTPException(503, str(exc)) from exc


class OrchestrateRequest(BaseModel):
    subject: str = Field(min_length=2, max_length=100)
    query: str = Field(min_length=2, max_length=400)
    top_n: int = Field(default=5, ge=1, le=10)
    use_live_web: bool = True
    ingest_catalog_resources: bool = False


@router.post("/orchestrate")
async def orchestrate(req: OrchestrateRequest):
    """Use the existing research pipeline with Knowledge Bank routing.

    The bridge first resolves the canonical ATLAS subject, recommends trusted
    source families, surfaces existing human-written resources, optionally
    ingests those resources through the Knowledge Bank, and can then run the
    existing live web research path.
    """
    try:
        return await orchestrate_research(
            subject=req.subject,
            query=req.query,
            top_n=req.top_n,
            use_live_web=req.use_live_web,
            ingest_catalog_resources=req.ingest_catalog_resources,
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ResearchUnreachable as exc:
        raise HTTPException(503, str(exc)) from exc


class PatentRequest(BaseModel):
    query: str = Field(min_length=2, max_length=400)
    top_n: int = Field(default=5, ge=1, le=10)
    deep: bool = False


@router.post("/patent")
async def patent(req: PatentRequest):
    try:
        return await research_patents(req.query, top_n=req.top_n, deep=req.deep)
    except PatentUnreachable as exc:
        raise HTTPException(503, str(exc)) from exc


@router.post("/pdf")
async def pdf(
    file: UploadFile = File(...),
    summarise: bool = Form(default=True),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "file must be a .pdf")
    blob = await file.read()
    if not blob:
        raise HTTPException(400, "empty upload")
    if len(blob) > MAX_PDF_BYTES:
        raise HTTPException(413, f"pdf too large (>{MAX_PDF_BYTES // (1024*1024)} MB)")
    try:
        return await research_pdf(blob, filename=file.filename, summarise=summarise)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/recent")
async def recent(limit: int = 20, source_type: Optional[str] = None):
    rows = await mb.list_memories(category="research", limit=limit, include_decayed=True)
    if source_type:
        rows = [r for r in rows if r.get("source_type") == source_type.lower()]
    return {"count": len(rows), "items": rows}
