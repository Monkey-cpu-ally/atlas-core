"""YouTube Channel Watchlists — Knowledge Bank Phase B.

A channel is a persistent reference (`youtube_channels`) that ATLAS
keeps an eye on. Each poll fetches the channel's public uploads RSS
feed (via `youtube_resolver.resolve_channel`) and surfaces NEW video
URLs into `worldwatch_updates` so the existing research orchestrator
can route them.

Transcripts themselves are NOT auto-fetched — Google cloud-IP blocks
make that unreliable — so the architect-driven manual transcript
ingest at `/api/youtube/ingest-transcript` remains the canonical path.
This module just removes the "which channels do I care about?" gap.
"""
from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

from services import memory_bank as mb
from services import youtube_resolver as yt_res

logger = logging.getLogger("atlas.youtube_channels")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _channels():   return _db()["youtube_channels"]
def _runs():       return _db()["youtube_channel_runs"]
def _ww_updates(): return _db()["worldwatch_updates"]
def _transcripts(): return _db()["youtube_transcripts_private"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


class YouTubeChannel(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    channel_url: str                             # canonical /channel/UC... or /@handle URL
    channel_id: Optional[str] = None             # resolved UC... id
    name: Optional[str] = None                   # human label
    uploads_rss_url: Optional[str] = None        # resolved
    subject_slug: Optional[str] = None           # from `subjects` taxonomy
    agent: str = "minerva"                       # which persona owns it
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True
    last_polled_at: Optional[str] = None
    last_video_published_at: Optional[str] = None
    new_videos_seen: int = 0
    poll_count: int = 0
    notes: Optional[str] = None
    registered_at: str = Field(default_factory=_now)


# --- Registry --------------------------------------------------------------
async def register(channel: YouTubeChannel) -> Dict[str, Any]:
    """Resolve the channel URL → ID + uploads RSS, then persist."""
    try:
        uc_id = await yt_res.resolve_channel_id(channel.channel_url)
        channel.channel_id = uc_id
        channel.uploads_rss_url = yt_res.RSS_URL_TEMPLATE.format(channel_id=uc_id)
        # Best-effort fetch channel title via 1-video probe
        try:
            videos = await yt_res.latest_video_urls(channel.channel_url, n=1)
            if videos and videos[0].get("channel_title"):
                channel.name = channel.name or videos[0]["channel_title"]
        except Exception:                       # noqa: BLE001
            pass
    except Exception as exc:                    # noqa: BLE001
        # Couldn't resolve right now (network / 403). Persist anyway so
        # the architect can fix the URL later — channel_id stays None.
        logger.warning("could not resolve %s: %s", channel.channel_url, exc)

    existing = await _channels().find_one({"channel_url": channel.channel_url})
    if existing:
        await _channels().update_one(
            {"_id": existing["_id"]},
            {"$set": channel.model_dump(exclude={"id", "registered_at"})},
        )
        return await _channels().find_one({"channel_url": channel.channel_url}, {"_id": 0})

    await _channels().insert_one(channel.model_dump().copy())
    return channel.model_dump()


async def list_channels(enabled_only: bool = True,
                        agent: Optional[str] = None) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if enabled_only:
        q["enabled"] = True
    if agent:
        q["agent"] = agent
    cur = _channels().find(q, {"_id": 0}).sort("name", 1)
    return [d async for d in cur]


async def get_channel(channel_id_or_url: str) -> Optional[Dict[str, Any]]:
    return await _channels().find_one(
        {"$or": [{"id": channel_id_or_url},
                 {"channel_url": channel_id_or_url},
                 {"channel_id": channel_id_or_url}]},
        {"_id": 0},
    )


async def delete_channel(channel_id: str) -> int:
    r = await _channels().delete_one({"id": channel_id})
    return r.deleted_count


# --- Polling ---------------------------------------------------------------
async def poll_channel(channel_id: str) -> Dict[str, Any]:
    """Fetch the channel's latest videos and surface new ones into
    `worldwatch_updates`. Returns a per-run proof envelope."""
    ch = await get_channel(channel_id)
    if not ch:
        return {"ok": False, "reason": "channel not found"}

    # Use the resolver's purpose-built video lister — it handles the
    # YouTube Atom feed schema (different from generic RSS).
    try:
        videos = await yt_res.latest_video_urls(ch["channel_url"], n=25)
    except Exception as exc:                    # noqa: BLE001
        return {"ok": False, "reason": f"latest_video_urls failed: {exc}"}

    # If we couldn't capture the channel_id at register time, do it now
    if not ch.get("channel_id") and videos and videos[0].get("channel_id"):
        await _channels().update_one(
            {"id": ch["id"]},
            {"$set": {"channel_id": videos[0]["channel_id"],
                      "uploads_rss_url": yt_res.RSS_URL_TEMPLATE.format(
                          channel_id=videos[0]["channel_id"]),
                      "name": ch.get("name") or videos[0].get("channel_title")}},
        )

    run_id = uuid4().hex
    started = _now()
    new_video_urls: List[str] = []
    for video in videos:
        url = video.get("url") or ""
        if not url:
            continue
        # Have we surfaced this video before?
        seen = await _ww_updates().find_one(
            {"url": url, "source_type": "youtube_channel"},
            {"_id": 1},
        )
        if seen:
            continue
        upd_id = uuid4().hex
        await _ww_updates().insert_one({
            "id": upd_id,
            "entry_hash": _hash(url),
            "domain": ch.get("subject_slug") or "youtube",
            "agent": ch.get("agent", "minerva"),
            "feed_label": ch.get("name") or video.get("channel_title") or ch.get("channel_url"),
            "feed_id": ch["id"],
            "source_type": "youtube_channel",
            "title": video.get("title") or "",
            "url": url,
            "published": video.get("published") or "",
            "summary_excerpt": (
                f"YouTube video · {video.get('author') or ch.get('name', '')} · "
                f"published {video.get('published','')[:10]}"
            )[:600],
            "what_changed": {
                "one_line": f"New video from {ch.get('name') or ch['channel_url']}",
                "bullets": [video.get("title") or ""],
            },
            "knowledge_id": None,
            "memory_bank_id": None,
            "captured_at": _now(),
        })
        new_video_urls.append(url)

    proof = {
        "run_id": run_id,
        "channel_id": ch["id"],
        "started_at": started,
        "ended_at": _now(),
        "entries_seen": len(videos),
        "new_videos": len(new_video_urls),
        "new_video_urls": new_video_urls[:10],
    }
    await _runs().insert_one(proof.copy())
    last_pub = videos[0].get("published") if videos else ch.get("last_video_published_at")
    await _channels().update_one(
        {"id": ch["id"]},
        {"$set": {"last_polled_at": _now(),
                  "last_video_published_at": last_pub},
         "$inc": {"poll_count": 1,
                  "new_videos_seen": len(new_video_urls)}},
    )
    if new_video_urls:
        try:
            await mb.auto_store(
                f"YOUTUBE CHANNEL POLL · {ch.get('name') or ch['channel_url']} · "
                f"+{len(new_video_urls)} new videos",
                persona=ch.get("agent", "minerva"),
                category="research",
                source_type="youtube_channel_poll",
                source_id=ch["id"],
                tags=["youtube", "channel_poll",
                      f"subject:{ch.get('subject_slug')}" if ch.get('subject_slug') else "subject:none"],
            )
        except Exception as exc:                # noqa: BLE001
            logger.warning("MB write for channel poll failed: %s", exc)
    return {"ok": True, **proof}


async def poll_all(limit: int = 50) -> Dict[str, Any]:
    enabled = await list_channels(enabled_only=True)
    enabled = enabled[:limit]
    per_channel: List[Dict[str, Any]] = []
    total_new = 0
    for ch in enabled:
        r = await poll_channel(ch["id"])
        per_channel.append({"channel_id": ch["id"],
                            "name": ch.get("name") or ch["channel_url"],
                            "ok": r.get("ok", False),
                            "new_videos": r.get("new_videos", 0),
                            "reason": r.get("reason")})
        if r.get("ok"):
            total_new += r.get("new_videos", 0)
    return {"channels_polled": len(enabled),
            "total_new_videos": total_new,
            "per_channel": per_channel}


async def list_runs(channel_id: Optional[str] = None,
                    limit: int = 30) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if channel_id:
        q["channel_id"] = channel_id
    cur = _runs().find(q, {"_id": 0}).sort("started_at", -1).limit(limit)
    return [d async for d in cur]


async def stats() -> Dict[str, Any]:
    total_channels = await _channels().count_documents({})
    enabled = await _channels().count_documents({"enabled": True})
    total_new = 0
    cur = _channels().find({}, {"new_videos_seen": 1})
    async for c in cur:
        total_new += int(c.get("new_videos_seen") or 0)
    total_transcripts = await _transcripts().count_documents({})
    return {
        "channels_total": total_channels,
        "channels_enabled": enabled,
        "total_new_videos_seen_lifetime": total_new,
        "transcripts_ingested": total_transcripts,
    }
