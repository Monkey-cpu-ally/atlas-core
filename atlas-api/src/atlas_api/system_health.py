"""System health API contract for ATLAS."""

from __future__ import annotations

from atlas_core_runtime.registry import ServiceRegistry

from .models import ServiceHealthDTO, SystemHealthResponse


CRITICAL_STATUSES = {"critical", "offline", "degraded"}
WARNING_STATUSES = {"warning"}


def build_system_health_response(registry: ServiceRegistry) -> SystemHealthResponse:
    """Build a framework-neutral system health response from the service registry."""

    reports = registry.health_report()
    service_dtos: list[ServiceHealthDTO] = []
    statuses: list[str] = []

    for report in reports:
        status_value = getattr(report.status, "value", str(report.status))
        statuses.append(status_value)
        service_dtos.append(
            ServiceHealthDTO(
                service_name=report.service_name,
                status=status_value,
                message=report.message,
                details=getattr(report, "details", {}) or {},
            )
        )

    if any(status in CRITICAL_STATUSES for status in statuses):
        overall = "degraded"
    elif any(status in WARNING_STATUSES for status in statuses):
        overall = "warning"
    else:
        overall = "healthy"

    return SystemHealthResponse(status=overall, services=service_dtos)
