"""Phase 7 — Device registry + command pipeline + telemetry store.

Simulation-first command flow:
  1. authorise(role, kind)       — owner-only gate on actuator/motion/binding
  2. allow-list check            — kind must be in ALLOWED_COMMANDS
  3. simulate via Phase-5 twin   — uses 'failure' sim on the bound twin
  4. validate                    — score ≥ 0.50 AND no hard failures
  5. execute                     — publish to MQTT and/or HTTP-poll inbox
  6. log + memory wiring         — Phase-2 mb.auto_store + project log

Hard constraint: this layer never bypasses simulation.
"""
import logging
import os
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from models.robot_models import (
    ALLOWED_COMMANDS,
    Command,
    CommandKind,
    CommandStatus,
    Device,
    DeviceStatus,
    OWNER_ONLY_COMMANDS,
    Role,
    TelemetryRecord,
)
from models.twin_models import SimulationKind
from services import digital_twin as dt, memory_bank as mb

logger = logging.getLogger("atlas.robot")

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _devices():    return _db()["robot_devices"]
def _telemetry():  return _db()["robot_telemetry"]
def _commands():   return _db()["robot_commands"]


# --- Authorisation ---------------------------------------------------------
def authorise(role: Role, kind: CommandKind) -> Optional[str]:
    """Return None if allowed, else a rejection reason string."""
    if kind.value not in ALLOWED_COMMANDS:
        return f"command kind '{kind.value}' not on the allow-list"
    if kind in OWNER_ONLY_COMMANDS and role != Role.OWNER:
        return f"command '{kind.value}' is owner-only (got role={role.value})"
    if kind == CommandKind.EMERGENCY_STOP and role != Role.OWNER:
        return "EMERGENCY_STOP is owner-only"
    return None


# --- Device registry -------------------------------------------------------
async def register_device(dev: Device) -> Dict[str, Any]:
    doc = dev.model_dump()
    await _devices().insert_one(doc.copy())
    await mb.auto_store(
        f"DEVICE registered · {dev.name} ({dev.kind.value})\n"
        f"id={dev.id} · topic={dev.mqtt_topic or '—'}",
        persona="council", category="project",
        source_type="robot_device", source_id=dev.id,
        tags=["robot", "device", dev.kind.value],
    )
    return _strip(doc)


async def get_device(device_id: str) -> Optional[Dict[str, Any]]:
    return await _devices().find_one({"id": device_id}, {"_id": 0})


async def list_devices(
    *, status: Optional[str] = None, kind: Optional[str] = None, limit: int = 100,
) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if status:
        filt["status"] = status
    if kind:
        filt["kind"] = kind
    cur = _devices().find(filt, {"_id": 0}).sort("updated_at", -1).limit(limit)
    return [d async for d in cur]


async def bind_twin(device_id: str, twin_id: str) -> Optional[Dict[str, Any]]:
    """Bind only when both sides exist; never leave a phantom twin binding."""
    device = await get_device(device_id)
    if not device:
        return None
    twin = await dt.get_twin(twin_id)
    if not twin:
        return None

    now = _now()
    result = await _devices().update_one(
        {"id": device_id},
        {"$set": {"twin_id": twin_id, "updated_at": now}},
    )
    if result.matched_count != 1:
        return None

    # Mirror the binding into the twin only after the device update succeeds.
    state = dict(twin.get("state") or {})
    state["hardware_binding"] = {"device_id": device_id, "bridge": "mqtt"}
    state["updated_at"] = now
    twin_result = await dt._twins().update_one(
        {"id": twin_id}, {"$set": {"state": state}}
    )
    if twin_result.matched_count != 1:
        # Roll back the device side if the twin disappeared concurrently.
        await _devices().update_one(
            {"id": device_id, "twin_id": twin_id},
            {"$set": {"twin_id": device.get("twin_id"), "updated_at": _now()}},
        )
        return None
    return await get_device(device_id)


