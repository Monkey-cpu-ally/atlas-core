"""
Knowledge Ingestion routes (prefix /api/kbase).

Distinct from the legacy `/api/knowledge` 22-subject teaching endpoints
(see routes/knowledge_core.py) — this module is the new Knowledge
Ingestion System that turns external URLs into distilled MemoryRecords.

Endpoints:
  POST   /api/kbase/ingest                    → ingest a URL (or PDF blob)
  GET    /api/kbase/search                    → search records
  GET    /api/kbase/{id}                      → fetch a single record
  GET    /api/kbase/by-url                    → fetch by exact URL
  DELETE /api/kbase/{id}                      → remove a record (does NOT drop mb row)
  GET    /api/kbase/agents/route              → preview the routing decision
  GET    /api/kbase/classify                  → preview source-type classification
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from models.knowledge_models import IngestRequest, SourceType
from services import knowledge_ingestion as ki
from services.knowledge_distiller import route_agent
from services.source_fetchers import IngestError, classify

router = APIRouter(prefix="/api/kbase", tags=["KnowledgeIngestion"])


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


@router.get("/agents/route")
async def preview_routing(text: str = Query(min_length=2, max_length=2000)):
    return {"text": text[:120] + ("..." if len(text) > 120 else ""),
            "suggested_agent": route_agent(text)}


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
