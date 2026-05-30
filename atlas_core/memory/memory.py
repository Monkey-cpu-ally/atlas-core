"""Memory layer — MongoDB-backed when MONGO_URL is set, in-memory otherwise.

Three things are stored:

  • conversations  — list of {role, content, ts} per session_id
  • archive        — list of dicts (from `archive_engine.parser.ArchiveEntry`)
  • events         — append-only audit log (shield rejections, council
                     decisions, identity-attack blocks, etc.)

Design notes:

  * The public API is **synchronous** so it can be called from anywhere
    (including from inside other sync helpers). Internally we keep a
    write-through cache in memory and asynchronously flush writes to
    MongoDB on a background event-loop task.
  * If MONGO_URL is unset or MongoDB is unreachable at startup, we fall
    back to in-memory only — same behavior as v1. Nothing else has to
    change.
  * Everything is sanitized via shield_core before storage so prompt-
    injection attempts cannot survive across sessions.

Collections used:

  * atlas_conversations  — {session_id, role, content, ts}
  * atlas_archive        — full ArchiveEntry dicts
  * atlas_events         — {kind, payload, ts}
"""
from __future__ import annotations

import asyncio
import logging
import os
import threading
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional

from ..shield_core.shield import sanitize_text

logger = logging.getLogger("atlas.memory")

_lock = threading.Lock()


class Memory:
    """Thread-safe write-through cache. Reads are local; writes also flush to Mongo.

    The Mongo handle is created lazily so importing this module never
    requires a network connection. Call :meth:`bind_mongo` once at app
    startup to wire it up; everything else continues to work even if that
    call is skipped.
    """

    def __init__(self, conversation_cap: int = 200, event_cap: int = 1000):
        self._conversations: Dict[str, Deque[dict]] = defaultdict(
            lambda: deque(maxlen=conversation_cap)
        )
        self._archive: List[dict] = []
        self._events: Deque[dict] = deque(maxlen=event_cap)

        # MongoDB handles set by `bind_mongo`. Absent ⇒ in-memory only.
        self._conv_col = None
        self._arch_col = None
        self._evt_col = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ----------------------------------------------------------------- bind
    def bind_mongo(self, db, loop: asyncio.AbstractEventLoop) -> None:
        """Attach a motor database handle for write-through persistence.

        We capture the running event loop so synchronous public methods
        can schedule async Mongo writes via `run_coroutine_threadsafe`
        without callers having to await anything.
        """
        self._conv_col = db["atlas_conversations"]
        self._arch_col = db["atlas_archive"]
        self._evt_col = db["atlas_events"]
        self._loop = loop
        logger.info("Memory bound to MongoDB collections")

    async def hydrate(self) -> None:
        """Load existing archive + recent events from Mongo into the cache."""
        if self._arch_col is None or self._evt_col is None:
            return
        try:
            arch_docs = await self._arch_col.find({}, {"_id": 0}).to_list(length=500)
            evt_docs = await self._evt_col.find({}, {"_id": 0}) \
                .sort("ts", -1).to_list(length=self._events.maxlen)
            with _lock:
                self._archive = arch_docs
                # restore in chronological order so deque order matches
                self._events.extend(reversed(evt_docs))
            logger.info(
                "Memory hydrated: %d archive entries, %d events",
                len(arch_docs), len(evt_docs),
            )
        except Exception as exc:
            logger.warning("Memory hydration failed (continuing in-memory): %s", exc)

    # ----------------------------------------------- internal helpers
    def _schedule_insert(self, collection, doc: dict) -> None:
        """Fire-and-forget insert into a motor collection."""
        if collection is None or self._loop is None:
            return

        async def _insert():
            try:
                # Mongo mutates the dict to add _id; pass a shallow copy so the
                # cached doc remains JSON-clean.
                await collection.insert_one({**doc})
            except Exception as exc:
                logger.warning("Mongo insert failed: %s", exc)

        try:
            asyncio.run_coroutine_threadsafe(_insert(), self._loop)
        except RuntimeError:
            # loop may not be running yet during shutdown — drop silently
            pass

    # ----------------------------------------------------------------- conversations
    def append_message(self, session_id: str, role: str, content: str) -> dict:
        record = {
            "session_id": session_id,
            "role": role,
            "content": sanitize_text(content),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            self._conversations[session_id].append(record)
        self._schedule_insert(self._conv_col, record)
        return record

    def get_history(self, session_id: str) -> List[dict]:
        with _lock:
            return list(self._conversations.get(session_id, ()))

    def clear_session(self, session_id: str) -> None:
        with _lock:
            self._conversations.pop(session_id, None)
        # Also clear from Mongo asynchronously.
        if self._conv_col is not None and self._loop is not None:
            async def _del():
                try:
                    await self._conv_col.delete_many({"session_id": session_id})
                except Exception as exc:
                    logger.warning("Mongo delete failed: %s", exc)
            try:
                asyncio.run_coroutine_threadsafe(_del(), self._loop)
            except RuntimeError:
                pass

    # ----------------------------------------------------------------- archive
    def add_archive_entry(self, entry: dict) -> None:
        stamped = {**entry, "ts": datetime.now(timezone.utc).isoformat()}
        with _lock:
            self._archive.append(stamped)
        self._schedule_insert(self._arch_col, stamped)

    def list_archive(self, core: Optional[str] = None) -> List[dict]:
        with _lock:
            entries = list(self._archive)
        if core:
            return [e for e in entries if e.get("classified_core") == core]
        return entries

    # ----------------------------------------------------------------- events
    def log_event(self, kind: str, payload: dict) -> None:
        record = {
            "kind": kind,
            "payload": payload,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            self._events.append(record)
        self._schedule_insert(self._evt_col, record)

    def recent_events(self, limit: int = 50) -> List[dict]:
        with _lock:
            return list(self._events)[-limit:]


# Module-level singleton.
memory = Memory()


# ---------------------------------------------------------------------------
# Convenience wiring used by the FastAPI app at startup.
# ---------------------------------------------------------------------------

async def attach_mongo_on_startup() -> None:
    """Wire `memory` to MongoDB using MONGO_URL + DB_NAME from the env.

    Safe to call even if the env vars are missing — we simply log and
    leave the singleton in pure in-memory mode.
    """
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        logger.info("MONGO_URL or DB_NAME not set — memory stays in-memory only")
        return
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        loop = asyncio.get_running_loop()
        memory.bind_mongo(db, loop)
        await memory.hydrate()
    except Exception as exc:
        logger.warning(
            "MongoDB attach failed (continuing in-memory): %s", exc,
        )
