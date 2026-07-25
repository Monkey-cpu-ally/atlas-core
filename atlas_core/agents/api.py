from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .bus import AgentMessage, MessageKind
from .council import CouncilVerdict, CouncilVote
from .runtime import AgentTask
from .service import AgentOperatingService


class ProjectCreate(BaseModel):
    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class TaskCreate(BaseModel):
    task_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    description: str = ""
    dependencies: set[str] = set()


class MessageCreate(BaseModel):
    sender: str
    recipient: str
    kind: MessageKind
    subject: str
    body: str
    project_id: str | None = None


class VoteCreate(BaseModel):
    agent: str
    score: float = Field(ge=0, le=100)
    verdict: CouncilVerdict
    rationale: str = ""


class DecisionCreate(BaseModel):
    domain: str
    votes: list[VoteCreate]


class MemoryCreate(BaseModel):
    key: str
    value: Any
    author: str


def create_app(database_path: str | None = None) -> FastAPI:
    service = AgentOperatingService(database_path or os.getenv("ATLAS_AGENT_DB", "atlas_agents.db"))
    app = FastAPI(title="ATLAS Agent Operating System", version="0.2.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "system": "atlas-agents"}

    @app.post("/projects")
    def create_project(payload: ProjectCreate) -> dict[str, object]:
        try:
            project = service.create_project(payload.project_id, payload.name)
        except ValueError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return {"project_id": project.project_id, "name": project.name, "progress": project.progress}

    @app.get("/projects/{project_id}")
    def get_project(project_id: str) -> dict[str, object]:
        project = service.orchestrator.projects.get(project_id) or service.load_project(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return {
            "project_id": project.project_id,
            "name": project.name,
            "progress": project.progress,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "domain": task.domain,
                    "description": task.description,
                    "dependencies": sorted(task.dependencies),
                    "assignee": task.assignee,
                    "completed": task.completed,
                }
                for task in project.tasks.values()
            ],
        }

    @app.post("/projects/{project_id}/tasks")
    def add_task(project_id: str, payload: TaskCreate) -> dict[str, object]:
        try:
            task = service.add_task(
                project_id,
                AgentTask(
                    task_id=payload.task_id,
                    title=payload.title,
                    domain=payload.domain,
                    description=payload.description,
                    dependencies=set(payload.dependencies),
                ),
            )
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return {"task_id": task.task_id, "assignee": task.assignee, "completed": task.completed}

    @app.post("/projects/{project_id}/tasks/{task_id}/complete")
    def complete_task(project_id: str, task_id: str) -> dict[str, object]:
        try:
            task = service.complete_task(project_id, task_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        project = service.orchestrator.projects[project_id]
        return {"task_id": task.task_id, "completed": task.completed, "progress": project.progress}

    @app.post("/memory/global")
    def save_global_memory(payload: MemoryCreate) -> dict[str, object]:
        entry = service.remember_global(payload.key, payload.value, payload.author)
        return {"key": entry.key, "scope": entry.scope, "author": entry.author}

    @app.post("/messages")
    def publish_message(payload: MessageCreate) -> dict[str, object]:
        message = service.publish(
            AgentMessage(
                payload.sender,
                payload.recipient,
                payload.kind,
                payload.subject,
                payload.body,
                payload.project_id,
            )
        )
        return {"sender": message.sender, "recipient": message.recipient, "kind": message.kind.value}

    @app.get("/projects/{project_id}/messages")
    def project_messages(project_id: str) -> list[dict[str, object]]:
        return [
            {
                "sender": message.sender,
                "recipient": message.recipient,
                "kind": message.kind.value,
                "subject": message.subject,
                "body": message.body,
                "created_at": message.created_at,
            }
            for message in service.store.project_messages(project_id)
        ]

    @app.post("/projects/{project_id}/council-decisions")
    def council_decision(project_id: str, payload: DecisionCreate) -> dict[str, object]:
        votes = [
            CouncilVote(vote.agent, vote.score, vote.verdict, vote.rationale)
            for vote in payload.votes
        ]
        try:
            decision = service.decide(project_id, payload.domain, votes)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return {
            "domain": decision.domain,
            "score": decision.score,
            "verdict": decision.verdict.value,
            "weights": decision.weights,
        }

    return app


app = create_app()
