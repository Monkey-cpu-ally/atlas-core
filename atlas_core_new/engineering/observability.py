"""
Observability Layer — Structured logging, crash reporting, analytics events.

If you can't see failures, you can't fix them fast.

Event types:
- action: User-triggered actions (record_started, message_sent, panel_opened)
- error: Failures and exceptions (api_error, db_error, render_error)  
- metric: Performance measurements (response_time, load_time, cache_hit)
- lifecycle: System state changes (startup, shutdown, seed_complete)
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from collections import deque

logger = logging.getLogger("atlas.observability")


class EventLevel(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


class EventCategory(str, Enum):
    ACTION = "action"
    ERROR = "error"
    METRIC = "metric"
    LIFECYCLE = "lifecycle"
    REFUSAL = "refusal"


@dataclass
class ObservabilityEvent:
    event_name: str
    category: EventCategory
    level: EventLevel
    feature_id: Optional[str] = None
    detail: str = ""
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


_event_buffer: deque[ObservabilityEvent] = deque(maxlen=1000)
_crash_reports: deque[dict] = deque(maxlen=100)
_counters: dict[str, int] = {}


def emit(event_name: str, category: EventCategory, level: EventLevel = EventLevel.INFO,
         feature_id: Optional[str] = None, detail: str = "", metadata: Optional[dict] = None):
    event = ObservabilityEvent(
        event_name=event_name,
        category=category,
        level=level,
        feature_id=feature_id,
        detail=detail,
        metadata=metadata or {},
    )
    _event_buffer.append(event)

    _counters[event_name] = _counters.get(event_name, 0) + 1

    log_msg = f"[{category.value}] {event_name}"
    if feature_id:
        log_msg += f" ({feature_id})"
    if detail:
        log_msg += f": {detail}"

    if level == EventLevel.ERROR or level == EventLevel.CRITICAL:
        logger.error(log_msg)
    elif level == EventLevel.WARN:
        logger.warning(log_msg)
    else:
        logger.info(log_msg)


def report_crash(feature_id: str, error_type: str, error_message: str,
                 stack_trace: str = "", metadata: Optional[dict] = None):
    report = {
        "feature_id": feature_id,
        "error_type": error_type,
        "error_message": error_message,
        "stack_trace": stack_trace,
        "metadata": metadata or {},
        "timestamp": time.time(),
    }
    _crash_reports.append(report)

    emit(
        event_name=f"crash_{error_type}",
        category=EventCategory.ERROR,
        level=EventLevel.CRITICAL,
        feature_id=feature_id,
        detail=error_message,
        metadata={"stack_trace": stack_trace[:500]},
    )

    return report


def get_recent_events(limit: int = 100, category: Optional[str] = None,
                      level: Optional[str] = None) -> list[dict]:
    events = list(_event_buffer)

    if category:
        events = [e for e in events if e.category.value == category]
    if level:
        events = [e for e in events if e.level.value == level]

    events = sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]

    return [
        {
            "event_name": e.event_name,
            "category": e.category.value,
            "level": e.level.value,
            "feature_id": e.feature_id,
            "detail": e.detail,
            "metadata": e.metadata,
            "timestamp": e.timestamp,
        }
        for e in events
    ]


def get_crash_reports(limit: int = 20) -> list[dict]:
    reports = sorted(_crash_reports, key=lambda r: r["timestamp"], reverse=True)
    return list(reports[:limit])


def get_counters() -> dict:
    return dict(_counters)


def get_health_summary() -> dict:
    now = time.time()
    recent_window = 300

    recent = [e for e in _event_buffer if now - e.timestamp < recent_window]
    errors_recent = [e for e in recent if e.level in (EventLevel.ERROR, EventLevel.CRITICAL)]
    crashes_recent = [r for r in _crash_reports if now - r["timestamp"] < recent_window]

    if len(crashes_recent) > 0:
        status = "critical"
    elif len(errors_recent) > 5:
        status = "degraded"
    elif len(errors_recent) > 0:
        status = "warning"
    else:
        status = "healthy"

    return {
        "status": status,
        "total_events": len(_event_buffer),
        "events_last_5min": len(recent),
        "errors_last_5min": len(errors_recent),
        "crashes_last_5min": len(crashes_recent),
        "total_crash_reports": len(_crash_reports),
        "top_events": sorted(_counters.items(), key=lambda x: x[1], reverse=True)[:10],
    }


emit("system_boot", EventCategory.LIFECYCLE, EventLevel.INFO, detail="Observability layer initialized")
