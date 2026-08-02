"""AtlasOS service health registry and executive status aggregation."""
from __future__ import annotations

import inspect
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    NOT_IMPLEMENTED = "not_implemented"


@dataclass(frozen=True)
class ServiceDefinition:
    id: str
    name: str
    owner: str
    category: str
    required_for_v1: bool
    health_endpoint: str | None = None
    implementation_status: str = "implemented"


@dataclass
class ServiceHealth:
    service_id: str
    name: str
    owner: str
    category: str
    state: HealthState
    required_for_v1: bool
    checked_at: str
    summary: str
    details: dict[str, Any]
    health_endpoint: str | None = None


Probe = Callable[[], dict[str, Any] | Awaitable[dict[str, Any]]]


SERVICE_DEFINITIONS: tuple[ServiceDefinition, ...] = (
    ServiceDefinition("campus-service", "Campus Engine", "council", "experience", True, "/api/campus/health"),
    ServiceDefinition("knowledge-service", "Knowledge Bank", "council", "knowledge", True, "/api/knowledge/governance/health"),
    ServiceDefinition("ai-orchestrator", "AI Orchestrator", "council", "intelligence", True, "/api/ai-services/status"),
    ServiceDefinition("project-service", "Project Intelligence", "ajani", "operations", True, "/api/project-intelligence/status"),
    ServiceDefinition("digital-twin-service", "Digital Twin Engine", "hermes", "engineering", True, "/api/twins"),
    ServiceDefinition("research-service", "Research Engine", "minerva", "science", True, "/api/research-labs/status"),
    ServiceDefinition("engineering-service", "Engineering OS", "hermes", "engineering", True, "/api/engineering-os/status"),
    ServiceDefinition("simulation-service", "Simulation Engine", "hermes", "engineering", False, implementation_status="partial"),
    ServiceDefinition("manufacturing-service", "Manufacturing Engine", "hermes", "manufacturing", False, implementation_status="partial"),
    ServiceDefinition("strategy-service", "Strategy Engine", "ajani", "operations", False, implementation_status="partial"),
    ServiceDefinition("audit-service", "Audit Service", "council", "infrastructure", True, implementation_status="partial"),
    ServiceDefinition("notification-service", "Notification Service", "ajani", "infrastructure", False, implementation_status="partial"),
    ServiceDefinition("robotics-fleet-service", "Robotics Fleet Service", "hermes", "robotics", False, implementation_status="planned"),
)

_PROBES: dict[str, Probe] = {}


def register_probe(service_id: str, probe: Probe) -> None:
    if service_id not in {item.id for item in SERVICE_DEFINITIONS}:
        raise KeyError(f"Unknown AtlasOS service: {service_id}")
    _PROBES[service_id] = probe


def unregister_probe(service_id: str) -> None:
    _PROBES.pop(service_id, None)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_state(value: Any) -> HealthState:
    text = str(value or "unknown").strip().lower()
    aliases = {"ok": "healthy", "up": "healthy", "ready": "healthy", "error": "offline", "down": "offline"}
    text = aliases.get(text, text)
    try:
        return HealthState(text)
    except ValueError:
        return HealthState.UNKNOWN


async def _run_probe(definition: ServiceDefinition) -> ServiceHealth:
    checked_at = _now()
    probe = _PROBES.get(definition.id)

    if probe is None:
        if definition.implementation_status == "planned":
            state = HealthState.NOT_IMPLEMENTED
            summary = "Planned service has no runtime health probe yet."
        else:
            state = HealthState.UNKNOWN
            summary = "Service exists or is partially designed, but no runtime probe is registered."
        return ServiceHealth(
            service_id=definition.id,
            name=definition.name,
            owner=definition.owner,
            category=definition.category,
            state=state,
            required_for_v1=definition.required_for_v1,
            checked_at=checked_at,
            summary=summary,
            details={"implementation_status": definition.implementation_status},
            health_endpoint=definition.health_endpoint,
        )

    try:
        result = probe()
        if inspect.isawaitable(result):
            result = await result
        if not isinstance(result, dict):
            raise TypeError("Health probe must return a dictionary")
        state = _normalize_state(result.get("status") or result.get("state"))
        return ServiceHealth(
            service_id=definition.id,
            name=definition.name,
            owner=definition.owner,
            category=definition.category,
            state=state,
            required_for_v1=definition.required_for_v1,
            checked_at=checked_at,
            summary=str(result.get("summary") or f"{definition.name} reported {state.value}."),
            details=result,
            health_endpoint=definition.health_endpoint,
        )
    except Exception as exc:  # health aggregation must never crash the dashboard
        return ServiceHealth(
            service_id=definition.id,
            name=definition.name,
            owner=definition.owner,
            category=definition.category,
            state=HealthState.OFFLINE,
            required_for_v1=definition.required_for_v1,
            checked_at=checked_at,
            summary="Health probe failed.",
            details={"error": type(exc).__name__, "message": str(exc)},
            health_endpoint=definition.health_endpoint,
        )


async def service_health(service_id: str) -> dict[str, Any] | None:
    definition = next((item for item in SERVICE_DEFINITIONS if item.id == service_id), None)
    if definition is None:
        return None
    return asdict(await _run_probe(definition))


async def all_service_health() -> list[dict[str, Any]]:
    return [asdict(await _run_probe(item)) for item in SERVICE_DEFINITIONS]


async def executive_summary() -> dict[str, Any]:
    services = await all_service_health()
    counts = {state.value: 0 for state in HealthState}
    for item in services:
        counts[item["state"]] += 1

    required = [item for item in services if item["required_for_v1"]]
    blocking = [item for item in required if item["state"] in {HealthState.OFFLINE.value, HealthState.NOT_IMPLEMENTED.value}]
    uncertain = [item for item in required if item["state"] == HealthState.UNKNOWN.value]
    degraded = [item for item in required if item["state"] == HealthState.DEGRADED.value]

    if blocking:
        overall = HealthState.OFFLINE
    elif degraded or uncertain:
        overall = HealthState.DEGRADED
    else:
        overall = HealthState.HEALTHY

    return {
        "status": overall.value,
        "generated_at": _now(),
        "version": "0.1.0",
        "service_counts": counts,
        "v1_required_services": len(required),
        "v1_blockers": [item["service_id"] for item in blocking],
        "v1_uncertain": [item["service_id"] for item in uncertain],
        "v1_degraded": [item["service_id"] for item in degraded],
        "services": services,
        "truth_rule": "Unknown services remain unknown; the dashboard never reports false health.",
    }


def registry_manifest() -> dict[str, Any]:
    return {
        "version": "0.1.0",
        "services": [asdict(item) for item in SERVICE_DEFINITIONS],
        "registered_probes": sorted(_PROBES),
    }
