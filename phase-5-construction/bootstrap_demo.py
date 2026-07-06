"""Phase 5 bootstrap demo for ATLAS Core.

This script shows the intended startup flow for the first ATLAS services.
It can run in memory-only mode or JSON-backed persistence mode.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from atlas_agent_runtime.service import AgentRuntimeService
from atlas_api.service import ApiService
from atlas_core_runtime.registry import ServiceRegistry
from atlas_diagnostics.service import DiagnosticsService
from atlas_events.json_repository import JsonEventRepository
from atlas_events.models import AtlasEvent
from atlas_events.service import EventBusService
from atlas_knowledge_engine.json_repository import JsonKnowledgeRepository, JsonSourceRepository
from atlas_knowledge_engine.models import KnowledgeEntry, SourcePassport
from atlas_knowledge_engine.service import KnowledgeService
from atlas_memory_engine.json_repository import JsonMemoryRepository
from atlas_memory_engine.models import MemoryRecord, MemoryType
from atlas_memory_engine.service import MemoryService
from atlas_persistence.json_store import JsonFileStore
from atlas_tasks.json_repository import JsonTaskRepository
from atlas_tasks.models import AtlasTask
from atlas_tasks.service import TaskService


def build_registry(data_dir: Path | None = None) -> ServiceRegistry:
    """Create and start the first ATLAS services."""

    registry = ServiceRegistry()

    if data_dir is None:
        event_service = EventBusService()
        task_service = TaskService()
        memory_service = MemoryService()
        knowledge_service = KnowledgeService()
    else:
        store = JsonFileStore(data_dir)
        event_service = EventBusService(repository=JsonEventRepository(store))
        task_service = TaskService(repository=JsonTaskRepository(store))
        memory_service = MemoryService(repository=JsonMemoryRepository(store))
        knowledge_service = KnowledgeService(
            source_repository=JsonSourceRepository(store),
            knowledge_repository=JsonKnowledgeRepository(store),
        )

    services = [
        event_service,
        task_service,
        memory_service,
        knowledge_service,
        AgentRuntimeService(),
        ApiService(),
        DiagnosticsService(),
    ]

    for service in services:
        service.start()
        registry.register(service)

    return registry


def seed_demo_data(registry: ServiceRegistry) -> None:
    """Create one event, task, memory, source, knowledge entry, and API route."""

    events = registry.get("atlas-events")
    tasks = registry.get("atlas-tasks")
    memory = registry.get("atlas-memory-engine")
    knowledge = registry.get("atlas-knowledge-engine")
    api = registry.get("atlas-api")

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
            summary="First ATLAS services were started and seeded.",
            content="This memory records the bootstrap demo for ATLAS Phase 5.",
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
            known_facts=["Service contracts exist", "JSON-backed persistence exists"],
            unknowns=["Full HTTP API layer not implemented", "SQLite persistence not implemented"],
            risks=["Scaffold can grow messy without tests and packaging"],
        )
    )

    api.register_route(
        "/system/health",
        lambda _payload: {
            "services": [report.service_name for report in registry.health_report()],
            "status": "ok",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ATLAS Phase 5 bootstrap demo.")
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Save demo records through JSON repositories.",
    )
    parser.add_argument(
        "--data-dir",
        default="atlas-data/local/bootstrap-demo",
        help="Directory for JSON persistence when --persist is used.",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.persist else None
    registry = build_registry(data_dir=data_dir)
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

    api = registry.get("atlas-api")
    print("\nAPI demo:")
    print(api.call("/system/health"))

    if data_dir is not None:
        print(f"\nPersistent JSON data written to: {data_dir}")


if __name__ == "__main__":
    main()
