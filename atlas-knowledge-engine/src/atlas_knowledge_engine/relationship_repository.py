"""Repository contracts for ATLAS knowledge relationships."""

from __future__ import annotations

from typing import Protocol

from .relationships import KnowledgeNode, KnowledgeRelationship


class KnowledgeNodeRepository(Protocol):
    """Storage boundary for knowledge nodes."""

    def save(self, node: KnowledgeNode) -> KnowledgeNode:
        """Persist a knowledge node."""

    def list_all(self) -> list[dict[str, object]]:
        """Return all persisted nodes as dictionaries."""


class KnowledgeRelationshipRepository(Protocol):
    """Storage boundary for knowledge relationships."""

    def save(self, relationship: KnowledgeRelationship) -> KnowledgeRelationship:
        """Persist a relationship."""

    def list_all(self) -> list[dict[str, object]]:
        """Return all persisted relationships as dictionaries."""
