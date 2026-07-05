"""Phase 5 bootstrap demo for ATLAS Core.

This script shows the intended startup flow for the first in-memory services.
It assumes the service packages are importable through PYTHONPATH or a future workspace setup.
"""

from atlas_agent_runtime.service import AgentRuntimeService
from atlas_core_runtime.registry import ServiceRegistry
from atlas_diagnostics.service import DiagnosticsService
from atlas_events.models import AtlasEvent
from atlas_events.service import EventBusService
from atlas_knowledge_engine.models import KnowledgeEntry, SourcePassport
from atlas_knowledge_engine.service import KnowledgeService
from atlas_memory_engine.models import MemoryRecord, MemoryType
from atlas_memory_engine.service import MemoryService
from atlas_tasks.models import AtlasTask
from atlas_tasks.service import TaskService


def build_registry() -> ServiceRegistry:
    """Create and start the first ATLAS services."""

    registry = ServiceRegistry()
    services = [
        EventBusService(),
        TaskService(),
        MemoryService(),
        KnowledgeService(),
        AgentRuntimeService(),
        DiagnosticsService(),
    ]

    for service in services:
        service.start()
        registry.register(service)

    return registry


def seed_demo_data(registry: ServiceRegistry) -> None:
    """Create one event, task, memory, source, and knowledge entry."""

    events = registry.get("atlas-events")
    tasks = registry.get("atlas-tasks")
    memory = registry.get("atlas-memory-engine")
    knowledge = registry.get("atlas-knowledge-engine")

    events.publish(
        AtlasEvent(
            event_type="system.bootstrap.completed",
            source_service="phase-5-bootstrap",
            payload={"message": "ATLAS bootstrap demo completed"},
        )
    )

    tasks.create_task(
        AtlasTask(
            title="Verify ATLAS Core scaffold",
            description="Confirm the first runtime services can start and report health.",
            task_type="system_task",
            created_by="phase-5-bootstrap",
            assigned_to="Council",
        )
    )

    memory.create_record(
        MemoryRecord(
            title="Phase 5 Bootstrap Demo",
            memory_type=MemoryType.PROJECT,
            summary="First in-memory services were started and seeded.",
            content="This memory records the first bootstrap demo for ATLAS Phase 5.",
            created_by="phase-5-bootstrap",
            related_projects=["ATLAS Core"],
        )
    )

    source = knowledge.add_source(
        SourcePassport(
            title="ATLAS Phase 5 Construction Notes",
            source_type="ATLAS Research",
            creator_or_organization="ATLAS",
            primary_knowledge_bank="Software Engineering",
            related_knowledge_banks=["Artificial Intelligence", "Systems Engineering"],
            status="approved",
        )
    )

    knowledge.add_entry(
        KnowledgeEntry(
            title="ATLAS Core Runtime Scaffold",
            summary="The first runtime service contracts and in-memory services define the foundation of ATLAS Core.",
            primary_knowledge_bank="Software Engineering",
            created_by="phase-5-bootstrap",
            source_ids=[source.source_id],
            known_facts=["Service contracts exist", "In-memory service skeletons exist"],
            unknowns=["Persistence layer not implemented", "API layer not implemented"],
            risks=["Scaffold can grow messy without tests and packaging"],
        )
    )


def main() -> None:
    registry = build_registry()
    seed_demo_data(registry)

    diagnostics = registry.get("atlas-diagnostics")
    reports = registry.health_report()
    diagnostics.collect(reports)

    print("ATLAS Phase 5 bootstrap services:")
    for service_name in registry.list_services():
        print(f"- {service_name}")

    print("\nHealth reports:")
    for report in diagnostics.last_reports():
        print(f"- {report.service_name}: {report.status.value} — {report.message}")


if __name__ == "__main__":
    main()
