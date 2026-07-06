"""Repository contracts for ATLAS events."""

from __future__ import annotations

from typing import Protocol

from .models import AtlasEvent


class EventRepository(Protocol):
    """Storage boundary for event records."""

    def save(self, event: AtlasEvent) -> AtlasEvent:
        """Persist an event record."""

    def list_all(self) -> list[dict[str, object]]:
        """Return all persisted event records as dictionaries."""
