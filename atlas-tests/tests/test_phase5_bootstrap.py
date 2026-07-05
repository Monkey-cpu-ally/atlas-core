"""Smoke tests for the first ATLAS Phase 5 services."""

from atlas_agent_runtime.service import AgentRuntimeService
from atlas_core_runtime.registry import ServiceRegistry
from atlas_events.models import AtlasEvent
from atlas_events.service import EventBusService
from atlas_knowledge_engine.models import KnowledgeEntry, SourcePassport
from atlas_knowledge_engine.service import KnowledgeService
from atlas_memory_engine.models import MemoryRecord, MemoryType
from atlas_memory_engine.service import MemoryService
from atlas_tasks.models import AtlasTask
from atlas_tasks.service import TaskService


def test_phase5_services_can_start_and_store_records():
    registry = ServiceRegistry()

    event_service = EventBusService()
    task_service = TaskService()
    memory_service = MemoryService()
    knowledge_service = KnowledgeService()
    agent_service = AgentRuntimeService()

    for service in [event_service, task_service, memory_service, knowledge_service, agent_service]:
        service.start()
        registry.register(service)

    event_service.publish(
        AtlasEvent(
            event_type="test.event",
            source_service="test-suite",
            payload={"ok": True},
        )
    )
    assert len(event_service.list_events()) == 1

    task = task_service.create_task(
        AtlasTask(
            title="Smoke Test Task",
            description="Verify task storage.",
            task_type="test_task",
            created_by="test-suite",
        )
    )
    assert task_service.get_task(task.task_id).title == "Smoke Test Task"

    memory = memory_service.create_record(
        MemoryRecord(
            title="Smoke Test Memory",
            memory_type=MemoryType.PROJECT,
            summary="Testing memory storage.",
            content="Memory content.",
            created_by="test-suite",
        )
    )
    assert memory_service.get_record(memory.memory_id).title == "Smoke Test Memory"

    source = knowledge_service.add_source(
        SourcePassport(
            title="Smoke Test Source",
            source_type="Test",
            creator_or_organization="test-suite",
            primary_knowledge_bank="Software Engineering",
        )
    )
    assert knowledge_service.get_source(source.source_id).title == "Smoke Test Source"

    entry = knowledge_service.add_entry(
        KnowledgeEntry(
            title="Smoke Test Entry",
            summary="Testing knowledge storage.",
            primary_knowledge_bank="Software Engineering",
            created_by="test-suite",
            source_ids=[source.source_id],
        )
    )
    assert knowledge_service.get_entry(entry.entry_id).title == "Smoke Test Entry"

    agent_names = {agent.name for agent in agent_service.list_agents()}
    assert {"Hermes", "Minerva", "Ajani", "Council"}.issubset(agent_names)

    assert set(registry.list_services()) == {
        "atlas-agent-runtime",
        "atlas-events",
        "atlas-knowledge-engine",
        "atlas-memory-engine",
        "atlas-tasks",
    }
