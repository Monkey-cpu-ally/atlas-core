"""Phase 7 — Robot Control routes (prefix /api/robot).

Local-only by design; no public endpoint. Role is passed via the
`X-Atlas-Role` header (owner / council / ajani / minerva / hermes / guest).
For v1 this is a soft gate — a future iteration can swap it for JWT once
the deployment moves beyond the architect's local network.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field

from models.robot_models import (
    Command,
    CommandKind,
    Device,
    DeviceKind,
    DeviceStatus,
    HardwareProfile,
    Role,
)
from services import robot
from services import anomaly

router = APIRouter(prefix="/api/robot", tags=["RobotControl"])


def _role_from_header(x_atlas_role: Optional[str] = Header(default=None)) -> Role:
    if not x_atlas_role:
        return Role.GUEST
    try:
        return Role(x_atlas_role.lower().strip())
    except ValueError:
        return Role.GUEST


# --- Bootstrap -------------------------------------------------------------
@router.post("/seed")
async def seed():
    inserted = await robot.seed_if_needed()
    return {"seeded_devices": inserted}


@router.get("/roles")
async def roles():
    return {"roles": [r.value for r in Role],
            "owner_only_commands": [c.value for c in robot.OWNER_ONLY_COMMANDS]}


# --- Devices ---------------------------------------------------------------
class RegisterDeviceRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    kind: DeviceKind
    mqtt_topic: Optional[str] = None
    hardware_profile: HardwareProfile = Field(default_factory=HardwareProfile)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


@router.post("/devices")
async def register(req: RegisterDeviceRequest, role: Role = Depends(_role_from_header)):
    if role != Role.OWNER:
        raise HTTPException(403, "device registration is owner-only")
    dev = Device(**req.model_dump())
    persisted = await robot.register_device(dev)

    # Phase 8f — mint an mTLS cert pack for this device. The CA is local
    # to /app/backend/_data/mtls/. The PRIVATE KEY is returned ONCE in
    # this response and never stored server-side; the architect must
    # capture it now (this is the same UX as AWS/GCP TLS issuance).
    try:
        from services import mtls
        pack = mtls.issue_device_cert(persisted["id"], persisted["name"])
        # Persist just the cert fingerprint so future requests can be
        # checked when MTLS_ENFORCE=true is set.
        await robot._devices().update_one(
            {"id": persisted["id"]},
            {"$set": {
                "mtls_fingerprint": pack["fingerprint_sha256"],
                "mtls_serial": pack["serial_number"],
                "mtls_not_after": pack["not_after"],
            }},
        )
        persisted["mtls"] = {
            "cert_pem": pack["cert_pem"],
            "key_pem": pack["key_pem"],
            "ca_pem": pack["ca_pem"],
            "fingerprint_sha256": pack["fingerprint_sha256"],
            "not_after": pack["not_after"],
            "warning": (
                "Save these now — the private key will NOT be shown again. "
                "Flash cert_pem + key_pem onto the device; trust ca_pem in "
                "the device's mbedtls store. Enforcement is dormant in v1 "
                "(set MTLS_ENFORCE=true to require client certs on "
                "telemetry + inbox)."
            ),
        }
    except Exception as exc:    # noqa: BLE001
        # Cert issuance failure must NOT block device registration —
        # operator can re-issue via /mtls/issue later.
        import logging
        logging.getLogger("atlas.robot").warning(
            "mTLS issuance failed for %s: %s", persisted["id"], exc,
        )
        persisted["mtls"] = {"error": str(exc)[:200]}
    return persisted


@router.post("/devices/{device_id}/mtls/issue")
async def reissue_cert(device_id: str, role: Role = Depends(_role_from_header)):
    """Owner-only — re-mint the cert pack for an existing device (rotation
    or after a private-key loss). Returns the same envelope as the
    register endpoint's `mtls` block."""
    if role != Role.OWNER:
        raise HTTPException(403, "mTLS re-issue is owner-only")
    dev = await robot.get_device(device_id)
    if not dev:
        raise HTTPException(404, "device not found")
    from services import mtls
    pack = mtls.issue_device_cert(dev["id"], dev["name"])
    await robot._devices().update_one(
        {"id": dev["id"]},
        {"$set": {
            "mtls_fingerprint": pack["fingerprint_sha256"],
            "mtls_serial": pack["serial_number"],
            "mtls_not_after": pack["not_after"],
        }},
    )
    return pack


