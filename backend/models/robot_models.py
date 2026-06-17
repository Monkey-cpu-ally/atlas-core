"""Phase 7 — Robot Control Layer models.

Hardware-agnostic by design. The runtime is MQTT-style HTTP bridge (no
broker required for v1) so an ESP32 / Raspberry Pi can POST telemetry and
poll for commands without bringing in mosquitto. ROS2 compatibility can
slot in later via an adapter.

Hard constraints from architect spec:
  * simulation-first  — every command flows Twin → Sim → Validate → Execute
  * owner-locked       — binding / actuators / motion / firmware are owner-only
  * allow-list         — every command kind must be explicitly allowed
  * full audit trail   — every command logged + persisted
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Role(str, Enum):
    OWNER   = "owner"
    COUNCIL = "council"
    AJANI   = "ajani"
    MINERVA = "minerva"
    HERMES  = "hermes"
    GUEST   = "guest"


class DeviceKind(str, Enum):
    ESP32        = "esp32"
    RASPBERRY_PI = "raspberry_pi"
    USB_CAMERA   = "usb_camera"
    SENSOR       = "sensor"
    GATEWAY      = "gateway"


class DeviceStatus(str, Enum):
    REGISTERED = "registered"      # known but never seen
    ONLINE     = "online"
    OFFLINE    = "offline"
    SAFE_STATE = "safe_state"      # post-EMERGENCY-STOP
    QUARANTINED = "quarantined"    # owner blocked it


class CommandKind(str, Enum):
    # Read-only — agents may issue
    READ_TELEMETRY    = "read_telemetry"
    PING              = "ping"
    # Safe write — agents may recommend, owner approves
    CONFIGURE         = "configure"
    # Owner-only
    ACTUATE           = "actuate"
    MOTION            = "motion"
    BIND_TWIN         = "bind_twin"
    FIRMWARE_UPDATE   = "firmware_update"
    EMERGENCY_STOP    = "emergency_stop"


# --- Allow-list + per-command policy ---------------------------------------
OWNER_ONLY_COMMANDS = {
    CommandKind.ACTUATE,
    CommandKind.MOTION,
    CommandKind.BIND_TWIN,
    CommandKind.FIRMWARE_UPDATE,
}
# Read + ping are always allowed; configure is owner-only too, just less
# critical. Emergency stop is owner-only by design.
ALLOWED_COMMANDS = {c.value for c in CommandKind}


class CommandStatus(str, Enum):
    QUEUED         = "queued"
    SIMULATED      = "simulated"
    VALIDATED      = "validated"
    EXECUTED       = "executed"
    REJECTED       = "rejected"        # safety / sim failure / role missing
    FAILED         = "failed"          # runtime error after validation


# --- Sub-documents ---------------------------------------------------------
class HardwareProfile(BaseModel):
    cpu: Optional[str] = None
    ram_mb: Optional[int] = None
    storage_mb: Optional[int] = None
    sensors: List[str] = Field(default_factory=list)
    actuators: List[str] = Field(default_factory=list)
    firmware_version: Optional[str] = None
    notes: Optional[str] = None


class Device(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    kind: DeviceKind
    mqtt_topic: Optional[str] = None     # devices/{id}/{up|down} — convention
    twin_id: Optional[str] = None        # bound Phase-5 digital twin
    status: DeviceStatus = DeviceStatus.REGISTERED
    last_seen: Optional[str] = None
    hardware_profile: HardwareProfile = Field(default_factory=HardwareProfile)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str = Field(default_factory=_utc_now)


class TelemetryRecord(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    device_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    source: str = "mqtt"                 # 'mqtt' | 'http'
    received_at: str = Field(default_factory=_utc_now)


class Command(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    device_id: str
    kind: CommandKind
    payload: Dict[str, Any] = Field(default_factory=dict)
    issued_by_role: Role = Role.GUEST
    issued_by_agent: Optional[str] = None   # 'ajani'|'minerva'|'hermes'|'council'|None
    status: CommandStatus = CommandStatus.QUEUED
    sim_score: Optional[float] = None
    validation_findings: List[str] = Field(default_factory=list)
    rejection_reason: Optional[str] = None
    pipeline_log: List[Dict[str, Any]] = Field(default_factory=list)
    queued_at: str = Field(default_factory=_utc_now)
    executed_at: Optional[str] = None
