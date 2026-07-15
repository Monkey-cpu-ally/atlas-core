"""Core knowledge-graph models for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class GraphNode:
    """A typed knowledge entity stored in the ATLAS graph."""

    node_type: str
    name: str
    description: str = ""
    node_id: str = field(default_factory=lambda: str(uuid4()))
    aliases: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self) -> None:
        if not self.node_type.strip():
            raise ValueError("node_type cannot be empty")
        if not self.name.strip():
            raise ValueError("node name cannot be empty")


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """A directed relationship between two graph nodes."""

    source_id: str
    target_id: str
    relation: str
    edge_id: str = field(default_factory=lambda: str(uuid4()))
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.target_id.strip():
            raise ValueError("source_id and target_id are required")
        if self.source_id == self.target_id:
            raise ValueError("self-referencing graph edges are not allowed")
        if not self.relation.strip():
            raise ValueError("edge relation cannot be empty")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("edge weight must be between 0.0 and 1.0")
