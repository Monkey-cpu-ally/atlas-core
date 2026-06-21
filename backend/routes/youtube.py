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



# --- 4. Channel watchlist (Knowledge Bank Phase B) -------------------------
from services import youtube_channels as ytc


class RegisterChannelReq(BaseModel):
    channel_url: str
    name: Optional[str] = None
    subject_slug: Optional[str] = None
    agent: str = "minerva"
    tags: list = Field(default_factory=list)
    enabled: bool = True
    notes: Optional[str] = None


@router.post("/channels")
async def register_channel(req: RegisterChannelReq):
    return await ytc.register(ytc.YouTubeChannel(**req.model_dump()))


@router.get("/channels")
async def list_channels(enabled_only: bool = True,
                        agent: Optional[str] = None):
    items = await ytc.list_channels(enabled_only=enabled_only, agent=agent)
    return {"count": len(items), "items": items}


@router.get("/channels/stats")
async def channels_stats():
    return await ytc.stats()


@router.get("/channels/{channel_id}")
async def get_channel(channel_id: str):
    doc = await ytc.get_channel(channel_id)
    if not doc:
        raise HTTPException(404, "channel not found")
    return doc


@router.delete("/channels/{channel_id}")
async def delete_channel(channel_id: str):
    n = await ytc.delete_channel(channel_id)
    if not n:
        raise HTTPException(404, "channel not found")
    return {"deleted": n}


@router.post("/channels/{channel_id}/poll")
async def poll_channel(channel_id: str):
    return await ytc.poll_channel(channel_id)


@router.post("/channels/poll-all")
async def poll_all(limit: int = Query(50, ge=1, le=200)):
    return await ytc.poll_all(limit=limit)


@router.get("/channels/{channel_id}/runs")
async def channel_runs(channel_id: str, limit: int = Query(30, ge=1, le=100)):
    items = await ytc.list_runs(channel_id=channel_id, limit=limit)
    return {"count": len(items), "items": items}
