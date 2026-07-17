"""ATLAS Vision Systems — FastAPI routes.

All routes are prefixed `/api/vision/*`. Nothing outside this file
depends on OpenCV or PyTorch, so the router can be included from
`server.py` unconditionally.

Endpoint index:
    GET    /api/vision/health
    GET    /api/vision/devices?kind=camera|sensor
    POST   /api/vision/devices/camera            (register)
    POST   /api/vision/devices/sensor            (register)
    GET    /api/vision/devices/{device_id}
    DELETE /api/vision/devices/{device_id}
    POST   /api/vision/calibration/intrinsic
    GET    /api/vision/calibration/intrinsic/{device_id}
    POST   /api/vision/calibration/hand-eye
    GET    /api/vision/calibration/hand-eye/{device_id}
    POST   /api/vision/ingest/frame
    GET    /api/vision/frames/{frame_id}
    GET    /api/vision/frames?device_id=&limit=
    POST   /api/vision/detect
    GET    /api/vision/detections/{frame_id}
    POST   /api/vision/track
    GET    /api/vision/tracks/{track_id}
    POST   /api/vision/pose
    GET    /api/vision/poses/{frame_id}
    POST   /api/vision/inspection/industrial
    POST   /api/vision/inspection/pcb
    GET    /api/vision/inspection/{result_id}
    GET    /api/vision/inspections?device_id=&limit=
    POST   /api/vision/fusion
    POST   /api/vision/twin-link
    GET    /api/vision/twin-link/{twin_id}
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from models.vision_models import (
    Camera, Sensor, CameraCalibration, HandEyeCalibration, Frame, TwinLink,
    CameraRegisterRequest, SensorRegisterRequest,
    IntrinsicCalibrationRequest, HandEyeRequest,
    FrameIngestRequest, DetectRequest, TrackRequest, PoseRequest,
    InspectionRequest, FusionRequest, TwinLinkRequest,
    VisionDeviceRegisterRequest,
    VideoStartRequest, VideoChunkRequest, VideoCompleteRequest,
)
from services import vision as vsvc


router = APIRouter(prefix="/api/vision", tags=["Vision Systems"])


# --- Health ------------------------------------------------------------------
@router.get("/health")
async def health() -> Dict[str, Any]:
    devices = await vsvc.list_vision_devices()
    drivers = vsvc.list_drivers()
    return {
        "status": "ok",
        "layer": "vision-systems",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "device_count": devices["count"],
        "driver_count": len(drivers),
        "supported_kinds": [d["kind"] for d in drivers],
        "capabilities": [
            "vision_device_registry",
            "driver_plugin_interface",
            "camera_registry", "sensor_registry",
            "intrinsic_calibration", "hand_eye_calibration",
            "image_frame_ingest", "synthetic_frame_generation",
            "object_detection", "object_tracking",
            "pose_estimation",
            "industrial_inspection", "pcb_inspection",
            "sensor_fusion", "digital_twin_link",
            "chunked_video_ingest",
        ],
    }


# --- Unified VisionDevice registry ------------------------------------------
@router.get("/devices/drivers")
async def get_drivers():
    """Return the full plugin catalogue — one row per registered
    driver + its capability set. Route handlers use this to advertise
    the supported hardware surface at runtime."""
    return {"drivers": vsvc.list_drivers()}


@router.post("/devices")
async def register_vision_device(req: VisionDeviceRegisterRequest):
    try:
        dev = await vsvc.register_vision_device(req)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return dev.model_dump()


# --- Legacy per-kind convenience wrappers (backwards-compat) ----------------
@router.get("/devices")
async def get_devices(
    kind: Optional[str] = Query(None),
    capability: Optional[str] = Query(None),
):
    """Unified listing across new + legacy device collections.

    Also returns backwards-compat `cameras` / `sensors` splits so existing
    HUD panels keep working without a rewrite."""
    unified = await vsvc.list_vision_devices(kind=kind, capability=capability)
    if kind in (None, "camera", "sensor"):
        legacy = await vsvc.list_devices(kind=None)
    else:
        legacy = {"cameras": [], "sensors": [], "total": 0}
    return {
        "count": unified["count"],
        "devices": unified["devices"],
        "cameras": legacy.get("cameras", []),
        "sensors": legacy.get("sensors", []),
    }


@router.post("/devices/camera")
async def register_camera(req: CameraRegisterRequest) -> Camera:
    return await vsvc.register_camera(Camera(**req.model_dump()))


@router.post("/devices/sensor")
async def register_sensor(req: SensorRegisterRequest) -> Sensor:
    return await vsvc.register_sensor(Sensor(**req.model_dump()))


@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    row = await vsvc.get_vision_device(device_id)
    if not row:
        raise HTTPException(404, f"device '{device_id}' not found")
    return row


@router.delete("/devices/{device_id}")
async def delete_device(device_id: str):
    ok = await vsvc.delete_vision_device(device_id)
    if not ok:
        raise HTTPException(404, f"device '{device_id}' not found")
    return {"deleted": device_id}


# --- Calibration -------------------------------------------------------------
@router.post("/calibration/intrinsic")
async def calibrate_intrinsic(req: IntrinsicCalibrationRequest) -> CameraCalibration:
    dev = await vsvc.get_vision_device(req.device_id)
    if not dev:
        raise HTTPException(404, f"device '{req.device_id}' not found")
    return await vsvc.store_intrinsic(CameraCalibration(**req.model_dump()))


@router.get("/calibration/intrinsic/{device_id}")
async def get_intrinsic(device_id: str):
    row = await vsvc.get_intrinsic(device_id)
    if not row:
        raise HTTPException(404, f"no intrinsic calibration for '{device_id}'")
    return row


@router.post("/calibration/hand-eye")
async def calibrate_hand_eye(req: HandEyeRequest) -> HandEyeCalibration:
    dev = await vsvc.get_vision_device(req.device_id)
    if not dev:
        raise HTTPException(404, f"device '{req.device_id}' not found")
    return await vsvc.store_hand_eye(HandEyeCalibration(**req.model_dump()))


@router.get("/calibration/hand-eye/{device_id}")
async def get_hand_eye(device_id: str):
    row = await vsvc.get_hand_eye(device_id)
    if not row:
        raise HTTPException(404, f"no hand-eye calibration for '{device_id}'")
    return row


# --- Frame ingest ------------------------------------------------------------
@router.post("/ingest/frame")
async def ingest_frame(req: FrameIngestRequest) -> Frame:
    dev = await vsvc.get_vision_device(req.device_id)
    if not dev:
        raise HTTPException(404, f"device '{req.device_id}' not found")
    try:
        bytes_size, checksum, payload_ref = vsvc.ingest_frame_payload(
            width=req.width, height=req.height, channels=req.channels,
            fmt=req.format, payload_b64=req.payload_b64, seed=req.seed,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    frame = Frame(
        device_id=req.device_id,
        width=req.width, height=req.height, channels=req.channels,
        format=req.format,
        bytes_size=bytes_size, checksum=checksum, payload_ref=payload_ref,
        seed=req.seed, metadata=req.metadata,
    )
    return await vsvc.store_frame(frame)


@router.get("/frames/{frame_id}")
async def get_frame(frame_id: str):
    row = await vsvc.get_frame(frame_id)
    if not row:
        raise HTTPException(404, f"frame '{frame_id}' not found")
    return row


@router.get("/frames")
async def list_frames(device_id: Optional[str] = None, limit: int = 50):
    return {"items": await vsvc.list_frames(device_id, limit=limit)}


# --- Detection ---------------------------------------------------------------
@router.post("/detect")
async def detect(req: DetectRequest):
    frame_doc = await vsvc.get_frame(req.frame_id)
    if not frame_doc:
        raise HTTPException(404, f"frame '{req.frame_id}' not found")
    frame = Frame(**frame_doc)
    dets = await vsvc.run_detector(frame, req.detector, req.max_detections)
    return {"count": len(dets), "detections": [d.model_dump() for d in dets]}


@router.get("/detections/{frame_id}")
async def get_detections(frame_id: str):
    return {"items": await vsvc.list_detections(frame_id)}


# --- Tracking ----------------------------------------------------------------
@router.post("/track")
async def track(req: TrackRequest):
    tracks = await vsvc.link_detections_into_tracks(req.frame_id, req.iou_threshold)
    return {"count": len(tracks), "tracks": [t.model_dump() for t in tracks]}


@router.get("/tracks/{track_id}")
async def get_track(track_id: str):
    row = await vsvc.get_track(track_id)
    if not row:
        raise HTTPException(404, f"track '{track_id}' not found")
    return row


# --- Pose --------------------------------------------------------------------
@router.post("/pose")
async def pose(req: PoseRequest):
    p = await vsvc.estimate_pose(req.detection_id, req.method)
    if not p:
        raise HTTPException(404, f"detection '{req.detection_id}' not found")
    return p.model_dump()


@router.get("/poses/{frame_id}")
async def poses_for_frame(frame_id: str):
    return {"items": await vsvc.list_poses(frame_id)}


# --- Inspection --------------------------------------------------------------
@router.post("/inspection/industrial")
async def inspect_industrial(req: InspectionRequest):
    if not await vsvc.get_frame(req.frame_id):
        raise HTTPException(404, f"frame '{req.frame_id}' not found")
    result = await vsvc.run_industrial_inspection(
        req.device_id, req.frame_id, req.part_id, req.thresholds,
    )
    return result.model_dump()


@router.post("/inspection/pcb")
async def inspect_pcb(req: InspectionRequest):
    if not await vsvc.get_frame(req.frame_id):
        raise HTTPException(404, f"frame '{req.frame_id}' not found")
    result = await vsvc.run_pcb_inspection(
        req.device_id, req.frame_id, req.part_id, req.thresholds,
    )
    return result.model_dump()


@router.get("/inspection/{result_id}")
async def get_inspection_result(result_id: str):
    row = await vsvc.get_inspection(result_id)
    if not row:
        raise HTTPException(404, f"inspection '{result_id}' not found")
    return row


@router.get("/inspections")
async def list_inspection_results(device_id: Optional[str] = None, limit: int = 50):
    return {"items": await vsvc.list_inspections(device_id, limit=limit)}


# --- Fusion ------------------------------------------------------------------
@router.post("/fusion")
async def fuse(req: FusionRequest):
    return await vsvc.fuse_detections(req.frame_ids, req.strategy, req.iou_threshold)


# --- Twin link ---------------------------------------------------------------
@router.post("/twin-link")
async def link_twin(req: TwinLinkRequest):
    link = TwinLink(**req.model_dump())
    return (await vsvc.link_to_twin(link)).model_dump()


@router.get("/twin-link/{twin_id}")
async def get_twin_links(twin_id: str):
    return {"items": await vsvc.links_for_twin(twin_id)}


# --- Video ingestion (chunked upload) ---------------------------------------
@router.get("/ingest/video/config")
async def video_config():
    """Advertise the pod's chunked-upload limits so clients can size
    their PUTs correctly. Configurable via VISION_VIDEO_MAX_MB /
    VISION_VIDEO_MAX_SECONDS / VISION_VIDEO_CHUNK_MB env vars."""
    return vsvc.video_config()


@router.post("/ingest/video/start")
async def video_start(req: VideoStartRequest):
    try:
        return await vsvc.start_video_session(
            device_id=req.device_id, total_bytes=req.total_bytes,
            codec=req.codec, fps_extract=req.fps_extract,
            metadata={**req.metadata,
                      **({"duration_seconds": req.duration_seconds}
                         if req.duration_seconds is not None else {})},
        )
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/ingest/video/chunk")
async def video_chunk(req: VideoChunkRequest):
    try:
        return await vsvc.append_video_chunk(req.session_id, req.index, req.payload_b64)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/ingest/video/complete")
async def video_complete(req: VideoCompleteRequest):
    try:
        return await vsvc.complete_video_session(req.session_id, req.duration_seconds)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/ingest/video/{session_id}")
async def video_session(session_id: str):
    row = await vsvc.get_video_session(session_id)
    if not row:
        raise HTTPException(404, f"session '{session_id}' not found")
    return row
