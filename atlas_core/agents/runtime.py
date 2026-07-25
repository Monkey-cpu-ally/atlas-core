from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    REVIEWING = "reviewing"
    BLOCKED = "blocked"


@dataclass(slots=True)
class AgentTask:
    task_id: str
    title: str
    domain: str
    description: str = ""
    dependencies: set[str] = field(default_factory=set)
    assignee: str | None = None
    completed: bool = False


@dataclass(slots=True)
class AtlasAgent:
    name: str
    specialties: set[str]
    status: AgentStatus = AgentStatus.IDLE
    task_queue: list[AgentTask] = field(default_factory=list)
    completed_tasks: int = 0

    def can_handle(self, domain: str) -> bool:
        return domain.lower() in {item.lower() for item in self.specialties}

    def assign(self, task: AgentTask) -> None:
        task.assignee = self.name
        self.task_queue.append(task)
        if self.status is AgentStatus.IDLE:
            self.status = AgentStatus.WORKING

    def available_tasks(self, completed_ids: Iterable[str]) -> list[AgentTask]:
        completed = set(completed_ids)
        return [task for task in self.task_queue if not task.completed and task.dependencies <= completed]

    def complete(self, task_id: str) -> AgentTask:
        for task in self.task_queue:
            if task.task_id == task_id:
                task.completed = True
                self.completed_tasks += 1
                self.status = AgentStatus.IDLE if all(item.completed for item in self.task_queue) else AgentStatus.WORKING
                return task
        raise KeyError(f"Unknown task: {task_id}")


def default_agents() -> dict[str, AtlasAgent]:
    return {
        "Hermes": AtlasAgent("Hermes", {"engineering", "manufacturing", "materials", "software", "robotics"}),
        "Minerva": AtlasAgent("Minerva", {"design", "story", "culture", "history", "nature", "research"}),
        "Ajani": AtlasAgent("Ajani", {"business", "strategy", "finance", "operations", "risk"}),
    }
