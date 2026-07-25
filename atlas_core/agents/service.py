from __future__ import annotations

from pathlib import Path

from .bus import AgentMessage, CouncilBus
from .council import CouncilVote, WeightedCouncil, WeightedDecision
from .memory import AtlasMemory, MemoryEntry
from .orchestrator import AtlasProject, ProjectOrchestrator
from .persistence import AgentStore
from .runtime import AgentTask


class AgentOperatingService:
    """Coordinates runtime behavior with durable storage."""

    def __init__(self, database_path: str | Path = "atlas_agents.db") -> None:
        self.store = AgentStore(database_path)
        self.orchestrator = ProjectOrchestrator()
        self.memory = AtlasMemory()
        self.bus = CouncilBus()
        self.council = WeightedCouncil()

    def create_project(self, project_id: str, name: str) -> AtlasProject:
        project = self.orchestrator.create_project(project_id, name)
        self.store.save_project(project)
        return project

    def load_project(self, project_id: str) -> AtlasProject | None:
        project = self.store.load_project(project_id)
        if project is None:
            return None
        self.orchestrator.projects[project_id] = project
        for task in project.tasks.values():
            if task.assignee and task.assignee in self.orchestrator.agents:
                self.orchestrator.agents[task.assignee].task_queue.append(task)
        return project

    def add_task(self, project_id: str, task: AgentTask) -> AgentTask:
        if project_id not in self.orchestrator.projects:
            project = self.load_project(project_id)
            if project is None:
                raise KeyError(f"Unknown project: {project_id}")
        assigned = self.orchestrator.add_task(project_id, task)
        self.store.save_project(self.orchestrator.projects[project_id])
        return assigned

    def complete_task(self, project_id: str, task_id: str) -> AgentTask:
        if project_id not in self.orchestrator.projects:
            project = self.load_project(project_id)
            if project is None:
                raise KeyError(f"Unknown project: {project_id}")
        completed = self.orchestrator.complete_task(project_id, task_id)
        self.store.save_project(self.orchestrator.projects[project_id])
        return completed

    def remember_global(self, key: str, value: object, author: str) -> MemoryEntry:
        entry = self.memory.remember_global(key, value, author)
        self.store.save_memory(entry)
        return entry

    def remember_private(self, agent: str, key: str, value: object) -> MemoryEntry:
        entry = self.memory.remember_private(agent, key, value)
        self.store.save_memory(entry)
        return entry

    def publish(self, message: AgentMessage) -> AgentMessage:
        self.bus.publish(message)
        self.store.save_message(message)
        return message

    def decide(
        self,
        project_id: str,
        domain: str,
        votes: list[CouncilVote],
    ) -> WeightedDecision:
        decision = self.council.decide(domain, votes)
        self.store.save_decision(project_id, decision, votes)
        return decision
