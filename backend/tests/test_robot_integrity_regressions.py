from unittest.mock import AsyncMock, MagicMock

import pytest

from models.robot_models import CommandKind, DeviceStatus, Role
from services import robot


@pytest.mark.asyncio
async def test_bind_twin_does_not_mutate_twin_for_missing_device(monkeypatch):
    monkeypatch.setattr(robot, "get_device", AsyncMock(return_value=None))
    twin_lookup = AsyncMock(return_value={"id": "twin-1", "state": {}})
    monkeypatch.setattr(robot.dt, "get_twin", twin_lookup)

    result = await robot.bind_twin("missing-device", "twin-1")

    assert result is None
    twin_lookup.assert_not_awaited()


@pytest.mark.asyncio
async def test_mqtt_service_rejects_unknown_device_before_persisting(monkeypatch):
    monkeypatch.setattr(robot, "get_device", AsyncMock(return_value=None))

    with pytest.raises(ValueError, match="not registered"):
        await robot.ingest_telemetry("ghost-device", {"temperature": 21.5}, source="mqtt")


@pytest.mark.asyncio
async def test_emergency_stop_missing_device_writes_no_audit_records(monkeypatch):
    monkeypatch.setattr(robot, "get_device", AsyncMock(return_value=None))
    memory_write = AsyncMock()
    monkeypatch.setattr(robot.mb, "auto_store", memory_write)

    result = await robot.emergency_stop("ghost-device", role=Role.OWNER)

    assert result is None
    memory_write.assert_not_awaited()


@pytest.mark.asyncio
async def test_submit_emergency_stop_reuses_existing_command_record(monkeypatch):
    device = {
        "id": "device-1",
        "name": "TEST-DEVICE",
        "status": DeviceStatus.REGISTERED.value,
        "twin_id": None,
        "mqtt_topic": None,
    }
    monkeypatch.setattr(robot, "get_device", AsyncMock(return_value=device))
    emergency_stop = AsyncMock(return_value=device)
    monkeypatch.setattr(robot, "emergency_stop", emergency_stop)
    monkeypatch.setattr(robot, "_log_memory", AsyncMock())

    collection = MagicMock()
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    monkeypatch.setattr(robot, "_commands", lambda: collection)

    cmd = await robot.submit_command(
        "device-1", CommandKind.EMERGENCY_STOP, {}, role=Role.OWNER,
    )

    assert cmd.status.value == "executed"
    assert collection.insert_one.await_count == 1
    emergency_stop.assert_awaited_once_with(
        "device-1", role=Role.OWNER, enqueue_command=False,
    )
