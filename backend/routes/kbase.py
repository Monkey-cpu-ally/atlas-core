"""
Knowledge Ingestion routes (prefix /api/kbase).

This is the external Knowledge Bank ingestion API. It turns public sources
into distilled records, exposes source classification, provides the canonical
22-subject source-routing policy, exposes the Existing Resource Library, and
provides supported Project Gutenberg discovery plus book-memory ingestion.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from models.knowledge_models import IngestRequest, SourceType
from services import knowledge_ingestion as ki
from services.book_memory import ingest_gutenberg_book, search_book_memory
from services.knowledge_distiller import route_agent
from services.source_fetchers import IngestError, classify
from services.subject_source_router import SUBJECTS, route_subject, subjects_for_agent
from services.existing_resource_library import (
    all_resources,
    coverage as resource_coverage,
    get_resource,
    search_resources,
)
from services.project_gutenberg_connector import search_books as search_gutenberg_books

router = APIRouter(prefix="/api/kbase", tags=["KnowledgeIngestion"])


class GutenbergIngestRequest(BaseModel):
    query: str = Field(min_length=2, max_length=200)
    book_id: Optional[str] = Field(default=None, max_length=120)
    subjects: List[str] = Field(default_factory=list)
    confirm_public_domain_or_permitted: bool = False


@router.post("/ingest")
async def ingest(req: IngestRequest):
    try:
        return await ki.ingest_url(
            str(req.url),
            project_id=req.project_id,
            force_agent=req.force_agent,
            extra_tags=req.extra_tags,
            pdf_blob_b64=req.pdf_blob,
            pdf_filename=req.pdf_filename,
        )
    except IngestError as exc:
        raise HTTPException(503, f"ingest failed: {exc}") from exc


@router.get("/search")
async def search(
    q: Optional[str] = None,
    agent: Optional[str] = None,
    project_id: Optional[str] = None,
    source_type: Optional[SourceType] = None,
    tag: Optional[str] = None,
    limit: int = Query(30, ge=1, le=200),
):
    rows = await ki.search(
        q=q, agent=agent, project_id=project_id,
        source_type=source_type.value if source_type else None,
        tag=tag, limit=limit,
    )
    return {"count": len(rows), "items": rows}


@router.get("/books/gutenberg/search")
async def gutenberg_search(q: str = Query(min_length=2, max_length=200)):
    try:
        rows = await search_gutenberg_books(q)
    except Exception as exc:  # provider/network boundary
        raise HTTPException(503, f"Project Gutenberg search failed: {exc}") from exc
    return {
        "provider": "Project Gutenberg",
        "query": q,
        "count": len(rows),
        "items": rows,
        "policy": "OPDS discovery; selected plain-text books may be ingested only after rights confirmation",
    }


@router.post("/books/gutenberg/ingest")
async def gutenberg_ingest(req: GutenbergIngestRequest):
    if not req.confirm_public_domain_or_permitted:
        raise HTTPException(
            400,
            "confirm_public_domain_or_permitted must be true before ATLAS stores a full book text",
        )
    unknown = [s for s in req.subjects if not route_subject(s).get("found")]
    if unknown:
        raise HTTPException(400, f"unknown ATLAS subjects: {', '.join(unknown)}")
    canonical_subjects = [route_subject(s)["subject"] for s in req.subjects]
    try:
        return await ingest_gutenberg_book(
            req.query,
            book_id=req.book_id,
            subjects=canonical_subjects,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:  # provider/database boundary
        raise HTTPException(503, f"Project Gutenberg ingestion failed: {exc}") from exc


@router.get("/books/memory/search")
async def book_memory_search(
    q: str = Query(min_length=2, max_length=500),
    persona: str = Query(pattern="^(ajani|minerva|hermes)$"),
    limit: int = Query(default=6, ge=1, le=20),
):
    try:
        rows = await search_book_memory(q, persona=persona, top_k=limit)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "query": q,
        "persona": persona,
        "count": len(rows),
        "items": rows,
        "retrieval": "vector-memory cosine search",
    }


@router.get("/resources")
async def existing_resources(
    subject: Optional[str] = None,
    resource_type: Optional[str] = None,
    provider: Optional[str] = None,
    q: Optional[str] = None,
):
    rows = search_resources(subject=subject, resource_type=resource_type, provider=provider, q=q)
    return {"count": len(rows), "items": rows}


@router.get("/resources/coverage")
async def existing_resource_coverage():
    rows = all_resources()
    return {
        "resource_count": len(rows),
        "subjects": resource_coverage(SUBJECTS),
    }


@router.get("/resources/{resource_id}")
async def existing_resource(resource_id: str):
    row = get_resource(resource_id)
    if not row:
        raise HTTPException(404, "existing resource not found")
    return row


@router.get("/agents/route")
async def preview_routing(text: str = Query(min_length=2, max_length=2000)):
    return {"text": text[:120] + ("..." if len(text) > 120 else ""),
            "suggested_agent": route_agent(text)}


@router.get("/agents/{agent}/subjects")
async def agent_subject_affinity(agent: str):
    subjects = subjects_for_agent(agent)
    if not subjects:
        raise HTTPException(404, "unknown agent or no subject affinity configured")
    return {
        "agent": agent.lower(),
        "preferred_subjects": subjects,
        "access_policy": "all ATLAS personas may query all 22 subjects",
    }


@router.get("/subjects")
async def knowledge_bank_subjects():
    return {"count": len(SUBJECTS), "subjects": SUBJECTS}


@router.get("/subjects/{subject}/sources")
async def subject_sources(subject: str):
    decision = route_subject(subject)
    if not decision["found"]:
        raise HTTPException(404, f"unknown ATLAS subject: {subject}")
    return decision


@router.get("/classify")
async def classify_url(url: str = Query(min_length=8)):
    return {"url": url, "source_type": classify(url).value}


@router.get("/by-url")
async def by_url(url: str = Query(min_length=8)):
    rec = await ki.get_by_url(url)
    if not rec:
        raise HTTPException(404, "no record for that url")
    return rec


@router.get("/{record_id}")
async def get_record(record_id: str):
    rec = await ki.get(record_id)
    if not rec:
        raise HTTPException(404, "knowledge record not found")
    return rec


@router.delete("/{record_id}")
async def delete_record(record_id: str):
    if not await ki.delete(record_id):
        raise HTTPException(404, "knowledge record not found")
    return {"deleted": record_id}
