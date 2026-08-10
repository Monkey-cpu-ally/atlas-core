from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class LifecycleEventType(str, Enum):
    CREATED = "created"
    REVISION = "revision"
    PROTOTYPE = "prototype"
    TEST = "test"
    COUNCIL_DECISION = "council_decision"
    MANUFACTURING = "manufacturing"
    QUALITY = "quality"
    REPAIR = "repair"
    OWNERSHIP = "ownership"
    ARCHIVE = "archive"


@dataclass(slots=True, frozen=True)
class LifecycleEvent:
    event_type: LifecycleEventType
    summary: str
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class ProductDigitalTwin:
    product_id: str
    product_name: str
    collection_id: str | None = None
    design_revision: int = 1
    serial_number: str | None = None
    materials: list[str] = field(default_factory=list)
    hardware: list[str] = field(default_factory=list)
    readiness_level: int = 1
    owner_reference: str | None = None
    events: list[LifecycleEvent] = field(default_factory=list)

    def add_event(self, event: LifecycleEvent) -> None:
        self.events.append(event)

    def record_revision(self, revision: int, summary: str) -> None:
        if revision <= self.design_revision:
            raise ValueError("Digital twin revision must move forward")
        self.design_revision = revision
        self.add_event(
            LifecycleEvent(
                LifecycleEventType.REVISION,
                summary,
                {"revision": revision},
            )
        )

    def record_repair(self, summary: str, provider: str | None = None, cost: float | None = None) -> None:
        metadata: dict[str, object] = {}
        if provider:
            metadata["provider"] = provider
        if cost is not None:
            if cost < 0:
                raise ValueError("Repair cost cannot be negative")
            metadata["cost"] = cost
        self.add_event(LifecycleEvent(LifecycleEventType.REPAIR, summary, metadata))

    @property
    def repair_count(self) -> int:
        return sum(event.event_type is LifecycleEventType.REPAIR for event in self.events)

    @property
    def latest_event(self) -> LifecycleEvent | None:
        return self.events[-1] if self.events else None
