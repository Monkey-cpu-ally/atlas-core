"""Runtime registry for replaceable AtlasOS services."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HealthAwareService(Protocol):
    def health(self) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class ServiceEntry:
    name: str
    service: object
    version: str = "0.1.0"
    replaceable: bool = True


class ServiceRegistry:
    """Thread-safe service lookup with explicit replacement rules."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceEntry] = {}
        self._lock = RLock()

    def register(
        self,
        name: str,
        service: object,
        *,
        version: str = "0.1.0",
        replace: bool = False,
        replaceable: bool = True,
    ) -> ServiceEntry:
        normalized = name.strip().lower()
        if not normalized:
            raise ValueError("service name cannot be empty")
        if service is None:
            raise ValueError("service cannot be None")

        with self._lock:
            existing = self._services.get(normalized)
            if existing is not None:
                if not replace:
                    raise KeyError(f"service already registered: {normalized}")
                if not existing.replaceable:
                    raise PermissionError(f"service is not replaceable: {normalized}")

            entry = ServiceEntry(normalized, service, version, replaceable)
            self._services[normalized] = entry
            return entry

    def get(self, name: str) -> object:
        normalized = name.strip().lower()
        with self._lock:
            try:
                return self._services[normalized].service
            except KeyError as exc:
                raise KeyError(f"service not registered: {normalized}") from exc

    def entry(self, name: str) -> ServiceEntry:
        normalized = name.strip().lower()
        with self._lock:
            try:
                return self._services[normalized]
            except KeyError as exc:
                raise KeyError(f"service not registered: {normalized}") from exc

    def unregister(self, name: str) -> ServiceEntry:
        normalized = name.strip().lower()
        with self._lock:
            try:
                return self._services.pop(normalized)
            except KeyError as exc:
                raise KeyError(f"service not registered: {normalized}") from exc

    def names(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._services))

    def health_snapshot(self) -> dict[str, dict[str, Any]]:
        snapshot: dict[str, dict[str, Any]] = {}
        with self._lock:
            entries = tuple(self._services.values())

        for entry in entries:
            if isinstance(entry.service, HealthAwareService):
                try:
                    status = dict(entry.service.health())
                except Exception as exc:
                    status = {"status": "unhealthy", "error": str(exc)}
            else:
                status = {"status": "unknown"}
            status.setdefault("version", entry.version)
            snapshot[entry.name] = status
        return snapshot
