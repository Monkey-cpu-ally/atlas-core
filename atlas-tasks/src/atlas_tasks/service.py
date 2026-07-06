"""Task service for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from atlas_core_runtime.service import HealthReport, ServiceStatus
except ImportError:
    HealthReport = object  # type: ignore
    ServiceStatus = None  # type: ignore

from .models import AtlasTask, TaskStatus
from .repository import TaskRepository


@dataclass
class TaskService:
    """Stores ATLAS tasks in memory and optionally persists them."""

    repository: TaskRepository | None = None
    name: str = "atlas-tasks"
    version: str = "0.1.0"
    _tasks: dict[str, AtlasTask] = field(default_factory=dict)
    _running: bool = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def create_task(self, task: AtlasTask) -> AtlasTask:
        if task.task_id in self._tasks:
            raise ValueError(f"Task already exists: {task.task_id}")
        self._tasks[task.task_id] = task
        if self.repository is not None:
            self.repository.save(task)
        return task

    def get_task(self, task_id: str) -> AtlasTask:
        return self._tasks[task_id]

    def list_tasks(self, status: TaskStatus | None = None) -> list[AtlasTask]:
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        return tasks

    def update_status(self, task_id: str, status: TaskStatus) -> AtlasTask:
        task = self.get_task(task_id)
        task.status = status
        self._tasks[task_id] = task
        if self.repository is not None:
            self.repository.save(task)
        return task

    def persisted_tasks(self) -> list[dict[str, object]]:
        if self.repository is None:
            return []
        return self.repository.list_all()

    def health_check(self):
        if ServiceStatus is None:
            return {"service_name": self.name, "status": "healthy" if self._running else "offline"}
        persistence = "persistent" if self.repository is not None else "in-memory only"
        return HealthReport(
            service_name=self.name,
            status=ServiceStatus.HEALTHY if self._running else ServiceStatus.OFFLINE,
            message=f"{len(self._tasks)} tasks stored; mode={persistence}",
        )
