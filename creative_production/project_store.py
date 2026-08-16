"""SQLite-backed immutable revision store for ATLAS creative productions."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ProjectRevision:
    project: str
    version: int
    created_at: str
    parent_version: Optional[int]
    message: str
    payload: Dict[str, Any]
    content_hash: str


class CreativeProjectStore:
    """Persists append-only project snapshots; old revisions are never overwritten."""

    def __init__(self, database: str = ":memory:") -> None:
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS creative_project_revisions (
                project TEXT NOT NULL,
                version INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                parent_version INTEGER,
                message TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                PRIMARY KEY (project, version)
            )
        """)
        self.connection.commit()

    @staticmethod
    def _encode(payload: Dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)

    def save_revision(self, *, project: str, payload: Dict[str, Any], message: str) -> ProjectRevision:
        latest = self.latest(project)
        version = 1 if latest is None else latest.version + 1
        parent_version = None if latest is None else latest.version
        encoded = self._encode(payload)
        content_hash = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        created_at = datetime.now(timezone.utc).isoformat()
        self.connection.execute(
            "INSERT INTO creative_project_revisions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (project, version, created_at, parent_version, message, encoded, content_hash),
        )
        self.connection.commit()
        return ProjectRevision(project, version, created_at, parent_version, message, payload, content_hash)

    def get(self, project: str, version: int) -> Optional[ProjectRevision]:
        row = self.connection.execute(
            "SELECT * FROM creative_project_revisions WHERE project=? AND version=?", (project, version)
        ).fetchone()
        return self._row(row) if row else None

    def latest(self, project: str) -> Optional[ProjectRevision]:
        row = self.connection.execute(
            "SELECT * FROM creative_project_revisions WHERE project=? ORDER BY version DESC LIMIT 1", (project,)
        ).fetchone()
        return self._row(row) if row else None

    def history(self, project: str) -> List[ProjectRevision]:
        rows = self.connection.execute(
            "SELECT * FROM creative_project_revisions WHERE project=? ORDER BY version", (project,)
        ).fetchall()
        return [self._row(row) for row in rows]

    def compare(self, *, project: str, from_version: int, to_version: int) -> Dict[str, Dict[str, Any]]:
        before = self.get(project, from_version)
        after = self.get(project, to_version)
        if before is None or after is None:
            raise KeyError(f"unknown revision comparison: {project} v{from_version}->v{to_version}")
        keys = sorted(set(before.payload) | set(after.payload))
        return {
            key: {"before": before.payload.get(key), "after": after.payload.get(key)}
            for key in keys
            if before.payload.get(key) != after.payload.get(key)
        }

    def restore(self, *, project: str, version: int, message: str = "restore prior revision") -> ProjectRevision:
        source = self.get(project, version)
        if source is None:
            raise KeyError(f"unknown revision: {project} v{version}")
        return self.save_revision(project=project, payload=source.payload, message=message)

    @staticmethod
    def _row(row: sqlite3.Row) -> ProjectRevision:
        return ProjectRevision(
            project=row["project"], version=row["version"], created_at=row["created_at"],
            parent_version=row["parent_version"], message=row["message"],
            payload=json.loads(row["payload_json"]), content_hash=row["content_hash"],
        )
