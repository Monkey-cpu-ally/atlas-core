"""Repository contracts for ATLAS memory."""

from __future__ import annotations

from typing import Protocol

from .models import MemoryRecord


class MemoryRepository(Protocol):
    """Storage boundary for memory records."""

    def save(self, record: MemoryRecord) -> MemoryRecord:
        """Persist a memory record."""

    def list_all(self) -> list[dict[str, object]]:
        """Return all persisted memory records as dictionaries."""
