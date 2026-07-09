"""Relationship models for the ATLAS Knowledge Division."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class KnowledgeNodeType(str, Enum):
    KNOWLEDGE_ENTRY = "knowledge_entry"
    SOURCE = "source"
    PROJECT = "project"
    KNOWLEDGE_BANK = "knowledge_bank"
    TECHNOLOGY = "technology"
    AGENT = "agent"
    TASK = "task"
    EVENT = "event"
    EXPERIMENT = "experiment"
    BLUEPRINT = "blueprint"


class KnowledgeRelationshipType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    INSPIRED_BY = "inspired_by"
    USED_BY = "used_by"
    REVIEWED_BY = "reviewed_by"
    BELONGS_TO = "belongs_to"
    UPDATES = "updates"
    DERIVED_FROM = "derived_from"
    APPLIES_TO = "applies_to"


@dataclass(slots=True)
class KnowledgeNode:
    """A node in the ATLAS knowledge relationship network."""

    title: str
    node_type: KnowledgeNodeType
    external_id: str | None = None
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    node_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class KnowledgeRelationship:
    """A directed relationship between two knowledge nodes."""

    from_node_id: str
    to_node_id: str
    relationship_type: KnowledgeRelationshipType
    reason: str
    confidence: float = 0.5
    evidence_source_ids: list[str] = field(default_factory=list)
    created_by: str = "atlas-knowledge-engine"
    relationship_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
