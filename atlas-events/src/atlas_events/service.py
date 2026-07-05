"""In-memory event bus service for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

try:
    from atlas_core_runtime.service import HealthReport, ServiceStatus
except ImportError:  # Allows local file review before packaging is wired.
    HealthReport = object  # type: ignore
    ServiceStatus = None  # type: ignore

from .models import AtlasEvent

EventHandler = Callable[[AtlasEvent], None]


@dataclass
class EventBusService:
    """Small in-memory event bus.

    This is not the final distributed event system. It is the first working service
    shape for local development and testing.
    """

    name: str = "atlas-events"
    version: str = "0.1.0"
    _events: list[AtlasEvent] = field(default_factory=list)
    _subscribers: dict[str, list[EventHandler]] = field(default_factory=dict)
    _running: bool = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def publish(self, event: AtlasEvent) -> None:
        self._events.append(event)
        for handler in self._subscribers.get(event.event_type, []):
            handler(event)
        for handler in self._subscribers.get("*", []):
            handler(event)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def list_events(self) -> list[AtlasEvent]:
        return list(self._events)

    def health_check(self):
        if ServiceStatus is None:
            return {"service_name": self.name, "status": "healthy" if self._running else "offline"}
        return HealthReport(
            service_name=self.name,
            status=ServiceStatus.HEALTHY if self._running else ServiceStatus.OFFLINE,
            message=f"{len(self._events)} events stored in memory",
        )
