"""
ATLAS Prototype Manager schemas.

These models control prototype readiness, safety planning, test records,
bill of materials, and failure learning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from atlas_platform.schemas.base import ConfidenceLevel


class PrototypeStatus(str, Enum):
    PLANNED = "planned"
    APPROVED = "approved"
    TESTING = "testing"
    PASSED = "passed"
    FAILED = "failed"
    PAUSED = "paused"
    ARCHIVED = "archived"


class PrototypeLevel(int, Enum):
    PAPER = 0
    DIGITAL = 1
    BENCH = 2
    FUNCTIONAL = 3
    FIELD = 4
    PRODUCTION = 5


@dataclass
class BillOfMaterialsItem:
    item_id: str
    name: str
    quantity: int
    purpose: str
    estimated_cost_usd: Optional[float] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class PrototypeRecord:
    prototype_id: str
    project_id: str
    prototype_level: PrototypeLevel
    purpose: str
    status: PrototypeStatus = PrototypeStatus.PLANNED
    required_parts: List[BillOfMaterialsItem] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    safety_risks: List[str] = field(default_factory=list)
    safety_controls: List[str] = field(default_factory=list)
    stop_conditions: List[str] = field(default_factory=list)
    test_environment: Optional[str] = None
    pass_criteria: List[str] = field(default_factory=list)
    fail_criteria: List[str] = field(default_factory=list)
    data_to_record: List[str] = field(default_factory=list)
    council_decision: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


@dataclass
class FailureLog:
    failure_id: str
    project_id: str
    prototype_id: str
    objective: str
    expected_result: str
    actual_result: str
    failure_description: str
    root_cause_known: Optional[str] = None
    root_cause_suspected: Optional[str] = None
    safety_issues_observed: List[str] = field(default_factory=list)
    data_collected: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: Optional[str] = None
    digital_twin_updates_needed: List[str] = field(default_factory=list)
    graph_memory_links_to_create: List[str] = field(default_factory=list)
    council_review_required: bool = False
    next_experiment: Optional[str] = None
