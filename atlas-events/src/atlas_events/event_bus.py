"""Small, dependency-free event bus for AtlasOS services."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Any, Callable
from uuid import uuid4

EventHandler = Callable[["AtlasEvent"], None]


@dataclass(frozen=True, slots=True)
class AtlasEvent:
    """Immutable message exchanged between AtlasOS services."""

    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "atlas"
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class EventBus:
    """Thread-safe synchronous event bus.

    Handlers are isolated: one failing subscriber does not stop the remaining
    subscribers. Failures are returned to the caller for logging or diagnostics.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_type: str, handler: EventHandler) -> Callable[[], None]:
        if not event_type.strip():
            raise ValueError("event_type cannot be empty")
        with self._lock:
            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)

        def unsubscribe() -> None:
            self.unsubscribe(event_type, handler)

        return unsubscribe

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        with self._lock:
            handlers = self._handlers.get(event_type)
            if not handlers:
                return
            self._handlers[event_type] = [current for current in handlers if current != handler]
            if not self._handlers[event_type]:
                self._handlers.pop(event_type, None)

    def publish(self, event: AtlasEvent) -> list[Exception]:
        with self._lock:
            handlers = tuple(self._handlers.get(event.event_type, ()))
            wildcard_handlers = tuple(self._handlers.get("*", ()))

        failures: list[Exception] = []
        for handler in (*handlers, *wildcard_handlers):
            try:
                handler(event)
            except Exception as exc:  # subscriber boundaries must be isolated
                failures.append(exc)
        return failures

    def subscriber_count(self, event_type: str | None = None) -> int:
        with self._lock:
            if event_type is not None:
                return len(self._handlers.get(event_type, ()))
            return sum(len(handlers) for handlers in self._handlers.values())
