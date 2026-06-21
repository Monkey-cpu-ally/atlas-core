"""Research Sources — unified view (Knowledge Bank Phase C).

A READ-ONLY aggregator that gives the architect (and HUD) one consistent
shape over the three separate registries that ATLAS already maintains:

  - `worldwatch_feeds`            (RSS + patent)
  - `watchers`                    (web / git scrape targets)
  - `youtube_channels`            (uploads RSS — Phase B)

No new write path; mutations stay on each owner's existing endpoints
(/api/worldwatch/* /api/watchers/* /api/youtube/channels/*). This keeps
the source-of-truth contract clean: one registry per kind, one view to
read them all.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


# Unified row shape:
# {
#   id, kind ('rss'|'patent'|'web'|'git'|'youtube_channel'),
#   label, url, agent, subject_slug, tags, enabled,
#   last_polled_at, last_seen_count, registered_at,
#   stats: {runs, new_items_total, errors_total}
# }
def _shape_worldwatch(doc: Dict[str, Any]) -> Dict[str, Any]:
    kind = "patent" if doc.get("source_type") == "patent" else "rss"
    return {
        "id":              doc.get("id"),
        "kind":            kind,
        "label":           doc.get("label") or doc.get("url"),
        "url":             doc.get("url"),
        "agent":           doc.get("agent"),
        "subject_slug":    None,                    # worldwatch uses `domain`
        "domain":          doc.get("domain"),
        "tags":            [doc.get("domain") or ""],
        "enabled":         bool(doc.get("approved", True)),
        "last_polled_at":  doc.get("last_run_at"),
        "registered_at":   doc.get("registered_at"),
        "run_count":       int(doc.get("run_count") or 0),
        "registry":        "worldwatch_feeds",
    }


def _shape_watcher(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id":              doc.get("id"),
        "kind":            doc.get("kind") or "web",    # 'git' | 'web'
        "label":           doc.get("label") or doc.get("url"),
        "url":             doc.get("url"),
        "agent":           "ajani",                     # watchers default to engineering
        "subject_slug":    None,
        "domain":          None,
        "tags":            ["code_watcher"],
        "enabled":         (doc.get("status") or "active") == "active",
        "last_polled_at":  doc.get("last_run_at"),
        "registered_at":   doc.get("registered_at"),
        "run_count":       int(doc.get("run_count") or 0),
        "registry":        "watchers",
    }


def _shape_youtube_channel(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id":              doc.get("id"),
        "kind":            "youtube_channel",
        "label":           doc.get("name") or doc.get("channel_url"),
        "url":             doc.get("channel_url"),
        "agent":           doc.get("agent"),
        "subject_slug":    doc.get("subject_slug"),
        "domain":          "youtube",
        "tags":            doc.get("tags") or [],
        "enabled":         bool(doc.get("enabled", True)),
        "last_polled_at":  doc.get("last_polled_at"),
        "registered_at":   doc.get("registered_at"),
        "run_count":       int(doc.get("poll_count") or 0),
        "new_videos_seen": int(doc.get("new_videos_seen") or 0),
        "registry":        "youtube_channels",
    }


async def list_sources(
    kind: Optional[str] = None,
    agent: Optional[str] = None,
    enabled_only: bool = True,
) -> List[Dict[str, Any]]:
    db = _db()
    out: List[Dict[str, Any]] = []

    if kind in (None, "rss", "patent"):
        ww_q: Dict[str, Any] = {}
        if enabled_only:
            ww_q["approved"] = True
        if kind == "patent":
            ww_q["source_type"] = "patent"
        elif kind == "rss":
            ww_q["$or"] = [{"source_type": "rss"}, {"source_type": {"$exists": False}}]
        async for d in db["worldwatch_feeds"].find(ww_q, {"_id": 0}):
            shaped = _shape_worldwatch(d)
            if not agent or shaped["agent"] == agent:
                out.append(shaped)

    if kind in (None, "web", "git"):
        w_q: Dict[str, Any] = {}
        if enabled_only:
            w_q["status"] = "active"
        if kind in ("web", "git"):
            w_q["kind"] = kind
        async for d in db["watchers"].find(w_q, {"_id": 0}):
            shaped = _shape_watcher(d)
            if not agent or shaped["agent"] == agent:
                out.append(shaped)

    if kind in (None, "youtube_channel"):
        yt_q: Dict[str, Any] = {}
        if enabled_only:
            yt_q["enabled"] = True
        if agent:
            yt_q["agent"] = agent
        async for d in db["youtube_channels"].find(yt_q, {"_id": 0}):
            out.append(_shape_youtube_channel(d))

    # newest first
    out.sort(key=lambda r: (r.get("registered_at") or ""), reverse=True)
    return out


async def stats() -> Dict[str, Any]:
    """Counts per kind across all 3 registries."""
    db = _db()
    counts = {
        "rss": await db["worldwatch_feeds"].count_documents(
            {"$or": [{"source_type": "rss"},
                     {"source_type": {"$exists": False}}]}),
        "patent": await db["worldwatch_feeds"].count_documents({"source_type": "patent"}),
        "web": await db["watchers"].count_documents({"kind": "web"}),
        "git": await db["watchers"].count_documents({"kind": "git"}),
        "youtube_channel": await db["youtube_channels"].count_documents({}),
    }
    counts["total"] = sum(counts.values())
    return {"by_kind": counts}
