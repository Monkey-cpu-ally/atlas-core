"""SQLite persistence for ATLAS Innovation Lab projects."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Union

from atlas_platform.schemas.base import AtlasProject, LeadAI, ProjectStatus


class SQLiteProjectRepository:
    """Persist AtlasProject records using Python's built-in SQLite driver."""

    def __init__(self, database: Union[str, Path]) -> None:
        self.database = str(database)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS innovation_projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    lead_ai TEXT NOT NULL,
                    status TEXT NOT NULL,
                    intended_user TEXT,
                    operating_environment TEXT,
                    council_decision TEXT,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                )
                """
            )

    def save(self, project: AtlasProject) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO innovation_projects (
                    project_id, name, category, purpose, lead_ai, status,
                    intended_user, operating_environment, council_decision,
                    tags_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    name=excluded.name,
                    category=excluded.category,
                    purpose=excluded.purpose,
                    lead_ai=excluded.lead_ai,
                    status=excluded.status,
                    intended_user=excluded.intended_user,
                    operating_environment=excluded.operating_environment,
                    council_decision=excluded.council_decision,
                    tags_json=excluded.tags_json,
                    metadata_json=excluded.metadata_json
                """,
                (
                    project.project_id,
                    project.name,
                    project.category,
                    project.purpose,
                    project.lead_ai.value,
                    project.status.value,
                    project.intended_user,
                    project.operating_environment,
                    project.council_decision,
                    json.dumps(project.tags, sort_keys=True),
                    json.dumps(project.metadata, sort_keys=True),
                ),
            )

    def get(self, project_id: str) -> Optional[AtlasProject]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM innovation_projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return self._from_row(row) if row else None

    def list(self, *, status: Optional[ProjectStatus] = None) -> Iterable[AtlasProject]:
        with self._connect() as connection:
            if status is None:
                rows = connection.execute(
                    "SELECT * FROM innovation_projects ORDER BY name, project_id"
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM innovation_projects WHERE status = ? ORDER BY name, project_id",
                    (status.value,),
                ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> AtlasProject:
        return AtlasProject(
            project_id=row["project_id"],
            name=row["name"],
            category=row["category"],
            purpose=row["purpose"],
            lead_ai=LeadAI(row["lead_ai"]),
            status=ProjectStatus(row["status"]),
            intended_user=row["intended_user"],
            operating_environment=row["operating_environment"],
            council_decision=row["council_decision"],
            tags=json.loads(row["tags_json"]),
            metadata=json.loads(row["metadata_json"]),
        )
