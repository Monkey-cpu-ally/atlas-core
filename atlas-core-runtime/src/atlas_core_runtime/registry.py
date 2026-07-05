"""Service registry for ATLAS Core Runtime."""

from __future__ import annotations

from dataclasses import dataclass, field

from .service import AtlasService, HealthReport, ServiceStatus


@dataclass
class ServiceRegistry:
    """In-memory registry for ATLAS services.

    This is a first scaffold. Later this can be backed by dependency injection,
    persistent runtime state, and richer service discovery.
    """

    _services: dict[str, AtlasService] = field(default_factory=dict)

    def register(self, service: AtlasService) -> None:
        if service.name in self._services:
            raise ValueError(f"Service already registered: {service.name}")
        self._services[service.name] = service

    def get(self, name: str) -> AtlasService:
        try:
            return self._services[name]
        except KeyError as exc:
            raise KeyError(f"Service not registered: {name}") from exc

    def list_services(self) -> list[str]:
        return sorted(self._services.keys())

    def health_report(self) -> list[HealthReport]:
        reports: list[HealthReport] = []
        for service in self._services.values():
            try:
                reports.append(service.health_check())
            except Exception as exc:  # defensive runtime boundary
                reports.append(
                    HealthReport(
                        service_name=service.name,
                        status=ServiceStatus.CRITICAL,
                        message=str(exc),
                    )
                )
        return reports
