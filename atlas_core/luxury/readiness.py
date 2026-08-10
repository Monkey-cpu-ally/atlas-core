from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class ProductReadinessLevel(IntEnum):
    IDEA = 1
    RESEARCHED = 2
    CONCEPT = 3
    ENGINEERING_REVIEWED = 4
    PROTOTYPED = 5
    TESTED = 6
    MANUFACTURING_READY = 7
    PRODUCTION = 8
    LIFECYCLE_SUPPORTED = 9


REQUIREMENTS: dict[ProductReadinessLevel, frozenset[str]] = {
    ProductReadinessLevel.IDEA: frozenset({"idea"}),
    ProductReadinessLevel.RESEARCHED: frozenset({"idea", "research"}),
    ProductReadinessLevel.CONCEPT: frozenset({"idea", "research", "concept"}),
    ProductReadinessLevel.ENGINEERING_REVIEWED: frozenset({"idea", "research", "concept", "engineering_review"}),
    ProductReadinessLevel.PROTOTYPED: frozenset({"idea", "research", "concept", "engineering_review", "prototype"}),
    ProductReadinessLevel.TESTED: frozenset({"idea", "research", "concept", "engineering_review", "prototype", "prototype_tests"}),
    ProductReadinessLevel.MANUFACTURING_READY: frozenset({"idea", "research", "concept", "engineering_review", "prototype", "prototype_tests", "council_approval", "manufacturing_plan"}),
    ProductReadinessLevel.PRODUCTION: frozenset({"idea", "research", "concept", "engineering_review", "prototype", "prototype_tests", "council_approval", "manufacturing_plan", "production_run"}),
    ProductReadinessLevel.LIFECYCLE_SUPPORTED: frozenset({"idea", "research", "concept", "engineering_review", "prototype", "prototype_tests", "council_approval", "manufacturing_plan", "production_run", "repair_plan", "archive_record"}),
}


@dataclass(slots=True)
class ProductReadiness:
    product_id: str
    evidence: set[str] = field(default_factory=set)

    def add_evidence(self, *items: str) -> None:
        self.evidence.update(item.strip().lower() for item in items if item.strip())

    @property
    def level(self) -> ProductReadinessLevel:
        achieved = ProductReadinessLevel.IDEA if "idea" in self.evidence else ProductReadinessLevel.IDEA
        for level in ProductReadinessLevel:
            if REQUIREMENTS[level] <= self.evidence:
                achieved = level
            else:
                break
        return achieved

    def missing_for(self, target: ProductReadinessLevel) -> tuple[str, ...]:
        return tuple(sorted(REQUIREMENTS[target] - self.evidence))

    def can_enter_production(self) -> bool:
        return self.level >= ProductReadinessLevel.MANUFACTURING_READY
