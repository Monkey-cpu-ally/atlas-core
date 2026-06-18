"""
Watcher routes (prefix /api/watchers).

GET   /api/watchers/sources                → list registered sources
POST  /api/watchers/github/register        → register a GitHub repo
POST  /api/watchers/github/run             → run a watcher source now
GET   /api/watchers/github/status          → status for a specific source
GET   /api/watchers/proof/{source_id}      → proof-of-execution record
GET   /api/kbase/sources/github            → all GitHub knowledge entries
                                              (helper: shows what the watcher ingested)
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl

from services import knowledge_watcher as kw
from services import knowledge_ingestion as ki

router = APIRouter(prefix="/api/watchers", tags=["Watchers"])


class GithubRegisterReq(BaseModel):
    url: HttpUrl
    label: Optional[str] = None


class GithubRunReq(BaseModel):
    source_id: str
    generate_lesson: bool = True
    max_links: int = 40


@router.get("/sources")
async def list_sources(kind: Optional[str] = None):
    items = await kw.list_sources(kind=kind)
    return {"count": len(items), "items": items}


@router.post("/github/register")
async def register_github(req: GithubRegisterReq):
    try:
        return await kw.register_github_source(str(req.url), label=req.label)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/github/run")
async def run_github(req: GithubRunReq):
    try:
        return await kw.run_github_watcher(
            req.source_id,
            generate_lesson=req.generate_lesson,
            max_links=req.max_links,
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/github/status")
async def github_status(source_id: str = Query(...)):
    s = await kw.get_status(source_id)
    if not s:
        raise HTTPException(404, "unknown watcher source")
    return s


@router.get("/proof/{source_id}")
async def proof(source_id: str):
    p = await kw.get_proof(source_id)
    if not p:
        raise HTTPException(404, "no run found for source")
    return p


# --- helper that lives under the watchers section but reaches into kbase --
kbase_helper_router = APIRouter(prefix="/api/kbase", tags=["Watchers"])


@kbase_helper_router.get("/sources/github")
async def github_sources(limit: int = Query(50, ge=1, le=500)):
    """All knowledge entries that came from a GitHub source."""
    rows = await ki.search(source_type="github", limit=limit)
    return {"count": len(rows), "items": rows}
