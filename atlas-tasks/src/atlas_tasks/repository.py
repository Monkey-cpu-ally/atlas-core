"""Repository contracts for ATLAS tasks."""

from __future__ import annotations

from typing import Protocol

from .models import AtlasTask


class TaskRepository(Protocol):
    """Storage boundary for task records."""

    def save(self, task: AtlasTask) -> AtlasTask:
        """Persist a task record."""

    def list_all(self) -> list[dict[str, object]]:
        """Return all persisted task records as dictionaries."""
