from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ReviewVerdict(str, Enum):
    APPROVE = "approve"
    REVISE = "revise"
    REBUILD = "rebuild"
    STUDY_FURTHER = "study_further"


class ForgeStage(str, Enum):
    IDEA = "idea"
    RESEARCH = "research"
    STORY = "story"
    FORM = "form"
    MATERIALS = "materials"
    PATTERN = "pattern"
    ENGINEERING = "engineering"
    VIABILITY = "viability"
    CRITIQUE = "critique"
    COUNCIL = "council"
    ARCHIVE = "archive"


@dataclass(frozen=True)
class MaterialProfile:
    name: str
    category: str
    properties: Dict[str, float]
    emotions: List[str] = field(default_factory=list)
    compatible_materials: List[str] = field(default_factory=list)
    repairability: float = 0.5
    sustainability: float = 0.5
    aging_quality: float = 0.5
    notes: str = ""

    def __post_init__(self) -> None:
        for label, value in {
            "repairability": self.repairability,
            "sustainability": self.sustainability,
            "aging_quality": self.aging_quality,
        }.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{label} must be between 0.0 and 1.0")


@dataclass
class DesignConcept:
    design_id: str
    name: str
    product_type: str
    description: str
    story: str = ""
    silhouette_notes: str = ""
    materials: List[str] = field(default_factory=list)
    hardware: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    inspirations: List[str] = field(default_factory=list)
    repair_plan: str = ""
    manufacturing_notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GenomeScore:
    category: str
    score: float
    reason: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 100.0:
            raise ValueError("Genome score must be between 0 and 100")


@dataclass
class DesignGenome:
    design_id: str
    scores: List[GenomeScore]

    @property
    def overall(self) -> float:
        if not self.scores:
            return 0.0
        return round(sum(item.score for item in self.scores) / len(self.scores), 2)

    def as_dict(self) -> Dict[str, float]:
        return {item.category: item.score for item in self.scores}


@dataclass(frozen=True)
class CritiqueFinding:
    category: str
    severity: str
    observation: str
    recommendation: str


@dataclass
class AIReview:
    reviewer: str
    verdict: ReviewVerdict
    score: float
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    required_changes: List[str] = field(default_factory=list)


@dataclass
class CouncilDecision:
    design_id: str
    verdict: ReviewVerdict
    overall_score: float
    reviews: List[AIReview]
    summary: str


@dataclass
class ForgeRecord:
    concept: DesignConcept
    stage: ForgeStage = ForgeStage.IDEA
    genome: Optional[DesignGenome] = None
    critiques: List[CritiqueFinding] = field(default_factory=list)
    council_decision: Optional[CouncilDecision] = None
    history: List[str] = field(default_factory=list)

    def advance(self, stage: ForgeStage, note: str = "") -> None:
        self.stage = stage
        self.history.append(f"{stage.value}: {note}".strip())
