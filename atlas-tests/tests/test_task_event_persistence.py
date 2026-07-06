"""Tests for task and event JSON persistence repositories."""

from atlas_events.json_repository import JsonEventRepository
from atlas_events.models import AtlasEvent
from atlas_events.service import EventBusService
from atlas_persistence.json_store import JsonFileStore
from atlas_tasks.json_repository import JsonTaskRepository
from atlas_tasks.models import AtlasTask
from atlas_tasks.service import TaskService


def test_task_service_can_persist_tasks_through_json_repository(tmp_path):
    store = JsonFileStore(tmp_path)
    repository = JsonTaskRepository(store)
    service = TaskService(repository=repository)
    service.start()

    task = service.create_task(
        AtlasTask(
            title="Persistent Task Test",
            description="Testing repository-backed task storage.",
            task_type="test_task",
            created_by="test-suite",
        )
    )

    persisted = service.persisted_tasks()

    assert task.title == "Persistent Task Test"
    assert len(persisted) == 1
    assert persisted[0]["title"] == "Persistent Task Test"
    assert persisted[0]["task_type"] == "test_task"


def test_event_bus_service_can_persist_events_through_json_repository(tmp_path):
    store = JsonFileStore(tmp_path)
    repository = JsonEventRepository(store)
    service = EventBusService(repository=repository)
    service.start()

    event = AtlasEvent(
        event_type="test.event.persisted",
        source_service="test-suite",
        payload={"ok": True},
    )
    service.publish(event)

    persisted = service.persisted_events()

    assert len(service.list_events()) == 1
    assert len(persisted) == 1
    assert persisted[0]["event_type"] == "test.event.persisted"
    assert persisted[0]["payload"] == {"ok": True}