@router.get("/mtls/ca")
async def mtls_ca():
    """Return the ATLAS root CA in PEM so devices can trust the server
    (when the inbox is moved behind HTTPS) and operators can sanity-check
    the chain."""
    from services import mtls
    return {
        "ca_pem": mtls.get_ca_pem(),
        "enforced": mtls.is_enforced(),
    }


@router.get("/devices")
async def list_devices(
    status: Optional[DeviceStatus] = None,
    kind: Optional[DeviceKind] = None,
    limit: int = Query(50, ge=1, le=200),
):
    rows = await robot.list_devices(
        status=status.value if status else None,
        kind=kind.value if kind else None,
        limit=limit,
    )
    return {"count": len(rows), "items": rows}


@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    d = await robot.get_device(device_id)
    if not d:
        raise HTTPException(404, "device not found")
    return d


class BindTwinRequest(BaseModel):
    twin_id: str


@router.post("/devices/{device_id}/bind-twin")
async def bind_twin(device_id: str, req: BindTwinRequest,
                    role: Role = Depends(_role_from_header)):
    if role != Role.OWNER:
        raise HTTPException(403, "binding is owner-only")
    d = await robot.bind_twin(device_id, req.twin_id)
    if not d:
        raise HTTPException(404, "device or twin not found")
    return d


# --- Telemetry -------------------------------------------------------------
class TelemetryRequest(BaseModel):
    payload: Dict[str, Any]
    source: str = "mqtt"


@router.post("/devices/{device_id}/telemetry")
async def push_telemetry(device_id: str, req: TelemetryRequest):
    """Device push — no role check; devices on the local LAN report freely.
    The role check happens on COMMANDS, not on telemetry reports."""
    d = await robot.get_device(device_id)
    if not d:
        raise HTTPException(404, "device not found")
    return await robot.ingest_telemetry(device_id, req.payload, source=req.source)


@router.get("/devices/{device_id}/telemetry")
async def history(device_id: str, limit: int = Query(50, ge=1, le=500)):
    return {"items": await robot.telemetry_history(device_id, limit=limit)}


# --- Commands --------------------------------------------------------------
class CommandRequest(BaseModel):
    kind: CommandKind
    payload: Dict[str, Any] = Field(default_factory=dict)
    issuing_agent: Optional[str] = None     # 'ajani'|'minerva'|'hermes'|'council'


@router.post("/devices/{device_id}/command")
async def submit(device_id: str, req: CommandRequest,
                 role: Role = Depends(_role_from_header)):
    cmd: Command = await robot.submit_command(
        device_id, req.kind, req.payload,
        role=role, agent=req.issuing_agent,
    )
    if cmd.status.value == "rejected" and cmd.rejection_reason \
            and "owner-only" in cmd.rejection_reason:
        # Surface as 403 so callers can branch on it.
        return cmd.model_dump()      # still 200 — body has full context
    return cmd.model_dump()


@router.get("/devices/{device_id}/commands")
async def list_commands(device_id: str, limit: int = Query(50, ge=1, le=200)):
    return {"items": await robot.list_commands(device_id, limit=limit)}


@router.get("/devices/{device_id}/commands/inbox")
async def inbox(device_id: str):
    """Device-side poll endpoint. Returns commands that have been executed
    but not yet delivered to the device. Each call marks them delivered."""
    return {"items": await robot.inbox(device_id)}


@router.get("/commands/{command_id}")
async def get_command(command_id: str):
    c = await robot.get_command(command_id)
    if not c:
        raise HTTPException(404, "command not found")
    return c


@router.post("/devices/{device_id}/emergency-stop")
async def stop(device_id: str, role: Role = Depends(_role_from_header)):
    if role != Role.OWNER:
        raise HTTPException(403, "EMERGENCY_STOP is owner-only")
    d = await robot.emergency_stop(device_id, role=role)
    if not d:
        raise HTTPException(404, "device not found")
    return d


class ClearSafeStateRequest(BaseModel):
    confirm: str = Field(..., description="Must equal the device's exact name as anti-fat-finger guard")


