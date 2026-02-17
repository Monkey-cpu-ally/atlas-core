"""
Refusal + Fallback Engine — Centralized failure handling.

Every risky operation gets a fallback chain:
- no internet → cached mode
- API down → retry + show status
- permission denied → guide user
- storage full → warn + cleanup tools

All refusals are logged to the observability system.
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable, Any

logger = logging.getLogger("atlas.refusal_engine")


class FailureType(str, Enum):
    NETWORK_DOWN = "network_down"
    API_UNAVAILABLE = "api_unavailable"
    API_TIMEOUT = "api_timeout"
    API_KEY_MISSING = "api_key_missing"
    PERMISSION_DENIED = "permission_denied"
    STORAGE_FULL = "storage_full"
    DATABASE_ERROR = "database_error"
    RATE_LIMITED = "rate_limited"
    INVALID_INPUT = "invalid_input"
    UNKNOWN = "unknown"


class FallbackAction(str, Enum):
    CACHE = "cache"
    RETRY = "retry"
    DEGRADE = "degrade"
    GUIDE = "guide"
    WARN = "warn"
    REFUSE = "refuse"
    QUEUE = "queue"


@dataclass
class RefusalEvent:
    feature_id: str
    failure_type: FailureType
    fallback_action: FallbackAction
    message_to_user: str
    technical_detail: str
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    resolved: bool = False


FALLBACK_CHAINS = {
    FailureType.NETWORK_DOWN: [
        {
            "action": FallbackAction.CACHE,
            "message": "You're offline. Showing cached data — some features may be limited.",
            "technical": "Network unreachable, serving from local cache",
        },
        {
            "action": FallbackAction.QUEUE,
            "message": "Your request is saved and will send when you're back online.",
            "technical": "Request queued for background sync",
        },
    ],
    FailureType.API_UNAVAILABLE: [
        {
            "action": FallbackAction.RETRY,
            "message": "The AI service is temporarily busy. Retrying...",
            "technical": "API returned 5xx, retry with exponential backoff",
        },
        {
            "action": FallbackAction.DEGRADE,
            "message": "AI service is down. Showing limited functionality.",
            "technical": "Degraded mode: disable AI-dependent features, show status",
        },
    ],
    FailureType.API_TIMEOUT: [
        {
            "action": FallbackAction.RETRY,
            "message": "Response is taking longer than expected. Retrying...",
            "technical": "Request timeout exceeded, retry with longer timeout",
        },
        {
            "action": FallbackAction.DEGRADE,
            "message": "The request couldn't complete in time. Try a shorter question or try again later.",
            "technical": "Multiple timeouts, suggest simpler request",
        },
    ],
    FailureType.API_KEY_MISSING: [
        {
            "action": FallbackAction.GUIDE,
            "message": "This feature needs an API key to work. Check the setup instructions.",
            "technical": "Required environment variable not set",
        },
    ],
    FailureType.PERMISSION_DENIED: [
        {
            "action": FallbackAction.GUIDE,
            "message": "This feature needs your permission to work. Here's how to enable it.",
            "technical": "Browser/OS permission not granted for requested resource",
        },
        {
            "action": FallbackAction.DEGRADE,
            "message": "Permission not granted. Using an alternative method.",
            "technical": "Falling back to non-permission-requiring alternative",
        },
    ],
    FailureType.STORAGE_FULL: [
        {
            "action": FallbackAction.WARN,
            "message": "Storage is getting full. Consider clearing old conversations or data.",
            "technical": "Storage quota approaching limit",
        },
        {
            "action": FallbackAction.REFUSE,
            "message": "Storage is full. Please free up space before saving new data.",
            "technical": "Storage quota exceeded, write operations blocked",
        },
    ],
    FailureType.DATABASE_ERROR: [
        {
            "action": FallbackAction.RETRY,
            "message": "Having trouble saving. Retrying...",
            "technical": "Database connection error, retry with fresh connection",
        },
        {
            "action": FallbackAction.CACHE,
            "message": "Database is temporarily unavailable. Your data is saved locally and will sync when it's back.",
            "technical": "Database unreachable, using localStorage fallback",
        },
    ],
    FailureType.RATE_LIMITED: [
        {
            "action": FallbackAction.QUEUE,
            "message": "Too many requests. Your message is queued and will send shortly.",
            "technical": "Rate limit hit, queuing with backoff timer",
        },
    ],
    FailureType.INVALID_INPUT: [
        {
            "action": FallbackAction.GUIDE,
            "message": "That input doesn't look right. Here's what's expected.",
            "technical": "Input validation failed",
        },
    ],
}


_event_log: list[RefusalEvent] = []


def handle_failure(feature_id: str, failure_type: FailureType, detail: str = "") -> RefusalEvent:
    chain = FALLBACK_CHAINS.get(failure_type, FALLBACK_CHAINS[FailureType.UNKNOWN] if FailureType.UNKNOWN in FALLBACK_CHAINS else [])

    if not chain:
        chain = [{"action": FallbackAction.REFUSE, "message": "Something went wrong. Please try again.", "technical": "No fallback chain defined"}]

    step = chain[0]

    event = RefusalEvent(
        feature_id=feature_id,
        failure_type=failure_type,
        fallback_action=step["action"],
        message_to_user=step["message"],
        technical_detail=f"{step['technical']}: {detail}" if detail else step["technical"],
    )

    _event_log.append(event)

    logger.warning(
        "REFUSAL [%s] %s → %s | %s",
        feature_id,
        failure_type.value,
        step["action"].value,
        event.technical_detail,
    )

    return event


def get_recent_events(limit: int = 50) -> list[dict]:
    events = sorted(_event_log, key=lambda e: e.timestamp, reverse=True)[:limit]
    return [
        {
            "feature_id": e.feature_id,
            "failure_type": e.failure_type.value,
            "fallback_action": e.fallback_action.value,
            "message": e.message_to_user,
            "detail": e.technical_detail,
            "timestamp": e.timestamp,
            "resolved": e.resolved,
        }
        for e in events
    ]


def get_failure_summary() -> dict:
    if not _event_log:
        return {"total_events": 0, "by_type": {}, "by_feature": {}, "unresolved": 0}

    by_type: dict[str, int] = {}
    by_feature: dict[str, int] = {}
    unresolved = 0

    for e in _event_log:
        by_type[e.failure_type.value] = by_type.get(e.failure_type.value, 0) + 1
        by_feature[e.feature_id] = by_feature.get(e.feature_id, 0) + 1
        if not e.resolved:
            unresolved += 1

    return {
        "total_events": len(_event_log),
        "by_type": by_type,
        "by_feature": by_feature,
        "unresolved": unresolved,
    }
