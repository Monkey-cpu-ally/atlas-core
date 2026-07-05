"""Event models for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class EventPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class AtlasEvent:
    """A structured event that services can publish and consume."""

    event_type: str
    source_service: str
    payload: dict[str, object] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    actor: str | None = None
    correlation_id: str | None = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
