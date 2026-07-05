"""Memory models for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class MemoryType(str, Enum):
    CONVERSATION = "conversation_memory"
    USER = "user_memory"
    PROJECT = "project_memory"
    KNOWLEDGE = "knowledge_memory"
    RESEARCH = "research_memory"
    ENGINEERING = "engineering_memory"
    SOURCE = "source_memory"
    COUNCIL = "council_memory"
    ARCHIVE = "archive_memory"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    ARCHIVED = "archived"


@dataclass(slots=True)
class MemoryRecord:
    """A persistent record in ATLAS memory."""

    title: str
    memory_type: MemoryType
    summary: str
    content: str
    created_by: str
    confidence: float = 0.5
    related_projects: list[str] = field(default_factory=list)
    related_knowledge_banks: list[str] = field(default_factory=list)
    related_sources: list[str] = field(default_factory=list)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    visibility: str = "private"
    status: MemoryStatus = MemoryStatus.ACTIVE
    memory_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
