"""API response models for ATLAS.

These are framework-neutral models. FastAPI or another HTTP layer can wrap them later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class ServiceHealthDTO:
    """Serializable service health response."""

    service_name: str
    status: str
    message: str = ""
    details: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class SystemHealthResponse:
    """System health summary returned to the HUD/API clients."""

    status: str
    services: list[ServiceHealthDTO]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
