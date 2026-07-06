"""Repository contracts for ATLAS knowledge."""

from __future__ import annotations

from typing import Protocol

from .models import KnowledgeEntry, SourcePassport


class SourceRepository(Protocol):
    """Storage boundary for source passports."""

    def save(self, source: SourcePassport) -> SourcePassport:
        """Persist a source passport."""

    def list_all(self) -> list[dict[str, object]]:
        """Return all persisted source passports as dictionaries."""


class KnowledgeRepository(Protocol):
    """Storage boundary for knowledge entries."""

    def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Persist a knowledge entry."""

    def list_all(self) -> list[dict[str, object]]:
        """Return all persisted knowledge entries as dictionaries."""
