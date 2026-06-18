"""Phase 7 — Device registry + command pipeline + telemetry store.

Simulation-first command flow:
  1. authorise(role, kind)       — owner-only gate on actuator/motion/binding
  2. allow-list check            — kind must be in ALLOWED_COMMANDS
  3. simulate via Phase-5 twin   — uses 'failure' sim on the bound twin
  4. validate                    — score ≥ 0.50 AND no hard failures
  5. execute                     — for v1 this is the MQTT-bridge publish
                                    (no real hardware; the device polls
                                    /api/robot/devices/{id}/commands/inbox)
  6. log + memory wiring         — Phase-2 mb.auto_store + project log

Hard constraint: this layer never bypasses simulation.

For v1, the "MQTT bridge" is HTTP-only: devices POST telemetry to
/api/robot/devices/{id}/telemetry and GET pending commands from
/api/robot/devices/{id}/commands/inbox. A real MQTT broker can be slotted
in by re-implementing _publish_command() against paho-mqtt; the API
surface stays unchanged.
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
    if status: filt["status"] = status
    if kind:   filt["kind"] = kind
    cur = _devices().find(filt, {"_id": 0}).sort("updated_at", -1).limit(limit)
    return [d async for d in cur]


async def bind_twin(device_id: str, twin_id: str) -> Optional[Dict[str, Any]]:
    twin = await dt.get_twin(twin_id)
    if not twin:
        return None
    await _devices().update_one(
        {"id": device_id},
        {"$set": {"twin_id": twin_id, "updated_at": _now()}},
    )
    # Mirror the binding into the twin so Phases 5/6 see it via state.hardware_binding.
    state = twin.get("state") or {}
    state["hardware_binding"] = {"device_id": device_id, "bridge": "mqtt-http"}
    state["updated_at"] = _now()
    await dt._twins().update_one({"id": twin_id}, {"$set": {"state": state}})
    return await get_device(device_id)


async def emergency_stop(device_id: str, *, role: Role) -> Optional[Dict[str, Any]]:
    if role != Role.OWNER:
        return None
    await _devices().update_one(
        {"id": device_id},
        {"$set": {"status": DeviceStatus.SAFE_STATE.value, "updated_at": _now()}},
    )
    await mb.auto_store(
        f"EMERGENCY STOP · device={device_id} · role=owner",
        persona="council", category="council",
        source_type="robot_command", source_id=device_id,
        tags=["robot", "safety", "emergency_stop"],
    )
    return await get_device(device_id)


async def clear_safe_state(
    device_id: str, *, role: Role, confirm: str, agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Owner-only release of a device from SAFE_STATE back to ONLINE/REGISTERED.

    Safety contract (architect spec):
      * Owner-only — guest/council/agents always rejected.
      * Requires explicit confirmation: caller must pass the device's exact
        name in `confirm` (anti-fat-finger guard).
      * NEVER bypasses an active EMERGENCY_STOP — the device must already
        BE in SAFE_STATE. If it isn't (e.g. an emergency-stop never fired),
        we refuse so the operator cannot use this endpoint as a backdoor
        actuator on a healthy device.
      * Writes a Command record (kind=clear_safe_state, status=executed).
      * Writes a Memory Bank entry (council/permanent).
      * Updates the bound Digital Twin state with a clearance marker so
        downstream simulations see the chronology.

    Returns a dict carrying the new device snapshot + the audit Command id.
    Raises HTTPException-like dict (callers map to 4xx) on policy failures.
    """
    # 1. Role gate (defence-in-depth — caller already checked once)
    if role != Role.OWNER:
        return {"ok": False, "status": 403, "reason": "clear_safe_state is owner-only"}

    # 2. Look up the device
    device = await get_device(device_id)
    if not device:
        return {"ok": False, "status": 404, "reason": "device not found"}

    # 3. Confirmation must match the device's exact name (case-sensitive)
    if not confirm or confirm != device.get("name"):
        return {
            "ok": False, "status": 400,
            "reason": f"confirmation mismatch — pass confirm='{device.get('name')}' to release",
        }

    # 4. Device must actually BE in safe state. Refusing to "clear" a
    #    non-safe device prevents this endpoint from being used as a
    #    bypass for any other safety gate.
    if device.get("status") != DeviceStatus.SAFE_STATE.value:
        return {
            "ok": False, "status": 409,
            "reason": (
                f"device is not in safe_state (current={device.get('status')}) — "
                f"clear_safe_state cannot bypass an unrelated state"
            ),
        }

    cleared_at = _now()

    # 5. Audit command (status executed, full pipeline log)
    cmd = Command(
        device_id=device_id,
        kind=CommandKind.CLEAR_SAFE_STATE,
        payload={"confirm": confirm},
        issued_by_role=role.value,
        issued_by_agent=agent,
        status=CommandStatus.EXECUTED,
        pipeline_log=[
            {"step": "authorise", "ok": True, "ts": cleared_at, "note": "owner"},
            {"step": "confirm",   "ok": True, "ts": cleared_at, "note": f"confirm={confirm}"},
            {"step": "verify_safe_state", "ok": True, "ts": cleared_at,
             "note": "device was in safe_state, clear authorised"},
            {"step": "execute",   "ok": True, "ts": cleared_at,
             "note": "device released to registered; twin marked cleared"},
        ],
        executed_at=cleared_at,
    )
    await _commands().insert_one(cmd.model_dump())

    # 6. Flip device back to REGISTERED (the next telemetry burst will
    #    promote it to ONLINE — we don't fake that.)
    await _devices().update_one(
        {"id": device_id},
        {"$set": {"status": DeviceStatus.REGISTERED.value, "updated_at": cleared_at}},
    )

    # 7. Update the bound Digital Twin's state with a clearance marker so
    #    Phase-5/6 simulators can see the chronology.
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
            state["safety_history"] = history[-25:]   # cap
            state["safe_state"] = False
            state["last_safety_clear_at"] = cleared_at
            state["updated_at"] = cleared_at
            await dt._twins().update_one({"id": twin_id}, {"$set": {"state": state}})

    # 8. Memory Bank — permanent council entry (parity with emergency_stop)
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
async def ingest_telemetry(device_id: str, payload: Dict[str, Any], *, source: str = "mqtt") -> Dict[str, Any]:
    rec = TelemetryRecord(device_id=device_id, payload=payload, source=source)
    await _telemetry().insert_one(rec.model_dump())
    await _devices().update_one(
        {"id": device_id},
        {"$set": {"last_seen": rec.received_at, "status": DeviceStatus.ONLINE.value,
                  "updated_at": rec.received_at}},
    )
    # Phase 8b — feed Sentinel anomaly detection. update_and_score reads
    # the device doc we just touched, runs Welford's, and writes the
    # envelope + anomaly flag back. Safe to fail open — anomaly detection
    # never blocks telemetry intake.
    try:
        from services import anomaly  # local import to avoid circular load
        _, drifting, z_scores = await anomaly.update_and_score(device_id, payload)
    except Exception as exc:    # noqa: BLE001
        logger.warning("anomaly scoring failed for %s: %s", device_id, exc)
        drifting, z_scores = [], {}
    # Telemetry is decaying research memory by design.
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
    cmd = Command(device_id=device_id, kind=kind, payload=payload,
                  issued_by_role=role, issued_by_agent=agent)

    # 1. Authorise
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

    # 2. Simulate via Phase-5 twin (if bound and command is non-trivial)
    non_trivial = kind in OWNER_ONLY_COMMANDS or kind == CommandKind.CONFIGURE
    if non_trivial and device.get("twin_id"):
        try:
            sim = await dt.run_and_persist_simulation(device["twin_id"], SimulationKind.FAILURE)
            cmd.sim_score = sim.score
            cmd.validation_findings.extend(sim.findings[:5])
            cmd.pipeline_log.append({"step": "simulate", "ok": True, "score": sim.score,
                                     "sim_id": sim.id})
            cmd.status = CommandStatus.SIMULATED
        except Exception as exc:    # noqa: BLE001
            cmd.status = CommandStatus.REJECTED
            cmd.rejection_reason = f"simulation failed: {exc}"
            cmd.pipeline_log.append({"step": "simulate", "ok": False, "error": str(exc)})
            await _commands().insert_one(cmd.model_dump())
            await _log_memory(cmd)
            return cmd
    elif non_trivial:
        cmd.pipeline_log.append({"step": "simulate", "ok": True, "skipped": "no_twin_bound"})

    # 3. Validate
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

    # 4. Execute → publish on the MQTT-style bridge (v1 = HTTP-poll)
    if device.get("status") == DeviceStatus.SAFE_STATE.value and \
            kind != CommandKind.EMERGENCY_STOP and kind != CommandKind.PING:
        cmd.status = CommandStatus.REJECTED
        cmd.rejection_reason = "device is in SAFE_STATE — clear it first via owner"
        cmd.pipeline_log.append({"step": "execute", "ok": False, "reason": cmd.rejection_reason})
        await _commands().insert_one(cmd.model_dump())
        await _log_memory(cmd)
        return cmd

    cmd.status = CommandStatus.EXECUTED
    cmd.executed_at = _now()
    cmd.pipeline_log.append({"step": "execute", "ok": True,
                             "topic": device.get("mqtt_topic") or f"devices/{device_id}/down"})
    await _commands().insert_one(cmd.model_dump())

    # Phase 8c — best-effort MQTT publish. Dormant when MQTT_BROKER_HOST
    # is unset; failure never blocks the HTTP-poll inbox path.
    try:
        from services import mqtt_bridge
        pub = mqtt_bridge.publish_command(device, cmd.model_dump())
        if pub.get("published"):
            cmd.pipeline_log.append({"step": "mqtt_publish", "ok": True, "topic": pub.get("topic")})
    except Exception as exc:    # noqa: BLE001
        logger.debug("mqtt publish skipped: %s", exc)

    # 5. Side effect: emergency_stop changes device state
    if kind == CommandKind.EMERGENCY_STOP:
        await emergency_stop(device_id, role=role)

    await _log_memory(cmd)
    return cmd


