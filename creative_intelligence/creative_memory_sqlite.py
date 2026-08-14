"""SQLite-backed persistent Creative Memory for ATLAS."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .creative_memory import CreativeLesson


class SQLiteCreativeMemory:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS creative_lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL,
                    task TEXT NOT NULL,
                    references_json TEXT NOT NULL,
                    principle_attempted TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    critique TEXT NOT NULL,
                    revision TEXT NOT NULL,
                    lesson TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_creative_lessons_project ON creative_lessons(project)"
            )

    def remember(self, lesson: CreativeLesson) -> CreativeLesson:
        if not 0.0 <= lesson.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO creative_lessons (
                    project, task, references_json, principle_attempted, outcome,
                    critique, revision, lesson, confidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lesson.project,
                    lesson.task,
                    json.dumps(lesson.references),
                    lesson.principle_attempted,
                    lesson.outcome,
                    lesson.critique,
                    lesson.revision,
                    lesson.lesson,
                    lesson.confidence,
                    lesson.created_at,
                ),
            )
        return lesson

    def recall(self, project: str | None = None, term: str | None = None) -> list[CreativeLesson]:
        clauses: list[str] = []
        params: list[str] = []
        if project:
            clauses.append("lower(project) = lower(?)")
            params.append(project)
        if term:
            clauses.append(
                "lower(task || ' ' || principle_attempted || ' ' || outcome || ' ' || critique || ' ' || revision || ' ' || lesson) LIKE lower(?)"
            )
            params.append(f"%{term}%")
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        query = "SELECT * FROM creative_lessons" + where + " ORDER BY id ASC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            CreativeLesson(
                project=row["project"],
                task=row["task"],
                references=json.loads(row["references_json"]),
                principle_attempted=row["principle_attempted"],
                outcome=row["outcome"],
                critique=row["critique"],
                revision=row["revision"],
                lesson=row["lesson"],
                confidence=row["confidence"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
