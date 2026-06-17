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
    return await robot.register_device(dev)


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
