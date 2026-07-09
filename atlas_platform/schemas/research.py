"""
ATLAS Research Pipeline schemas.

These models capture research sources, extracted claims, reliability levels,
and project routing decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from atlas_platform.schemas.base import ConfidenceLevel, EvidenceLabel, LeadAI


class SourceType(str, Enum):
    PEER_REVIEWED_PAPER = "peer_reviewed_paper"
    PATENT = "patent"
    DATASHEET = "datasheet"
    STANDARD = "standard"
    GOVERNMENT_REPORT = "government_report"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    BOOK = "book"
    VIDEO = "video"
    ARTICLE = "article"
    FORUM = "forum"
    CONCEPT_ART = "concept_art"
    PRODUCT_PAGE = "product_page"
    OTHER = "other"


class ReliabilityLevel(str, Enum):
    LEVEL_1_STRONGEST = "level_1_strongest"
    LEVEL_2_TECHNICAL = "level_2_technical"
    LEVEL_3_INSPIRATION = "level_3_inspiration"
    LEVEL_4_WEAK_OR_UNSAFE = "level_4_weak_or_unsafe"


@dataclass
class ResearchClaim:
    claim_id: str
    source_id: str
    claim: str
    evidence_label: EvidenceLabel
    notes: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


@dataclass
class EvidenceSource:
    source_id: str
    title: str
    source_type: SourceType
    reliability_level: ReliabilityLevel
    connected_project_id: Optional[str] = None
    assigned_ai: List[LeadAI] = field(default_factory=list)
    author_or_organization: Optional[str] = None
    date: Optional[str] = None
    link_or_identifier: Optional[str] = None
    key_takeaway: Optional[str] = None
    claims: List[ResearchClaim] = field(default_factory=list)
    follow_up_research: List[str] = field(default_factory=list)