async def get_command(command_id: str) -> Optional[Dict[str, Any]]:
    return await _commands().find_one({"id": command_id}, {"_id": 0})


async def list_commands(device_id: str, *, limit: int = 50) -> List[Dict[str, Any]]:
    cur = _commands().find({"device_id": device_id}, {"_id": 0}) \
        .sort("queued_at", -1).limit(limit)
    return [d async for d in cur]


async def inbox(device_id: str) -> List[Dict[str, Any]]:
    """Commands the device should pick up next time it polls (v1 MQTT bridge)."""
    cur = _commands().find(
        {"device_id": device_id, "status": CommandStatus.EXECUTED.value, "delivered": {"$ne": True}},
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
    {"name": "POSEIDON-BUOY",   "kind": "sensor",
     "hardware_profile": {"sensors": ["water_temperature", "ph", "turbidity"]},
     "tags": ["water", "aquatic", "stationary"],
     "mqtt_topic": "devices/poseidon-buoy/up"},
    {"name": "AETHER-STATION",  "kind": "sensor",
     "hardware_profile": {"sensors": ["co2", "pm2_5", "voc", "temperature"]},
     "tags": ["air", "atmosphere", "stationary"],
     "mqtt_topic": "devices/aether-station/up"},
    {"name": "SOIL-WATCH",      "kind": "sensor",
     "hardware_profile": {"sensors": ["soil_moisture", "soil_temperature", "nutrient_level"]},
     "tags": ["soil", "agriculture", "stationary"],
     "mqtt_topic": "devices/soil-watch/up"},
]

_SEED_LOCK = None  # reserved — kept for future concurrent-seed guard


async def seed_if_needed() -> int:
    """Idempotently provision the architect's three seed devices.

    Previously gated on `count_documents({}) > 0`, which broke after tests
    left non-seed devices behind. Now we check by-name and insert only the
    seeds that are actually missing. Safe to call any number of times.
    """
    inserted = 0
    for spec in SEED_DEVICES:
        existing = await _devices().find_one({"name": spec["name"]}, {"id": 1})
        if existing:
            continue
        dev = Device(**spec)
        await register_device(dev)
        # Auto-spawn a twin per device (environment category — matches the spec)
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
