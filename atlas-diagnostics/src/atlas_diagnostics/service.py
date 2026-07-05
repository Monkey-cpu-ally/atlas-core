"""Diagnostics service for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from atlas_core_runtime.service import HealthReport, ServiceStatus
except ImportError:
    HealthReport = object  # type: ignore
    ServiceStatus = None  # type: ignore


@dataclass
class DiagnosticsService:
    """Aggregates service health reports."""

    name: str = "atlas-diagnostics"
    version: str = "0.1.0"
    _running: bool = False
    _last_reports: list[object] = field(default_factory=list)

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def collect(self, reports: list[object]) -> list[object]:
        self._last_reports = list(reports)
        return self._last_reports

    def last_reports(self) -> list[object]:
        return list(self._last_reports)

    def health_check(self):
        if ServiceStatus is None:
            return {"service_name": self.name, "status": "healthy" if self._running else "offline"}
        return HealthReport(
            service_name=self.name,
            status=ServiceStatus.HEALTHY if self._running else ServiceStatus.OFFLINE,
            message=f"{len(self._last_reports)} reports collected",
        )
