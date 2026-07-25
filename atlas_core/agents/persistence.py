from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .bus import AgentMessage, MessageKind
from .council import CouncilVerdict, CouncilVote, WeightedDecision
from .memory import MemoryEntry
from .orchestrator import AtlasProject
from .runtime import AgentTask


class AgentStore:
    """SQLite persistence for ATLAS projects, tasks, memory, messages, and Council decisions."""

    def __init__(self, database_path: str | Path = "atlas_agents.db") -> None:
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS agent_projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS agent_tasks (
                    project_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    description TEXT NOT NULL,
                    dependencies_json TEXT NOT NULL,
                    assignee TEXT,
                    completed INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (project_id, task_id),
                    FOREIGN KEY (project_id) REFERENCES agent_projects(project_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS agent_memory (
                    memory_key TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    author TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (memory_key, scope)
                );

                CREATE TABLE IF NOT EXISTS council_messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    project_id TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS council_decisions (
                    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    domain TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    score REAL NOT NULL,
                    weights_json TEXT NOT NULL,
                    votes_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def save_project(self, project: AtlasProject) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO agent_projects(project_id, name) VALUES (?, ?)",
                (project.project_id, project.name),
            )
            for task in project.tasks.values():
                connection.execute(
                    """
                    INSERT OR REPLACE INTO agent_tasks(
                        project_id, task_id, title, domain, description,
                        dependencies_json, assignee, completed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project.project_id,
                        task.task_id,
                        task.title,
                        task.domain,
                        task.description,
                        json.dumps(sorted(task.dependencies)),
                        task.assignee,
                        int(task.completed),
                    ),
                )

    def load_project(self, project_id: str) -> AtlasProject | None:
        with self._connect() as connection:
            project_row = connection.execute(
                "SELECT project_id, name FROM agent_projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if project_row is None:
                return None
            project = AtlasProject(project_row["project_id"], project_row["name"])
            rows = connection.execute(
                "SELECT * FROM agent_tasks WHERE project_id = ? ORDER BY task_id",
                (project_id,),
            ).fetchall()
        for row in rows:
            task = AgentTask(
                task_id=row["task_id"],
                title=row["title"],
                domain=row["domain"],
                description=row["description"],
                dependencies=set(json.loads(row["dependencies_json"])),
                assignee=row["assignee"],
                completed=bool(row["completed"]),
            )
            project.tasks[task.task_id] = task
        return project

    def save_memory(self, entry: MemoryEntry) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO agent_memory(
                    memory_key, scope, value_json, author, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (entry.key, entry.scope, json.dumps(entry.value), entry.author, entry.created_at),
            )

    def load_memory(self, key: str, scope: str = "global") -> MemoryEntry | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM agent_memory WHERE memory_key = ? AND scope = ?",
                (key, scope),
            ).fetchone()
        if row is None:
            return None
        return MemoryEntry(
            key=row["memory_key"],
            value=json.loads(row["value_json"]),
            author=row["author"],
            scope=row["scope"],
            created_at=row["created_at"],
        )

    def save_message(self, message: AgentMessage) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO council_messages(
                    sender, recipient, kind, subject, body, project_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.sender,
                    message.recipient,
                    message.kind.value,
                    message.subject,
                    message.body,
                    message.project_id,
                    message.created_at,
                ),
            )
            return int(cursor.lastrowid)

    def project_messages(self, project_id: str) -> list[AgentMessage]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM council_messages WHERE project_id = ? ORDER BY message_id",
                (project_id,),
            ).fetchall()
        return [
            AgentMessage(
                sender=row["sender"],
                recipient=row["recipient"],
                kind=MessageKind(row["kind"]),
                subject=row["subject"],
                body=row["body"],
                project_id=row["project_id"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_decision(
        self,
        project_id: str | None,
        decision: WeightedDecision,
        votes: Iterable[CouncilVote],
    ) -> int:
        vote_payload = [
            {
                "agent": vote.agent,
                "score": vote.score,
                "verdict": vote.verdict.value,
                "rationale": vote.rationale,
            }
            for vote in votes
        ]
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO council_decisions(
                    project_id, domain, verdict, score, weights_json, votes_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    decision.domain,
                    decision.verdict.value,
                    decision.score,
                    json.dumps(decision.weights),
                    json.dumps(vote_payload),
                ),
            )
            return int(cursor.lastrowid)

    def latest_decision(self, project_id: str) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM council_decisions
                WHERE project_id = ? ORDER BY decision_id DESC LIMIT 1
                """,
                (project_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "project_id": row["project_id"],
            "domain": row["domain"],
            "verdict": CouncilVerdict(row["verdict"]),
            "score": row["score"],
            "weights": json.loads(row["weights_json"]),
            "votes": json.loads(row["votes_json"]),
        }
