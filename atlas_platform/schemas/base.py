"""
ATLAS shared base schemas.

These models define common vocabulary used across Innovation Lab,
Graph Memory, Digital Twin, Research Pipeline, and Prototype Manager.

The first implementation uses the Python standard library only.
Later, these can be upgraded to Pydantic models if the project needs
runtime validation, FastAPI integration, or schema generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ConfidenceLevel(str, Enum):
    """How certain ATLAS is about a record, estimate, or claim."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProjectStatus(str, Enum):
    """Lifecycle status for an ATLAS project."""

    INTAKE = "intake"
    DISCOVERY = "discovery"
    CONCEPT = "concept"
    DIGITAL_TWIN = "digital_twin"
    PROTOTYPE = "prototype"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class LeadAI(str, Enum):
    """Official ATLAS AI owners."""

    AJANI = "Ajani"
    MINERVA = "Minerva"
    HERMES = "Hermes"
    COUNCIL = "Council"


class EvidenceLabel(str, Enum):
    """Evidence classification used by the Research Pipeline."""

    PROVEN = "proven"
    STRONG_EVIDENCE = "strong_evidence"
    PROMISING_EVIDENCE = "promising_evidence"
    EARLY_RESEARCH = "early_research"
    PLAUSIBLE_ASSUMPTION = "plausible_assumption"
    SPECULATIVE = "speculative"
    UNSUPPORTED = "unsupported"
    UNSAFE_OR_REJECTED = "unsafe_or_rejected"


class RiskSeverity(str, Enum):
    """Risk impact level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLikelihood(str, Enum):
    """Risk probability level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AtlasProject:
    """Core project record shared across ATLAS systems."""

    project_id: str
    name: str
    category: str
    purpose: str
    lead_ai: LeadAI
    status: ProjectStatus = ProjectStatus.INTAKE
    intended_user: Optional[str] = None
    operating_environment: Optional[str] = None
    council_decision: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AtlasRisk:
    """Risk record used by Innovation Lab, Digital Twin, and Prototype Manager."""

    risk_id: str
    project_id: str
    risk_type: str
    description: str
    severity: RiskSeverity
    likelihood: RiskLikelihood
    mitigation: Optional[str] = None
    stop_condition: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


@dataclass
class CouncilDecision:
    """Decision made by Ajani, Minerva, Hermes, or the Council."""

    decision_id: str
    project_id: str
    decision: str
    reason: str
    made_by: LeadAI = LeadAI.COUNCIL
    next_action: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