@router.post("/devices/{device_id}/clear-safe-state")
async def clear_safe_state(
    device_id: str,
    body: ClearSafeStateRequest,
    role: Role = Depends(_role_from_header),
):
    """Owner-only release of a device from SAFE_STATE.

    Hard rules (architect spec):
      * Owner role required (otherwise 403)
      * Body must include `confirm` equal to the device's exact `name`
        (anti-fat-finger; otherwise 400)
      * Device must already be in `safe_state` (otherwise 409 — this
        endpoint never bypasses any other safety gate)
      * Emits a Command record (kind=clear_safe_state, status=executed)
      * Patches the bound Digital Twin's `state.safety_history`
      * Writes a permanent council Memory Bank entry
    """
    if role != Role.OWNER:
        raise HTTPException(403, "CLEAR_SAFE_STATE is owner-only")
    res = await robot.clear_safe_state(device_id, role=role, confirm=body.confirm)
    if not res.get("ok"):
        raise HTTPException(res.get("status", 400), res.get("reason", "clear failed"))
    return res


@router.get("/mqtt/status")
async def mqtt_status():
    """Operational status of the MQTT bridge. Dormant when
    MQTT_BROKER_HOST is unset — Atlas falls back to HTTP-poll inbox."""
    from services import mqtt_bridge
    return mqtt_bridge.status()


# ---------------------------------------------------------------------------
# Phase 8b — Sentinel anomaly endpoints
# ---------------------------------------------------------------------------
@router.get("/devices/{device_id}/envelope")
async def get_envelope(device_id: str):
    """Return the learned rolling envelope per telemetry key + the
    current anomaly flag (if any). HUD Sentinel popovers can hit this
    to show 'mean ± stddev' bands next to live readings."""
    out = await anomaly.envelope_summary(device_id)
    if not out:
        raise HTTPException(404, "device not found")
    return out


@router.post("/devices/{device_id}/envelope/reset")
async def reset_envelope(device_id: str, role: Role = Depends(_role_from_header)):
    """Owner-only — wipe the envelope (e.g. after an intentional change
    to the device's operating range). Anomaly flag is also cleared."""
    if role != Role.OWNER:
        raise HTTPException(403, "envelope reset is owner-only")
    ok = await anomaly.reset_envelope(device_id)
    if not ok:
        raise HTTPException(404, "device not found")
    return {"ok": True, "device_id": device_id}


@router.post("/devices/{device_id}/ask-council")
async def ask_council(device_id: str):
    """One-click 'ask the Council' for the Sentinel anomaly popover.
    Fans out to /api/persona/council/chat with a question framed
    around the device's current state + drifting keys (if any).
    Returns the council response verbatim so the HUD can show it inline.
    """
    dev = await robot.get_device(device_id)
    if not dev:
        raise HTTPException(404, "device not found")

    state = dev.get("state") or {}
    anomaly_blk = state.get("anomaly") or {}
    last_tel = await robot.telemetry_history(device_id, limit=1)
    last_payload = (last_tel[0]["payload"] if last_tel else {})

    if anomaly_blk:
        drift_desc = ", ".join(
            f"{k} (z={anomaly_blk.get('z_scores', {}).get(k, '?'):.2f})"
            for k in anomaly_blk.get("drifting_keys") or []
        )
        question = (
            f"Device {dev['name']} ({dev.get('kind')}) is showing anomalous "
            f"telemetry. Drifting keys: {drift_desc}. Latest reading: "
            f"{last_payload}. Should we investigate, recalibrate, or take "
            f"protective action? Be brief and decisive."
        )
    else:
        question = (
            f"Quick check on {dev['name']} ({dev.get('kind')}). Latest "
            f"reading: {last_payload}. Status: {dev.get('status')}. Anything "
            f"to watch out for? Be brief."
        )

    # Lazy-import the persona_chat service to avoid bootstrap-time coupling.
    from services import persona_chat
    from models.persona_models import ChatRequest
    res = await persona_chat.chat_any(
        "council",
        ChatRequest(message=question, memory_top_k=3, knowledge_top_k=3),
    )
    return {
        "device_id": device_id,
        "device_name": dev["name"],
        "anomaly": anomaly_blk or None,
        "question": question,
        "council": res.model_dump(),
    }
