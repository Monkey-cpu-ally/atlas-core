"""Memory layer — minimal in-memory store with a clean interface for a
future persistent backend (MongoDB / Postgres).

Three things are stored:

  • conversations  — list of {role, content, ts} per session_id
  • archive        — list of dicts (from `archive_engine.parser.ArchiveEntry`)
  • events         — append-only audit log (shield rejections, council
                     decisions, etc.)

Everything goes through `sanitize_text()` from the shield before storage so
no prompt-injection attempt survives across sessions.
"""
from __future__ import annotations

import threading
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional

from ..shield_core.shield import sanitize_text


_lock = threading.Lock()


class Memory:
    """Thread-safe in-memory store. Swap with a DB-backed impl later."""

    def __init__(self, conversation_cap: int = 200, event_cap: int = 1000):
        self._conversations: Dict[str, Deque[dict]] = defaultdict(
            lambda: deque(maxlen=conversation_cap)
        )
        self._archive: List[dict] = []
        self._events: Deque[dict] = deque(maxlen=event_cap)

    # ------------------------------------------------------------ conversations
    def append_message(self, session_id: str, role: str, content: str) -> dict:
        record = {
            "role": role,
            "content": sanitize_text(content),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            self._conversations[session_id].append(record)
        return record

    def get_history(self, session_id: str) -> List[dict]:
        with _lock:
            return list(self._conversations.get(session_id, ()))

    def clear_session(self, session_id: str) -> None:
        with _lock:
            self._conversations.pop(session_id, None)

    # ------------------------------------------------------------ archive
    def add_archive_entry(self, entry: dict) -> None:
        with _lock:
            self._archive.append(entry)

    def list_archive(self, core: Optional[str] = None) -> List[dict]:
        with _lock:
            entries = list(self._archive)
        if core:
            return [e for e in entries if e.get("classified_core") == core]
        return entries

    # ------------------------------------------------------------ events
    def log_event(self, kind: str, payload: dict) -> None:
        with _lock:
            self._events.append({
                "kind": kind,
                "payload": payload,
                "ts": datetime.now(timezone.utc).isoformat(),
            })

    def recent_events(self, limit: int = 50) -> List[dict]:
        with _lock:
            return list(self._events)[-limit:]


# Module-level singleton — simple, sufficient for v1.
memory = Memory()
