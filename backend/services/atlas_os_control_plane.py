"""AtlasOS control-plane registry and readiness model.

This module does not replace existing ATLAS services. It provides a single,
well-defined registry that describes service ownership, dependencies, health
endpoints, and implementation status for the AtlasOS platform.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ServiceDefinition:
    service_id: str
    name: str
    owner_ai: str
    category: str
    route_prefix: str
    health_path: Optional[str]
    dependencies: tuple[str, ...] = ()
    status: str = "implemented"
    description: str = ""


_SERVICE_REGISTRY: Dict[str, ServiceDefinition] = {
    "engineering_os": ServiceDefinition(
        service_id="engineering_os",
        name="Engineering Operating System",
        owner_ai="Hermes",
        category="workflow",
        route_prefix="/api/engineering-os",
        health_path="/api/engineering-os/health",
        dependencies=(),
        description="Missions, tasks, risks, workflow phases, and engineering events.",
    ),
    "knowledge_graph": ServiceDefinition(
        service_id="knowledge_graph",
        name="Knowledge Graph",
        owner_ai="Minerva",
        category="knowledge",
        route_prefix="/api/knowledge-graph",
        health_path="/api/knowledge-graph/health",
        dependencies=(),
        description="Linked engineering knowledge, entities, and relationships.",
    ),
    "knowledge_bank": ServiceDefinition(
        service_id="knowledge_bank",
        name="Knowledge Bank",
        owner_ai="Minerva",
        category="knowledge",
        route_prefix="/api/kbase",
        health_path="/api/kbase/health",
        dependencies=("knowledge_graph",),
        description="Persistent documents, records, lessons, sources, and retrieval.",
    ),
    "digital_twin": ServiceDefinition(
        service_id="digital_twin",
        name="Digital Twin Engine",
        owner_ai="Hermes",
        category="engineering",
        route_prefix="/api/twins",
        health_path="/api/twins/health",
        dependencies=("knowledge_bank",),
        description="Configuration, lifecycle, test, maintenance, and operational records.",
    ),
    "research_orchestrator": ServiceDefinition(
        service_id="research_orchestrator",
        name="Research Orchestrator",
        owner_ai="Minerva",
        category="research",
        route_prefix="/api/research-orchestrator",
        health_path="/api/research-orchestrator/health",
        dependencies=("knowledge_bank",),
        description="Structured research missions, evidence review, and discovery intake.",
    ),
    "mission_scheduler": ServiceDefinition(
        service_id="mission_scheduler",
        name="Mission Scheduler",
        owner_ai="Ajani",
        category="operations",
        route_prefix="/api/mission-scheduler",
        health_path="/api/mission-scheduler/health",
        dependencies=("engineering_os",),
        description="Scheduling, priorities, recurring missions, and operational timing.",
    ),
    "project_intelligence": ServiceDefinition(
        service_id="project_intelligence",
        name="Project Intelligence",
        owner_ai="Ajani",
        category="operations",
        route_prefix="/api/project-intelligence",
        health_path="/api/project-intelligence/health",
        dependencies=("engineering_os", "knowledge_bank"),
        description="Project status, milestones, constraints, risks, and evidence-backed progress.",
    ),
    "council": ServiceDefinition(
        service_id="council",
        name="ATLAS Council",
        owner_ai="Council",
        category="coordination",
        route_prefix="/api/council",
        health_path=None,
        dependencies=("engineering_os", "knowledge_bank"),
        description="Cross-disciplinary review across Hermes, Minerva, and Ajani.",
    ),
    "weaver": ServiceDefinition(
        service_id="weaver",
        name="Weaver Manufacturing Service",
        owner_ai="Hermes",
        category="manufacturing",
        route_prefix="/api/weaver",
        health_path=None,
        dependencies=("digital_twin", "engineering_os"),
        description="Manufacturing workflows, tooling, assembly, and factory coordination.",
    ),
    "hud": ServiceDefinition(
        service_id="hud",
        name="ATLAS HUD Surfaces",
        owner_ai="Council",
        category="interface",
        route_prefix="/api/hud-surfaces",
        health_path=None,
        dependencies=(),
        description="User-facing ATLAS interface and status surfaces.",
    ),
}


def list_services(
    *,
    owner_ai: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
) -> List[dict]:
    """Return service definitions with optional exact-match filters."""
    services: Iterable[ServiceDefinition] = _SERVICE_REGISTRY.values()
    if owner_ai:
        services = (item for item in services if item.owner_ai.lower() == owner_ai.lower())
    if category:
        services = (item for item in services if item.category.lower() == category.lower())
    if status:
        services = (item for item in services if item.status.lower() == status.lower())
    return [serialize(item) for item in sorted(services, key=lambda value: value.service_id)]


def get_service(service_id: str) -> Optional[dict]:
    item = _SERVICE_REGISTRY.get(service_id)
    return serialize(item) if item else None


def dependency_order() -> List[str]:
    """Return a deterministic topological startup order.

    Raises RuntimeError when a missing dependency or dependency cycle is found.
    """
    visiting: set[str] = set()
    visited: set[str] = set()
    ordered: List[str] = []

    def visit(service_id: str) -> None:
        if service_id in visited:
            return
        if service_id in visiting:
            raise RuntimeError(f"AtlasOS dependency cycle detected at {service_id}")
        service = _SERVICE_REGISTRY.get(service_id)
        if service is None:
            raise RuntimeError(f"AtlasOS registry references missing service: {service_id}")
        visiting.add(service_id)
        for dependency in service.dependencies:
            if dependency not in _SERVICE_REGISTRY:
                raise RuntimeError(
                    f"AtlasOS service {service_id} references missing dependency {dependency}"
                )
            visit(dependency)
        visiting.remove(service_id)
        visited.add(service_id)
        ordered.append(service_id)

    for registered_id in sorted(_SERVICE_REGISTRY):
        visit(registered_id)
    return ordered


def platform_summary() -> dict:
    services = list_services()
    owners: Dict[str, int] = {}
    categories: Dict[str, int] = {}
    for service in services:
        owners[service["owner_ai"]] = owners.get(service["owner_ai"], 0) + 1
        categories[service["category"]] = categories.get(service["category"], 0) + 1

    return {
        "platform": "AtlasOS",
        "status": "operational",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "service_count": len(services),
        "owners": owners,
        "categories": categories,
        "startup_order": dependency_order(),
        "services": services,
    }


def validate_registry() -> dict:
    order = dependency_order()
    duplicate_routes: Dict[str, List[str]] = {}
    route_to_ids: Dict[str, List[str]] = {}
    for service in _SERVICE_REGISTRY.values():
        route_to_ids.setdefault(service.route_prefix, []).append(service.service_id)
    duplicate_routes = {
        route: service_ids
        for route, service_ids in route_to_ids.items()
        if len(service_ids) > 1
    }
    return {
        "valid": not duplicate_routes,
        "service_count": len(_SERVICE_REGISTRY),
        "startup_order": order,
        "duplicate_routes": duplicate_routes,
    }


def serialize(item: ServiceDefinition) -> dict:
    payload = asdict(item)
    payload["dependencies"] = list(item.dependencies)
    return payload
