"""
ATLAS Graph Memory schemas.

Graph Memory stores relationships between projects, concepts, sources,
risks, materials, components, AI roles, skills, domains, and decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from atlas_platform.schemas.base import ConfidenceLevel


class GraphNodeType(str, Enum):
    PROJECT = "project"
    CONCEPT = "concept"
    COMPONENT = "component"
    MATERIAL = "material"
    SOURCE = "source"
    RISK = "risk"
    AI = "ai"
    DECISION = "decision"
    SKILL = "skill"
    DOMAIN = "domain"


class GraphRelationship(str, Enum):
    PROJECT_USES_COMPONENT = "PROJECT_USES_COMPONENT"
    PROJECT_USES_MATERIAL = "PROJECT_USES_MATERIAL"
    PROJECT_HAS_RISK = "PROJECT_HAS_RISK"
    PROJECT_SUPPORTED_BY_SOURCE = "PROJECT_SUPPORTED_BY_SOURCE"
    PROJECT_OWNED_BY_AI = "PROJECT_OWNED_BY_AI"
    PROJECT_BELONGS_TO_DOMAIN = "PROJECT_BELONGS_TO_DOMAIN"
    PROJECT_DEPENDS_ON_SKILL = "PROJECT_DEPENDS_ON_SKILL"
    PROJECT_CONNECTS_TO_PROJECT = "PROJECT_CONNECTS_TO_PROJECT"
    CONCEPT_PART_OF_PROJECT = "CONCEPT_PART_OF_PROJECT"
    SOURCE_SUPPORTS_CLAIM = "SOURCE_SUPPORTS_CLAIM"
    SOURCE_CONTRADICTS_CLAIM = "SOURCE_CONTRADICTS_CLAIM"
    RISK_MITIGATED_BY = "RISK_MITIGATED_BY"
    AI_RESPONSIBLE_FOR_DOMAIN = "AI_RESPONSIBLE_FOR_DOMAIN"
    DECISION_APPLIES_TO_PROJECT = "DECISION_APPLIES_TO_PROJECT"


@dataclass
class GraphNode:
    node_id: str
    node_type: GraphNodeType
    name: str
    summary: str
    status: str = "active"
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    tags: List[str] = field(default_factory=list)


@dataclass
class GraphEdge:
    edge_id: str
    from_node: str
    to_node: str
    relationship: GraphRelationship
    summary: str
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    evidence: List[str] = field(default_factory=list)
