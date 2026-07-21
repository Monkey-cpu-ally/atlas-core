from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Mapping


@dataclass(frozen=True)
class FailureRecord:
    design_id: str
    version: int
    reason: str
    reviewer: str
    weak_categories: List[str] = field(default_factory=list)
    salvageable_ideas: List[str] = field(default_factory=list)
    prohibited_repetition: List[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class FailureArchive:
    def __init__(self) -> None:
        self._records: List[FailureRecord] = []

    def add(self, record: FailureRecord) -> None:
        if record.version < 1:
            raise ValueError("Failure version must be at least 1")
        self._records.append(record)

    def for_design(self, design_id: str) -> List[FailureRecord]:
        return [record for record in self._records if record.design_id == design_id]

    def search(self, term: str) -> List[FailureRecord]:
        needle = term.strip().lower()
        if not needle:
            return list(self._records)
        return [
            record
            for record in self._records
            if needle in " ".join(
                [
                    record.reason,
                    record.reviewer,
                    *record.weak_categories,
                    *record.salvageable_ideas,
                    *record.prohibited_repetition,
                ]
            ).lower()
        ]


@dataclass(frozen=True)
class CertificationResult:
    design_id: str
    certified: bool
    overall_score: float
    failed_gates: List[str]
    scores: Dict[str, float]


class MasterpieceCertificationEngine:
    DEFAULT_THRESHOLDS: Dict[str, float] = {
        "originality": 85.0,
        "engineering": 85.0,
        "craftsmanship": 88.0,
        "comfort": 80.0,
        "durability": 88.0,
        "repairability": 75.0,
        "story": 80.0,
        "manufacturing": 80.0,
        "prototype_testing": 90.0,
        "council_approval": 100.0,
    }

    def __init__(self, thresholds: Mapping[str, float] | None = None) -> None:
        self.thresholds = dict(self.DEFAULT_THRESHOLDS)
        if thresholds:
            self.thresholds.update(thresholds)
        for key, value in self.thresholds.items():
            if not 0.0 <= value <= 100.0:
                raise ValueError(f"Invalid threshold for {key}")

    def evaluate(
        self, design_id: str, scores: Mapping[str, float]
    ) -> CertificationResult:
        missing = [key for key in self.thresholds if key not in scores]
        if missing:
            raise ValueError(f"Missing certification scores: {', '.join(missing)}")
        normalized = {key: float(scores[key]) for key in self.thresholds}
        invalid = [key for key, value in normalized.items() if not 0.0 <= value <= 100.0]
        if invalid:
            raise ValueError(f"Scores must be between 0 and 100: {', '.join(invalid)}")
        failed = [
            key
            for key, threshold in self.thresholds.items()
            if normalized[key] < threshold
        ]
        overall = round(sum(normalized.values()) / len(normalized), 2)
        return CertificationResult(
            design_id=design_id,
            certified=not failed,
            overall_score=overall,
            failed_gates=failed,
            scores=normalized,
        )
