"""Core service contracts for ATLAS.

These contracts are intentionally small. They define the shape every future ATLAS service
should follow before the system grows more complex.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class ServiceStatus(str, Enum):
    """Common service lifecycle states."""

    OFFLINE = "offline"
    STARTING = "starting"
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    STOPPING = "stopping"


@dataclass(slots=True)
class HealthReport:
    """Health information returned by an ATLAS service."""

    service_name: str
    status: ServiceStatus
    message: str = ""
    details: dict[str, str] = field(default_factory=dict)


class AtlasService(Protocol):
    """Protocol every ATLAS service should implement."""

    name: str
    version: str

    def start(self) -> None:
        """Start the service."""

    def stop(self) -> None:
        """Stop the service."""

    def health_check(self) -> HealthReport:
        """Return service health."""
