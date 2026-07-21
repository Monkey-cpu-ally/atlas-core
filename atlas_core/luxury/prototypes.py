from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List


class TestStatus(str, Enum):
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class PrototypeTest:
    test_name: str
    measured_value: float
    required_value: float
    higher_is_better: bool = True
    unit: str = ""
    notes: str = ""

    @property
    def status(self) -> TestStatus:
        passed = (
            self.measured_value >= self.required_value
            if self.higher_is_better
            else self.measured_value <= self.required_value
        )
        return TestStatus.PASS if passed else TestStatus.FAIL

    @property
    def performance_ratio(self) -> float:
        if self.required_value == 0:
            return 1.0 if self.measured_value == 0 else 0.0
        ratio = (
            self.measured_value / self.required_value
            if self.higher_is_better
            else self.required_value / max(self.measured_value, 1e-9)
        )
        return round(max(0.0, min(ratio, 1.25)), 3)


@dataclass
class PrototypeRecord:
    prototype_id: str
    design_id: str
    version: int
    tests: List[PrototypeTest] = field(default_factory=list)
    notes: str = ""

    @property
    def pass_rate(self) -> float:
        if not self.tests:
            return 0.0
        passed = sum(test.status == TestStatus.PASS for test in self.tests)
        return round(passed / len(self.tests) * 100.0, 2)

    @property
    def passed(self) -> bool:
        return bool(self.tests) and all(test.status == TestStatus.PASS for test in self.tests)


class PrototypeLaboratory:
    def __init__(self) -> None:
        self._records: Dict[str, PrototypeRecord] = {}

    def register(self, record: PrototypeRecord) -> None:
        if record.prototype_id in self._records:
            raise ValueError(f"Prototype already exists: {record.prototype_id}")
        if record.version < 1:
            raise ValueError("Prototype version must be at least 1")
        self._records[record.prototype_id] = record

    def add_test(self, prototype_id: str, test: PrototypeTest) -> None:
        self.get(prototype_id).tests.append(test)

    def get(self, prototype_id: str) -> PrototypeRecord:
        try:
            return self._records[prototype_id]
        except KeyError as exc:
            raise KeyError(f"Unknown prototype: {prototype_id}") from exc

    def for_design(self, design_id: str) -> List[PrototypeRecord]:
        records: Iterable[PrototypeRecord] = self._records.values()
        return sorted(
            (record for record in records if record.design_id == design_id),
            key=lambda record: record.version,
        )

    def latest_passed(self, design_id: str) -> PrototypeRecord | None:
        passed = [record for record in self.for_design(design_id) if record.passed]
        return passed[-1] if passed else None
