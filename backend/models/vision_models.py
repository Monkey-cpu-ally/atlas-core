"""ATLAS Vision Systems — Pydantic models.

Data shapes for the robotics vision subsystem. All models are pure
Pydantic v2 — no numpy/opencv dependency at import time so the module
stays cheap to load and safe to unit-test in isolation.

MongoDB collections mapped to these models:

  vision_cameras         → Camera
  vision_sensors         → Sensor
  vision_calibrations    → CameraCalibration (intrinsic K + distortion)
  vision_hand_eye        → HandEyeCalibration (robot-mounted rig)
  vision_frames          → Frame       (image/video sample header)
  vision_detections      → Detection   (bounding boxes from a frame)
  vision_tracks          → Track       (temporal chain of detections)
  vision_poses           → Pose        (6-DoF estimate)
  vision_inspections     → InspectionResult (industrial + PCB)
  vision_twin_links      → TwinLink    (camera/sensor/inspection ↔ twin)

Every model exposes a stable `id` (uuid4 hex, no dashes).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _uid() -> str:
    return uuid4().hex


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------
class Camera(BaseModel):
    id: str = Field(default_factory=_uid)
    name: str
    make: Optional[str] = None
    model: Optional[str] = None
    resolution: List[int] = Field(default_factory=lambda: [640, 480])   # [w, h]
    fps: float = 30.0
    lens_mm: Optional[float] = None
    mount: Literal["fixed", "arm", "gimbal", "handheld"] = "fixed"
    twin_id: Optional[str] = None       # optional link to a Digital Twin
    ai_owner: str = "hermes"            # default persona
    calibrated: bool = False
    registered_at: str = Field(default_factory=_now_iso)
    tags: List[str] = Field(default_factory=list)


class Sensor(BaseModel):
    """Non-camera perception device — depth, IMU, force, LIDAR, thermal."""
    id: str = Field(default_factory=_uid)
    name: str
    kind: Literal["depth", "imu", "force", "lidar", "thermal", "nir_bridge"]
    resolution: Optional[List[int]] = None
    sample_rate_hz: float = 100.0
    twin_id: Optional[str] = None
    ai_owner: str = "hermes"
    registered_at: str = Field(default_factory=_now_iso)


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------
class CameraCalibration(BaseModel):
    """Pinhole intrinsic + radial distortion."""
    id: str = Field(default_factory=_uid)
    device_id: str
    # K = [[fx,0,cx],[0,fy,cy],[0,0,1]]
    fx: float
    fy: float
    cx: float
    cy: float
    distortion: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0, 0.0])
    reprojection_error_px: float = 0.0
    calibrated_at: str = Field(default_factory=_now_iso)
    notes: Optional[str] = None

    def K(self) -> List[List[float]]:
        return [
            [self.fx,      0.0, self.cx],
            [    0.0, self.fy, self.cy],
            [    0.0,     0.0,    1.0],
        ]


class HandEyeCalibration(BaseModel):
    """Rigid transform between a robot end-effector and a mounted camera."""
    id: str = Field(default_factory=_uid)
    device_id: str
    robot_id: Optional[str] = None            # link to a robot_devices row
    mount: Literal["eye_in_hand", "eye_to_hand"] = "eye_in_hand"
    # 4x4 SE(3) transform, row-major
    transform: List[List[float]] = Field(
        default_factory=lambda: [
            [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1],
        ]
    )
    solved_at: str = Field(default_factory=_now_iso)
    residual_mm: float = 0.0


# ---------------------------------------------------------------------------
# Frames + Detections
# ---------------------------------------------------------------------------
class Frame(BaseModel):
    id: str = Field(default_factory=_uid)
    device_id: str
    width: int
    height: int
    channels: int = 3
    format: Literal["png", "jpg", "raw", "synthetic"] = "synthetic"
    bytes_size: int = 0                       # size of the payload
    checksum: Optional[str] = None
    # payload_ref stores WHERE the pixels live (data URI, blob key, or None
    # for synthetic frames whose contents are deterministic from `seed`).
    payload_ref: Optional[str] = None
    seed: Optional[int] = None                # for synthetic reproducibility
    captured_at: str = Field(default_factory=_now_iso)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float


class Detection(BaseModel):
    id: str = Field(default_factory=_uid)
    frame_id: str
    device_id: str
    label: str
    confidence: float
    bbox: BoundingBox
    detected_at: str = Field(default_factory=_now_iso)
    meta: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Tracking + Pose
# ---------------------------------------------------------------------------
class TrackSample(BaseModel):
    frame_id: str
    detection_id: str
    bbox: BoundingBox
    t: str = Field(default_factory=_now_iso)


class Track(BaseModel):
    id: str = Field(default_factory=_uid)
    label: str
    device_id: str
    samples: List[TrackSample] = Field(default_factory=list)
    started_at: str = Field(default_factory=_now_iso)
    last_seen_at: str = Field(default_factory=_now_iso)
    active: bool = True


class Pose(BaseModel):
    """6-DoF pose estimate for a detected object."""
    id: str = Field(default_factory=_uid)
    frame_id: str
    device_id: str
    label: str
    detection_id: Optional[str] = None
    # translation in meters (relative to camera frame), rotation as quaternion
    translation: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    quaternion: List[float] = Field(default_factory=lambda: [1.0, 0.0, 0.0, 0.0])
    residual_px: float = 0.0
    estimated_at: str = Field(default_factory=_now_iso)


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------
class InspectionDefect(BaseModel):
    label: str
    severity: Literal["info", "warn", "fail"]
    bbox: Optional[BoundingBox] = None
    detail: Optional[str] = None


class InspectionResult(BaseModel):
    id: str = Field(default_factory=_uid)
    kind: Literal["industrial", "pcb"] = "industrial"
    device_id: str
    frame_id: str
    part_id: Optional[str] = None
    verdict: Literal["pass", "warn", "fail"] = "pass"
    defects: List[InspectionDefect] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    inspected_at: str = Field(default_factory=_now_iso)


# ---------------------------------------------------------------------------
# Digital Twin link
# ---------------------------------------------------------------------------
class TwinLink(BaseModel):
    id: str = Field(default_factory=_uid)
    twin_id: str
    entity_kind: Literal["camera", "sensor", "inspection", "track"]
    entity_id: str
    linked_at: str = Field(default_factory=_now_iso)
    note: Optional[str] = None


# ---------------------------------------------------------------------------
# Request shells (for API input)
# ---------------------------------------------------------------------------
class CameraRegisterRequest(BaseModel):
    name: str
    make: Optional[str] = None
    model: Optional[str] = None
    resolution: List[int] = Field(default_factory=lambda: [640, 480])
    fps: float = 30.0
    lens_mm: Optional[float] = None
    mount: Literal["fixed", "arm", "gimbal", "handheld"] = "fixed"
    twin_id: Optional[str] = None
    ai_owner: str = "hermes"
    tags: List[str] = Field(default_factory=list)


class SensorRegisterRequest(BaseModel):
    name: str
    kind: Literal["depth", "imu", "force", "lidar", "thermal", "nir_bridge"]
    resolution: Optional[List[int]] = None
    sample_rate_hz: float = 100.0
    twin_id: Optional[str] = None
    ai_owner: str = "hermes"


class IntrinsicCalibrationRequest(BaseModel):
    device_id: str
    fx: float = Field(gt=0)
    fy: float = Field(gt=0)
    cx: float = Field(ge=0)
    cy: float = Field(ge=0)
    distortion: List[float] = Field(default_factory=lambda: [0.0] * 5)
    reprojection_error_px: float = 0.0
    notes: Optional[str] = None


class HandEyeRequest(BaseModel):
    device_id: str
    robot_id: Optional[str] = None
    mount: Literal["eye_in_hand", "eye_to_hand"] = "eye_in_hand"
    transform: List[List[float]] = Field(min_length=4, max_length=4)
    residual_mm: float = 0.0


class FrameIngestRequest(BaseModel):
    device_id: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    channels: int = 3
    format: Literal["png", "jpg", "raw", "synthetic"] = "synthetic"
    # payload_b64 optional — omitted for synthetic frames (contents
    # derived deterministically from `seed`).
    payload_b64: Optional[str] = None
    seed: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectRequest(BaseModel):
    frame_id: str
    detector: Literal["synthetic_grid", "synthetic_center", "twin_hint"] = "synthetic_grid"
    max_detections: int = 8


class TrackRequest(BaseModel):
    frame_id: str
    iou_threshold: float = 0.30


class PoseRequest(BaseModel):
    detection_id: str
    method: Literal["synthetic", "pnp_stub"] = "synthetic"


class InspectionRequest(BaseModel):
    device_id: str
    frame_id: str
    part_id: Optional[str] = None
    thresholds: Dict[str, float] = Field(default_factory=dict)


class FusionRequest(BaseModel):
    frame_ids: List[str] = Field(min_length=1)
    strategy: Literal["union", "nms"] = "nms"
    iou_threshold: float = 0.30


class TwinLinkRequest(BaseModel):
    twin_id: str
    entity_kind: Literal["camera", "sensor", "inspection", "track"]
    entity_id: str
    note: Optional[str] = None
