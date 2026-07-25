from __future__ import annotations

from dataclasses import dataclass, field

from .runtime import AgentTask, AtlasAgent, default_agents


@dataclass(slots=True)
class AtlasProject:
    project_id: str
    name: str
    tasks: dict[str, AgentTask] = field(default_factory=dict)

    @property
    def progress(self) -> float:
        if not self.tasks:
            return 0.0
        complete = sum(task.completed for task in self.tasks.values())
        return round(complete / len(self.tasks) * 100, 2)


class ProjectOrchestrator:
    def __init__(self, agents: dict[str, AtlasAgent] | None = None) -> None:
        self.agents = agents or default_agents()
        self.projects: dict[str, AtlasProject] = {}

    def create_project(self, project_id: str, name: str) -> AtlasProject:
        if project_id in self.projects:
            raise ValueError(f"Project already exists: {project_id}")
        project = AtlasProject(project_id, name)
        self.projects[project_id] = project
        return project

    def add_task(self, project_id: str, task: AgentTask) -> AgentTask:
        project = self.projects[project_id]
        if task.task_id in project.tasks:
            raise ValueError(f"Task already exists: {task.task_id}")
        project.tasks[task.task_id] = task
        self.assign_best_agent(task)
        return task

    def assign_best_agent(self, task: AgentTask) -> AtlasAgent:
        qualified = [agent for agent in self.agents.values() if agent.can_handle(task.domain)]
        if not qualified:
            raise ValueError(f"No agent specializes in domain: {task.domain}")
        agent = min(qualified, key=lambda item: (len([t for t in item.task_queue if not t.completed]), item.name))
        agent.assign(task)
        return agent

    def complete_task(self, project_id: str, task_id: str) -> AgentTask:
        task = self.projects[project_id].tasks[task_id]
        if any(not self.projects[project_id].tasks[dep].completed for dep in task.dependencies):
            raise RuntimeError(f"Task dependencies are incomplete: {task_id}")
        if task.assignee is None:
            raise RuntimeError(f"Task has no assignee: {task_id}")
        return self.agents[task.assignee].complete(task_id)

    def blocked_tasks(self, project_id: str) -> list[AgentTask]:
        project = self.projects[project_id]
        return [
            task for task in project.tasks.values()
            if not task.completed and any(not project.tasks[dep].completed for dep in task.dependencies)
        ]
