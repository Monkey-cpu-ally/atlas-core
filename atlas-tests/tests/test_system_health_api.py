"""Smoke tests for the framework-neutral system health API."""

from atlas_api.system_health import build_system_health_response
from atlas_core_runtime.registry import ServiceRegistry
from atlas_events.service import EventBusService
from atlas_tasks.service import TaskService


def test_system_health_response_is_healthy_when_services_are_started():
    registry = ServiceRegistry()

    events = EventBusService()
    tasks = TaskService()

    events.start()
    tasks.start()

    registry.register(events)
    registry.register(tasks)

    response = build_system_health_response(registry)

    assert response.status == "healthy"
    assert {service.service_name for service in response.services} == {"atlas-events", "atlas-tasks"}
    assert all(service.status == "healthy" for service in response.services)
