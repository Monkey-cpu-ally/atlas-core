"""AtlasOS runtime kernel tying together core services and lifecycle events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from typing import Any, Protocol, runtime_checkable

from atlas_events.event_bus import AtlasEvent, EventBus

from .service_registry import ServiceRegistry


@runtime_checkable
class StartableService(Protocol):
    def start(self) -> None: ...


@runtime_checkable
class StoppableService(Protocol):
    def stop(self) -> None: ...


@dataclass(frozen=True, slots=True)
class KernelStatus:
    state: str
    started_at: str | None
    stopped_at: str | None
    registered_services: tuple[str, ...]
    service_health: dict[str, dict[str, Any]]


class AtlasKernel:
    """Coordinates AtlasOS service lifecycle through stable interfaces."""

    def __init__(
        self,
        *,
        event_bus: EventBus | None = None,
        registry: ServiceRegistry | None = None,
    ) -> None:
        self.events = event_bus or EventBus()
        self.services = registry or ServiceRegistry()
        self._state = "created"
        self._started_at: str | None = None
        self._stopped_at: str | None = None
        self._lock = RLock()

        self.services.register("event_bus", self.events, replaceable=False)

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    def register_service(
        self,
        name: str,
        service: object,
        *,
        version: str = "0.1.0",
        replace: bool = False,
        replaceable: bool = True,
    ) -> None:
        self.services.register(
            name,
            service,
            version=version,
            replace=replace,
            replaceable=replaceable,
        )
        self.events.publish(
            AtlasEvent(
                "SERVICE_REGISTERED",
                {"name": name.strip().lower(), "version": version},
                source="atlas-kernel",
            )
        )

    def start(self) -> None:
        with self._lock:
            if self._state == "running":
                return
            if self._state == "starting":
                raise RuntimeError("AtlasOS kernel is already starting")
            self._state = "starting"

        started: list[str] = []
        try:
            for name in self.services.names():
                if name == "event_bus":
                    continue
                service = self.services.get(name)
                if isinstance(service, StartableService):
                    service.start()
                    started.append(name)

            now = datetime.now(UTC).isoformat()
            with self._lock:
                self._state = "running"
                self._started_at = now
                self._stopped_at = None
            self.events.publish(
                AtlasEvent(
                    "KERNEL_STARTED",
                    {"services_started": started},
                    source="atlas-kernel",
                )
            )
        except Exception as exc:
            with self._lock:
                self._state = "failed"
            self.events.publish(
                AtlasEvent(
                    "KERNEL_START_FAILED",
                    {"error": str(exc), "services_started": started},
                    source="atlas-kernel",
                )
            )
            raise

    def stop(self) -> None:
        with self._lock:
            if self._state in {"created", "stopped"}:
                self._state = "stopped"
                self._stopped_at = datetime.now(UTC).isoformat()
                return
            self._state = "stopping"

        failures: dict[str, str] = {}
        stopped: list[str] = []
        for name in reversed(self.services.names()):
            if name == "event_bus":
                continue
            service = self.services.get(name)
            if isinstance(service, StoppableService):
                try:
                    service.stop()
                    stopped.append(name)
                except Exception as exc:
                    failures[name] = str(exc)

        now = datetime.now(UTC).isoformat()
        with self._lock:
            self._state = "stopped" if not failures else "degraded"
            self._stopped_at = now
        self.events.publish(
            AtlasEvent(
                "KERNEL_STOPPED",
                {"services_stopped": stopped, "failures": failures},
                source="atlas-kernel",
            )
        )

    def health(self) -> dict[str, Any]:
        snapshot = self.services.health_snapshot()
        unhealthy = sorted(
            name
            for name, status in snapshot.items()
            if status.get("status") in {"unhealthy", "failed"}
        )
        return {
            "status": "healthy" if self.state == "running" and not unhealthy else self.state,
            "state": self.state,
            "unhealthy_services": unhealthy,
            "services": snapshot,
        }

    def status(self) -> KernelStatus:
        return KernelStatus(
            state=self.state,
            started_at=self._started_at,
            stopped_at=self._stopped_at,
            registered_services=self.services.names(),
            service_health=self.services.health_snapshot(),
        )
