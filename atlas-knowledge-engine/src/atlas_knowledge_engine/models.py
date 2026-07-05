"""Knowledge models for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class EvidenceRating(str, Enum):
    A_LEVEL = "A-Level"
    B_LEVEL = "B-Level"
    C_LEVEL = "C-Level"
    D_LEVEL = "D-Level"
    F_LEVEL = "F-Level"


class KnowledgeStatus(str, Enum):
    UNKNOWN = "unknown"
    LEARNING = "learning"
    PARTIALLY_VERIFIED = "partially_verified"
    VERIFIED = "verified"
    TESTED = "tested"
    PROTOTYPE = "prototype"
    PROJECT_READY = "project_ready"
    ATLAS_ORIGINAL = "atlas_original"


@dataclass(slots=True)
class SourcePassport:
    """Traceability record for a source."""

    title: str
    source_type: str
    creator_or_organization: str
    primary_knowledge_bank: str
    related_knowledge_banks: list[str] = field(default_factory=list)
    country_or_region: str | None = None
    language: str = "English"
    evidence_rating: EvidenceRating = EvidenceRating.C_LEVEL
    trust_tier: str = "Tier C"
    status: str = "pending"
    license_notes: str = ""
    source_id: str = field(default_factory=lambda: f"SRC-{uuid4()}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class KnowledgeEntry:
    """A structured knowledge entry inside ATLAS."""

    title: str
    summary: str
    primary_knowledge_bank: str
    created_by: str
    related_knowledge_banks: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    known_facts: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    status: KnowledgeStatus = KnowledgeStatus.LEARNING
    confidence: float = 0.5
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
