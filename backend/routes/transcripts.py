"""Transcripts + Summaries REST API — Knowledge Bank Phase E.

Mounted at `/api/transcripts/*`.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import transcripts as tr_svc
from services.transcripts import Transcript, TranscriptSource

router = APIRouter(prefix="/api/transcripts",
                   tags=["Knowledge Bank · Transcripts"])


class StoreReq(BaseModel):
    title: str
    text: str
    source: TranscriptSource = TranscriptSource.OTHER
    source_url: Optional[str] = None
    author_or_channel: Optional[str] = None
    duration_seconds: Optional[float] = None
    language: str = "en"
    youtube_channel_id: Optional[str] = None
    subject_slug: Optional[str] = None
    agent: str = "minerva"
    tags: List[str] = Field(default_factory=list)


@router.post("")
async def store(req: StoreReq):
    return await tr_svc.store(Transcript(**req.model_dump()))


@router.get("")
async def list_transcripts(
    source: Optional[str] = None,
    subject_slug: Optional[str] = None,
    agent: Optional[str] = None,
    limit: int = Query(40, ge=1, le=200),
):
    items = await tr_svc.list_transcripts(
        source=source, subject_slug=subject_slug, agent=agent, limit=limit,
    )
    return {"count": len(items), "items": items}


@router.get("/stats")
async def stats():
    return await tr_svc.stats()


@router.get("/{transcript_id}")
async def get(transcript_id: str):
    doc = await tr_svc.get(transcript_id)
    if not doc:
        raise HTTPException(404, "transcript not found")
    return doc


@router.post("/{transcript_id}/summarise")
async def summarise(transcript_id: str):
    r = await tr_svc.summarise(transcript_id)
    if not r.get("ok"):
        raise HTTPException(400, r.get("reason", "summarisation failed"))
    return r


@router.get("/{transcript_id}/summary")
async def get_summary(transcript_id: str):
    s = await tr_svc.get_summary(transcript_id)
    if not s:
        raise HTTPException(404, "no summary yet")
    return s