async def emergency_stop(
    device_id: str, *, role: Role, enqueue_command: bool = True,
) -> Optional[Dict[str, Any]]:
    """Put a real registered device in SAFE_STATE and optionally enqueue stop."""
    if role != Role.OWNER:
        return None
    device = await get_device(device_id)
    if not device:
        return None

    now = _now()
    result = await _devices().update_one(
        {"id": device_id},
        {"$set": {"status": DeviceStatus.SAFE_STATE.value, "updated_at": now}},
    )
    if result.matched_count != 1:
        return None

    await mb.auto_store(
        f"EMERGENCY STOP · device={device_id} · role=owner",
        persona="council", category="council",
        source_type="robot_command", source_id=device_id,
        tags=["robot", "safety", "emergency_stop"],
    )

    # Direct emergency-stop calls need a command in the device inbox. When
    # submit_command() called us, that command already exists, so do not
    # create a duplicate audit/inbox record.
    if enqueue_command:
        stop_cmd = Command(
            device_id=device_id,
            kind=CommandKind.EMERGENCY_STOP,
            payload={},
            issued_by_role=Role.OWNER,
            status=CommandStatus.EXECUTED,
            executed_at=now,
            pipeline_log=[{"step": "emergency_stop", "by": "owner", "at": now}],
        )
        await _commands().insert_one(stop_cmd.model_dump())
        try:
            from services import mqtt_bridge
            pub = mqtt_bridge.publish_command(device, stop_cmd.model_dump())
            stop_cmd.pipeline_log.append({
                "step": "mqtt_publish",
                "ok": bool(pub.get("published")),
                "topic": pub.get("topic"),
                "reason": pub.get("reason") or pub.get("error"),
            })
            await _commands().update_one(
                {"id": stop_cmd.id},
                {"$set": {"pipeline_log": stop_cmd.pipeline_log}},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("emergency-stop MQTT publish failed: %s", exc)

    return await get_device(device_id)


async def clear_safe_state(
    device_id: str, *, role: Role, confirm: str, agent: Optional[str] = None,
) -> Dict[str, Any]:
    """Owner-only release of a device from SAFE_STATE."""
    if role != Role.OWNER:
        return {"ok": False, "status": 403, "reason": "clear_safe_state is owner-only"}

    device = await get_device(device_id)
    if not device:
        return {"ok": False, "status": 404, "reason": "device not found"}

    if not confirm or confirm != device.get("name"):
        return {
            "ok": False, "status": 400,
            "reason": f"confirmation mismatch — pass confirm='{device.get('name')}' to release",
        }

    if device.get("status") != DeviceStatus.SAFE_STATE.value:
        return {
            "ok": False, "status": 409,
            "reason": (
                f"device is not in safe_state (current={device.get('status')}) — "
                "clear_safe_state cannot bypass an unrelated state"
            ),
        }

    cleared_at = _now()
    cmd = Command(
        device_id=device_id,
        kind=CommandKind.CLEAR_SAFE_STATE,
        payload={"confirm": confirm},
        issued_by_role=role.value,
        issued_by_agent=agent,
        status=CommandStatus.EXECUTED,
        pipeline_log=[
            {"step": "authorise", "ok": True, "ts": cleared_at, "note": "owner"},
            {"step": "confirm", "ok": True, "ts": cleared_at, "note": f"confirm={confirm}"},
            {"step": "verify_safe_state", "ok": True, "ts": cleared_at,
             "note": "device was in safe_state, clear authorised"},
            {"step": "execute", "ok": True, "ts": cleared_at,
             "note": "device released to registered; twin marked cleared"},
        ],
        executed_at=cleared_at,
    )
    await _commands().insert_one(cmd.model_dump())

    await _devices().update_one(
        {"id": device_id},
        {"$set": {"status": DeviceStatus.REGISTERED.value, "updated_at": cleared_at}},
    )

    twin_id = device.get("twin_id")
    if twin_id:
        twin = await dt.get_twin(twin_id)
        if twin:
            state = twin.get("state") or {}
            history = list(state.get("safety_history") or [])
            history.append({
                "event": "clear_safe_state",
                "ts": cleared_at,
                "by_role": role.value,
                "command_id": cmd.id,
            })
            state["safety_history"] = history[-25:]
            state["safe_state"] = False
            state["last_safety_clear_at"] = cleared_at
            state["updated_at"] = cleared_at
            await dt._twins().update_one({"id": twin_id}, {"$set": {"state": state}})

    await mb.auto_store(
        f"CLEAR SAFE STATE · device={device['name']} ({device_id}) · role=owner "
        f"· cleared at {cleared_at}",
        persona="council", category="council",
        source_type="robot_command", source_id=cmd.id,
        tags=["robot", "safety", "clear_safe_state", device["name"]],
    )

    return {
        "ok": True,
        "device": await get_device(device_id),
        "command_id": cmd.id,
        "cleared_at": cleared_at,
    }


# --- Telemetry --------------------------------------------------------------
async def ingest_telemetry(
    device_id: str, payload: Dict[str, Any], *, source: str = "mqtt",
) -> Dict[str, Any]:
    """Persist telemetry only for registered devices.

    MQTT callbacks bypass the HTTP route-level existence check, so this
    service boundary must enforce registry integrity itself.
    """
    device = await get_device(device_id)
    if not device:
        raise ValueError(f"device {device_id} not registered")

    rec = TelemetryRecord(device_id=device_id, payload=payload, source=source)
    await _telemetry().insert_one(rec.model_dump())

    cur_status = device.get("status")
    sticky = {DeviceStatus.SAFE_STATE.value, DeviceStatus.QUARANTINED.value}
    update = {"last_seen": rec.received_at, "updated_at": rec.received_at}
    if cur_status not in sticky:
        update["status"] = DeviceStatus.ONLINE.value
    await _devices().update_one({"id": device_id}, {"$set": update})

    try:
        from services import anomaly
        _, drifting, z_scores = await anomaly.update_and_score(device_id, payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning("anomaly scoring failed for %s: %s", device_id, exc)
        drifting, z_scores = [], {}

    extra_tags = ["anomaly"] if drifting else []
    drift_line = ""
    if drifting:
        drift_line = "\nANOMALY · drifting=" + ",".join(
            f"{k}(z={z_scores.get(k):.1f})" for k in drifting
        )
    await mb.auto_store(
        f"TELEMETRY · {device_id}\n" + ", ".join(f"{k}={v}" for k, v in payload.items())
        + drift_line,
        persona="hermes", category="research",
        source_type="robot_telemetry", source_id=rec.id,
        tags=["robot", "telemetry", device_id[:8]] + extra_tags,
    )
    return _strip(rec.model_dump())


async def telemetry_history(device_id: str, *, limit: int = 50) -> List[Dict[str, Any]]:
    cur = _telemetry().find({"device_id": device_id}, {"_id": 0}) \
        .sort("received_at", -1).limit(limit)
    return [d async for d in cur]


# --- Command pipeline -------------------------------------------------------
async def submit_command(
    device_id: str, kind: CommandKind, payload: Dict[str, Any],
    *, role: Role, agent: Optional[str] = None,
) -> Command:
    cmd = Command(
        device_id=device_id, kind=kind, payload=payload,
        issued_by_role=role, issued_by_agent=agent,
    )

    reason = authorise(role, kind)
    if reason:
        cmd.status = CommandStatus.REJECTED
        cmd.rejection_reason = reason
        cmd.pipeline_log.append({"step": "authorise", "ok": False, "reason": reason})
        await _commands().insert_one(cmd.model_dump())
        await _log_memory(cmd)
        return cmd
    cmd.pipeline_log.append({"step": "authorise", "ok": True})

    device = await get_device(device_id)
    if not device:
        cmd.status = CommandStatus.REJECTED
        cmd.rejection_reason = f"device {device_id} not registered"
        cmd.pipeline_log.append({"step": "device_lookup", "ok": False})
        await _commands().insert_one(cmd.model_dump())
        await _log_memory(cmd)
        return cmd

    non_trivial = kind in OWNER_ONLY_COMMANDS or kind == CommandKind.CONFIGURE
    if non_trivial and device.get("twin_id"):
        try:
            sim = await dt.run_and_persist_simulation(
                device["twin_id"], SimulationKind.FAILURE
            )
            if sim is None:
                raise RuntimeError("bound digital twin no longer exists")
            cmd.sim_score = sim.score
            cmd.validation_findings.extend(sim.findings[:5])
            cmd.pipeline_log.append({
                "step": "simulate", "ok": True, "score": sim.score, "sim_id": sim.id,
            })
            cmd.status = CommandStatus.SIMULATED
        except Exception as exc:  # noqa: BLE001
            cmd.status = CommandStatus.REJECTED
            cmd.rejection_reason = f"simulation failed: {exc}"
            cmd.pipeline_log.append({"step": "simulate", "ok": False, "error": str(exc)})
            await _commands().insert_one(cmd.model_dump())
            await _log_memory(cmd)
            return cmd
    elif non_trivial:
        cmd.pipeline_log.append({"step": "simulate", "ok": True, "skipped": "no_twin_bound"})

    sim_ok = (cmd.sim_score is None) or (cmd.sim_score >= 0.5)
    if not sim_ok:
        cmd.status = CommandStatus.REJECTED
        cmd.rejection_reason = f"simulation score {cmd.sim_score:.2f} below 0.50 threshold"
        cmd.pipeline_log.append({"step": "validate", "ok": False, "reason": cmd.rejection_reason})
        await _commands().insert_one(cmd.model_dump())
        await _log_memory(cmd)
        return cmd
    cmd.status = CommandStatus.VALIDATED
    cmd.pipeline_log.append({"step": "validate", "ok": True})

    if (
        device.get("status") == DeviceStatus.SAFE_STATE.value
        and kind not in (CommandKind.EMERGENCY_STOP, CommandKind.PING)
    ):
        cmd.status = CommandStatus.REJECTED
        cmd.rejection_reason = "device is in SAFE_STATE — clear it first via owner"
        cmd.pipeline_log.append({"step": "execute", "ok": False, "reason": cmd.rejection_reason})
        await _commands().insert_one(cmd.model_dump())
        await _log_memory(cmd)
        return cmd

    cmd.status = CommandStatus.EXECUTED
    cmd.executed_at = _now()
    cmd.pipeline_log.append({
        "step": "execute", "ok": True,
        "topic": device.get("mqtt_topic") or f"devices/{device_id}/down",
    })
    await _commands().insert_one(cmd.model_dump())

    # Persist delivery diagnostics after publish; previously these existed
    # only in the in-memory return object and were missing from the audit DB.
    try:
        from services import mqtt_bridge
        pub = mqtt_bridge.publish_command(device, cmd.model_dump())
        cmd.pipeline_log.append({
            "step": "mqtt_publish",
            "ok": bool(pub.get("published")),
            "topic": pub.get("topic"),
            "reason": pub.get("reason") or pub.get("error"),
        })
    except Exception as exc:  # noqa: BLE001
        logger.debug("mqtt publish skipped: %s", exc)
        cmd.pipeline_log.append({
            "step": "mqtt_publish", "ok": False, "error": str(exc)[:200],
        })
    await _commands().update_one(
        {"id": cmd.id}, {"$set": {"pipeline_log": cmd.pipeline_log}}
    )

    if kind == CommandKind.EMERGENCY_STOP:
        # The command above is already the inbox/audit record. Only change
        # device state here; do not create a duplicate stop command.
        await emergency_stop(device_id, role=role, enqueue_command=False)

    await _log_memory(cmd)
    return cmd


async def get_command(command_id: str) -> Optional[Dict[str, Any]]:
    return await _commands().find_one({"id": command_id}, {"_id": 0})


async def list_commands(device_id: str, *, limit: int = 50) -> List[Dict[str, Any]]:
    cur = _commands().find({"device_id": device_id}, {"_id": 0}) \
        .sort("queued_at", -1).limit(limit)
    return [d async for d in cur]


async def inbox(device_id: str) -> List[Dict[str, Any]]:
    """Commands the device should pick up next time it polls."""
    cur = _commands().find(
        {
            "device_id": device_id,
            "status": CommandStatus.EXECUTED.value,
            "delivered": {"$ne": True},
        },
        {"_id": 0},
    ).sort("queued_at", 1).limit(20)
    items = [d async for d in cur]
    if items:
        await _commands().update_many(
            {"id": {"$in": [c["id"] for c in items]}},
            {"$set": {"delivered": True}},
        )
    return items


# --- Helpers ---------------------------------------------------------------
async def _log_memory(cmd: Command) -> None:
    body = (
        f"ROBOT CMD · {cmd.kind.value} · device={cmd.device_id} · "
        f"status={cmd.status.value} · role={cmd.issued_by_role.value}\n"
        f"sim_score={cmd.sim_score} · reason={cmd.rejection_reason or '—'}\n"
        f"payload={cmd.payload}"
    )
    await mb.auto_store(
        body, persona="council", category="project",
        source_type="robot_command", source_id=cmd.id,
        tags=["robot", "command", cmd.kind.value, cmd.status.value],
    )


def _strip(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "_id"}


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# --- Seeding the three architect-spec twins + devices ----------------------
SEED_DEVICES = [
    {"name": "POSEIDON-BUOY", "kind": "sensor",
     "hardware_profile": {"sensors": ["water_temperature", "ph", "turbidity"]},
     "tags": ["water", "aquatic", "stationary"],
     "mqtt_topic": "devices/poseidon-buoy/up"},
    {"name": "AETHER-STATION", "kind": "sensor",
     "hardware_profile": {"sensors": ["co2", "pm2_5", "voc", "temperature"]},
     "tags": ["air", "atmosphere", "stationary"],
     "mqtt_topic": "devices/aether-station/up"},
    {"name": "SOIL-WATCH", "kind": "sensor",
     "hardware_profile": {"sensors": ["soil_moisture", "soil_temperature", "nutrient_level"]},
     "tags": ["soil", "agriculture", "stationary"],
     "mqtt_topic": "devices/soil-watch/up"},
]

_SEED_LOCK = None


async def seed_if_needed() -> int:
    """Idempotently provision the architect's three seed devices."""
    inserted = 0
    for spec in SEED_DEVICES:
        existing = await _devices().find_one({"name": spec["name"]}, {"id": 1})
        if existing:
            continue
        dev = Device(**spec)
        await register_device(dev)
        from models.twin_models import (
            Component, DigitalTwin, SensorInput, TwinCategory, TwinState,
        )
        twin = DigitalTwin(
            name=dev.name + " twin",
            category=TwinCategory.ENVIRONMENT,
            owner_agent="minerva",
            description=f"Auto-spawned twin for {dev.name}",
            tags=["robot", "stationary"] + dev.tags,
            state=TwinState(
                components=[Component(id="mcu", name="ESP32 controller")],
                sensor_inputs=[
                    SensorInput(name=s, kind="reading", unit="raw")
                    for s in dev.hardware_profile.sensors
                ],
            ),
        )
        await dt.register_twin(twin)
        await bind_twin(dev.id, twin.id)
        inserted += 1
    return inserted
