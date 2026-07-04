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


def _metadata_block(doc: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Pull the Knowledge Network metadata fields off a raw registry doc,
    falling back to per-registry defaults so every source has a full shape."""
    return {
        "country":           doc.get("country") or defaults.get("country"),
        "region":            doc.get("region")  or defaults.get("region"),
        "source_language":   doc.get("source_language") or defaults.get("source_language", "en"),
        "source_type":       doc.get("source_type") or defaults.get("source_type"),
        "trust_level":       doc.get("trust_level") or defaults.get("trust_level", "unverified"),
        "ai_owner":          doc.get("ai_owner") or doc.get("agent") or defaults.get("ai_owner"),
        "update_frequency":  doc.get("update_frequency") or defaults.get("update_frequency", "on_demand"),
        "access_method":     doc.get("access_method") or defaults.get("access_method", "public"),
        "auto_sync":         bool(doc.get("auto_sync", defaults.get("auto_sync", False))),
        "private_source":    bool(doc.get("private_source", defaults.get("private_source", False))),
        "culture_tag":       doc.get("culture_tag") or defaults.get("culture_tag"),
    }


# Unified row shape:
# {
#   id, kind ('rss'|'patent'|'web'|'git'|'youtube_channel'),
#   label, url, agent, subject_slug, tags, enabled,
#   last_polled_at, last_seen_count, registered_at,
#   stats: {runs, new_items_total, errors_total}
# }
def _shape_worldwatch(doc: Dict[str, Any]) -> Dict[str, Any]:
    kind = "patent" if doc.get("source_type") == "patent" else "rss"
    shaped = {
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
    shaped.update(_metadata_block(doc, {
        "source_type": kind,           # 'rss' | 'patent'
        "trust_level": "curated",       # worldwatch is architect-approved
        "update_frequency": "hourly",
    }))
    shaped["source_name"] = shaped["label"]
    shaped["last_sync"] = shaped["last_polled_at"]
    return shaped


def _shape_watcher(doc: Dict[str, Any]) -> Dict[str, Any]:
    shaped = {
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
    shaped.update(_metadata_block(doc, {
        "source_type": doc.get("kind") or "web",
        "trust_level": "curated",
        "update_frequency": "on_demand",
    }))
    shaped["source_name"] = shaped["label"]
    shaped["last_sync"] = shaped["last_polled_at"]
    return shaped


def _shape_youtube_channel(doc: Dict[str, Any]) -> Dict[str, Any]:
    shaped = {
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
    shaped.update(_metadata_block(doc, {
        "source_type": "video",
        "trust_level": "curated",
        "update_frequency": "hourly",
        "access_method": "public_rss",
    }))
    shaped["source_name"] = shaped["label"]
    shaped["last_sync"] = shaped["last_polled_at"]
    return shaped


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



# ---------------------------------------------------------------------------
# Knowledge Network — extended metadata management
# ---------------------------------------------------------------------------

# Only these keys are writable through the metadata patch endpoint. Keeping
# it a strict allow-list prevents callers from mutating identity fields
# (id, url) or bypassing the enable/disable business logic.
KN_METADATA_FIELDS = (
    "country",
    "region",
    "source_language",
    "source_type",
    "trust_level",
    "ai_owner",
    "update_frequency",
    "access_method",
    "auto_sync",
    "private_source",
    "culture_tag",
)

_KN_REGISTRIES = ("worldwatch_feeds", "watchers", "youtube_channels")


async def find_source(source_id: str) -> Optional[Dict[str, Any]]:
    """Locate a source by id across all three registries. Returns the
    shaped row (with metadata block) or None."""
    db = _db()
    for reg in _KN_REGISTRIES:
        raw = await db[reg].find_one({"id": source_id}, {"_id": 0})
        if raw:
            if reg == "worldwatch_feeds":
                return _shape_worldwatch(raw)
            if reg == "watchers":
                return _shape_watcher(raw)
            return _shape_youtube_channel(raw)
    return None


async def update_source_metadata(
    source_id: str,
    metadata: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Merge Knowledge Network metadata onto the source's underlying doc.

    Returns the newly shaped row, or None if the id was not found.
    Only keys in `KN_METADATA_FIELDS` are honoured.
    """
    clean = {k: v for k, v in metadata.items() if k in KN_METADATA_FIELDS}
    if not clean:
        return await find_source(source_id)
    db = _db()
    for reg in _KN_REGISTRIES:
        raw = await db[reg].find_one({"id": source_id})
        if raw:
            await db[reg].update_one({"id": source_id}, {"$set": clean})
            return await find_source(source_id)
    return None
