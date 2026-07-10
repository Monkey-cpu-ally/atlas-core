"""Event records for the ATLAS Tool Bus."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


class ToolEventType(str, Enum):
    """Standard Tool Bus event types."""

    JOB_RECEIVED = "job_received"
    SAFETY_ALLOWED = "safety_allowed"
    SAFETY_APPROVAL_REQUIRED = "safety_approval_required"
    SAFETY_DENIED = "safety_denied"
    ADAPTER_VERIFICATION_FAILED = "adapter_verification_failed"
    JOB_STARTED = "job_started"
    JOB_SUCCEEDED = "job_succeeded"
    JOB_FAILED = "job_failed"
    JOB_CANCELLED = "job_cancelled"


@dataclass(frozen=True)
class ToolEvent:
    """One immutable event emitted by the Tool Bus."""

    event_type: ToolEventType
    job_id: str
    tool_name: str
    source: str = "tool_bus"
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["event_type"] = self.event_type.value
        return data


class InMemoryEventLog:
    """Simple append-only event log for the initial Tool Bus implementation."""

    def __init__(self) -> None:
        self._events: List[ToolEvent] = []

    def append(self, event: ToolEvent) -> None:
        self._events.append(event)

    def extend(self, events: Iterable[ToolEvent]) -> None:
        self._events.extend(events)

    def all(self) -> List[ToolEvent]:
        return list(self._events)

    def for_job(self, job_id: str) -> List[ToolEvent]:
        return [event for event in self._events if event.job_id == job_id]

    def for_tool(self, tool_name: str) -> List[ToolEvent]:
        return [event for event in self._events if event.tool_name == tool_name]

    def latest(self, limit: int = 50) -> List[ToolEvent]:
        if limit <= 0:
            return []
        return list(self._events[-limit:])

    def clear(self) -> None:
        self._events.clear()

    def __len__(self) -> int:
        return len(self._events)
