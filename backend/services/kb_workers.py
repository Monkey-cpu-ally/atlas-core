"""Knowledge Bank maintenance workers.

Two long-lived tasks:

  1. `start_youtube_poll_worker(interval_s)`
     Runs `youtube_channels.poll_all()` every `interval_s` seconds.
     Idempotent (only one instance ever starts).

  2. `retire_legacy_knowledge()`
     One-shot migration: copy every row from the legacy `knowledge`
     collection into `knowledge_records` (with proper schema mapping)
     and delete the source rows. Idempotent by `source_url` — re-runs
     find no rows to migrate. Safe to call on every startup.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("atlas.kb_workers")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None
_youtube_worker_task: Optional[asyncio.Task] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Worker: YouTube poll-all -----------------------------------------------
async def _yt_poll_loop(interval_s: int) -> None:
    from services import youtube_channels as ytc
    logger.info("YT poll worker started · interval=%ss", interval_s)
    while True:
        try:
            await asyncio.sleep(interval_s)   # wait first, so restarts don't hammer
            result = await ytc.poll_all(limit=100)
            if result.get("total_new_videos"):
                logger.info(
                    "YT poll worker · %s channels polled · +%s videos",
                    result.get("channels_polled"), result.get("total_new_videos"),
                )
        except asyncio.CancelledError:
            logger.info("YT poll worker cancelled")
            raise
        except Exception as exc:                # noqa: BLE001
            logger.warning("YT poll worker iteration failed: %s", exc)


def start_youtube_poll_worker(interval_s: int = 3600) -> Optional[asyncio.Task]:
    """Idempotent. Second call is a no-op."""
    global _youtube_worker_task
    if _youtube_worker_task and not _youtube_worker_task.done():
        return _youtube_worker_task
    _youtube_worker_task = asyncio.create_task(_yt_poll_loop(interval_s))
    return _youtube_worker_task


# --- One-shot: retire legacy `knowledge` -> `knowledge_records` ------------
async def retire_legacy_knowledge() -> Dict[str, Any]:
    """Migrate rows from the legacy `knowledge` collection into
    `knowledge_records`. Idempotent by `source_url` — rows already
    present in `knowledge_records` are not duplicated.

    Legacy shape (from `services/knowledge_core.py`):
        id, title, topic, source, transcript, summary, ai_owner
    Target shape (from `models/knowledge_models.KnowledgeRecord`):
        id, title, summary, key_points, tags, source_type, source_url,
        source_hash, confidence_score, related_agents, concepts,
        memory_bank_id, created_at
    """
    db = _db()
    legacy = db["knowledge"]
    target = db["knowledge_records"]

    total = await legacy.count_documents({})
    if total == 0:
        return {"migrated": 0, "skipped": 0, "remaining": 0, "already_done": True}

    migrated = 0
    skipped = 0
    async for row in legacy.find({}):
        source_url = row.get("source") or ""
        source_hash = f"legacy_knowledge:{row.get('id') or row.get('_id')}"
        # Skip if already migrated (by source_hash or by matching url)
        already = await target.find_one(
            {"$or": [{"source_hash": source_hash},
                     {"source_url": source_url}]},
            {"_id": 1},
        )
        if already:
            # URL already exists in the modern collection — legacy row is
            # redundant, delete it so `knowledge` fully drains.
            await legacy.delete_one({"_id": row["_id"]})
            skipped += 1
            continue

        migrated_doc = {
            "id":              row.get("id") or uuid4().hex,
            "title":           (row.get("title") or "")[:280],
            "summary":         (row.get("summary") or "")[:1200],
            "key_points":      [],
            "tags":            ["legacy_import", f"topic:{row.get('topic', '?')}"],
            "source_type":     "youtube" if "youtube" in (source_url or "").lower() else "web",
            "source_url":      source_url,
            "source_hash":     source_hash,
            "concepts":        [],
            "confidence_score": 0.5,
            "related_agents":  [row.get("ai_owner") or "minerva"],
            "memory_bank_id":  None,
            "extra": {"legacy_transcript_excerpt":
                      (row.get("transcript") or "")[:4000],
                      "legacy_topic": row.get("topic")},
            "created_at":      _now(),
        }
        await target.insert_one(migrated_doc)
        await legacy.delete_one({"_id": row["_id"]})
        migrated += 1

    remaining = await legacy.count_documents({})
    logger.info("legacy `knowledge` retirement · migrated=%s skipped=%s remaining=%s",
                migrated, skipped, remaining)
    return {"migrated": migrated, "skipped": skipped, "remaining": remaining}
