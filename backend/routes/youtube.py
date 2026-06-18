"""
YouTube routes (prefix /api/youtube).

GET   /api/youtube/resolve-channel?url=...&n=3
        Resolve a channel URL (any form: /channel/UC*, /user/X, /c/X, /@h)
        into its latest n videos via the public Atom RSS feed.

POST  /api/youtube/ingest-transcript
        Accept a user-supplied transcript and walk the full
        KB → MB → Graph → Lesson chain. Sidesteps the cloud-IP block.
        Body: {video_url, transcript_text, video_title?, channel_name?,
               channel_url?, generate_lesson?, force_agent?}

GET   /api/youtube/dashboard
        Live verification dashboard — counts every YouTube-side artefact
        in the database. Honest verdict at the top:
            "🔴 Not Verified" until ≥1 MANUAL_PROVIDED + ≥1 lesson.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, HttpUrl

from services import youtube_pipeline as yp
from services.youtube_resolver import ResolverError

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])


# --- 1. Channel RSS resolver -----------------------------------------------
@router.get("/resolve-channel")
async def resolve_channel(
    url: str = Query(..., description="YouTube channel URL (any form)"),
    n: int = Query(3, ge=1, le=15),
):
    try:
        return await yp.resolve_channel(url, n=n)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except ResolverError as exc:
        raise HTTPException(502, str(exc)) from exc


# --- 2. Manual transcript ingest -------------------------------------------
class ManualTranscriptReq(BaseModel):
    video_url: HttpUrl
    transcript_text: str = Field(..., min_length=40)
    video_title: Optional[str] = None
    channel_name: Optional[str] = None
    channel_url: Optional[str] = None
    generate_lesson: bool = True
    force_agent: Optional[str] = None


@router.post("/ingest-transcript")
async def ingest_transcript(req: ManualTranscriptReq) -> Dict[str, Any]:
    try:
        return await yp.ingest_manual_transcript(
            video_url=str(req.video_url),
            transcript_text=req.transcript_text,
            video_title=req.video_title,
            channel_name=req.channel_name,
            channel_url=req.channel_url,
            generate_lesson=req.generate_lesson,
            force_agent=req.force_agent,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


# --- 3. Verification dashboard ---------------------------------------------
@router.get("/dashboard")
async def dashboard():
    return await yp.dashboard()
