"""API service skeleton for ATLAS.

This is not a web server yet. It defines the first route registry boundary that a
future FastAPI or similar HTTP layer can wrap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

try:
    from atlas_core_runtime.service import HealthReport, ServiceStatus
except ImportError:
    HealthReport = object  # type: ignore
    ServiceStatus = None  # type: ignore

RouteHandler = Callable[[dict[str, object]], dict[str, object]]


@dataclass
class ApiService:
    """Small in-memory API route registry."""

    name: str = "atlas-api"
    version: str = "0.1.0"
    _routes: dict[str, RouteHandler] = field(default_factory=dict)
    _running: bool = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def register_route(self, path: str, handler: RouteHandler) -> None:
        if not path.startswith("/"):
            raise ValueError("API route paths must start with '/'")
        self._routes[path] = handler

    def call(self, path: str, payload: dict[str, object] | None = None) -> dict[str, object]:
        if path not in self._routes:
            raise KeyError(f"API route not registered: {path}")
        return self._routes[path](payload or {})

    def list_routes(self) -> list[str]:
        return sorted(self._routes.keys())

    def health_check(self):
        if ServiceStatus is None:
            return {"service_name": self.name, "status": "healthy" if self._running else "offline"}
        return HealthReport(
            service_name=self.name,
            status=ServiceStatus.HEALTHY if self._running else ServiceStatus.OFFLINE,
            message=f"{len(self._routes)} routes registered",
        )
