"""ATLAS Vision Systems — service layer.

Pure-Python + numpy implementation of the robotics perception pipeline.
No OpenCV / PyTorch / paid API dependency — every detector, tracker,
pose estimator and inspection pipeline is deterministic and simulated,
so tests run offline and CI stays fast.

The interfaces are drawn to match production libraries: swap the
`SyntheticGridDetector` for a `yolov8` implementation later and no
route code changes.

Sections:
    1. Mongo helpers
    2. Registry             — cameras + sensors CRUD
    3. Calibration          — intrinsic + hand-eye
    4. Ingestion            — frame headers, checksums, synthetic seed
    5. Detection            — interface + 3 synthetic implementations
    6. Tracking             — IoU-linker across frames
    7. Pose                 — synthetic 6-DoF + PnP-lite from intrinsic K
    8. Inspection           — industrial defect + PCB component pipelines
    9. Fusion               — multi-source NMS / union combiner
   10. Twin link            — camera/sensor/inspection ↔ digital twin
"""
from __future__ import annotations

import hashlib
import os
import struct
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient

from models.vision_models import (
    Camera, Sensor, CameraCalibration, HandEyeCalibration,
    Frame, Detection, BoundingBox, Track, TrackSample, Pose,
    InspectionResult, InspectionDefect, TwinLink,
)


# ============================================================================
# 1. Mongo helpers
# ============================================================================
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    return _client[os.environ.get("DB_NAME", "test_database")]


def _strip(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc.pop("_id", None)
    return doc


# ============================================================================
# 2. Registry
# ============================================================================
async def register_camera(cam: Camera) -> Camera:
    await _db()["vision_cameras"].insert_one(cam.model_dump())
    return cam


async def register_sensor(sen: Sensor) -> Sensor:
    await _db()["vision_sensors"].insert_one(sen.model_dump())
    return sen


async def get_device(device_id: str) -> Optional[Dict[str, Any]]:
    for coll in ("vision_cameras", "vision_sensors"):
        row = await _db()[coll].find_one({"id": device_id}, {"_id": 0})
        if row:
            row["_kind"] = "camera" if coll == "vision_cameras" else "sensor"
            return row
    return None


async def list_devices(kind: Optional[str] = None) -> Dict[str, Any]:
    cams: List[Dict[str, Any]] = []
    sens: List[Dict[str, Any]] = []
    if kind in (None, "camera"):
        cams = await _db()["vision_cameras"].find({}, {"_id": 0}).to_list(500)
    if kind in (None, "sensor"):
        sens = await _db()["vision_sensors"].find({}, {"_id": 0}).to_list(500)
    return {"cameras": cams, "sensors": sens, "total": len(cams) + len(sens)}


async def delete_device(device_id: str) -> bool:
    for coll in ("vision_cameras", "vision_sensors"):
        r = await _db()[coll].delete_one({"id": device_id})
        if r.deleted_count:
            return True
    return False


# ============================================================================
# 3. Calibration
# ============================================================================
async def store_intrinsic(calib: CameraCalibration) -> CameraCalibration:
    # Idempotent — one intrinsic per device (upsert).
    await _db()["vision_calibrations"].update_one(
        {"device_id": calib.device_id},
        {"$set": calib.model_dump()},
        upsert=True,
    )
    await _db()["vision_cameras"].update_one(
        {"id": calib.device_id}, {"$set": {"calibrated": True}}
    )
    return calib


async def get_intrinsic(device_id: str) -> Optional[Dict[str, Any]]:
    return _strip_or_none(
        await _db()["vision_calibrations"].find_one({"device_id": device_id})
    )


async def store_hand_eye(hec: HandEyeCalibration) -> HandEyeCalibration:
    await _db()["vision_hand_eye"].update_one(
        {"device_id": hec.device_id},
        {"$set": hec.model_dump()},
        upsert=True,
    )
    return hec


async def get_hand_eye(device_id: str) -> Optional[Dict[str, Any]]:
    return _strip_or_none(
        await _db()["vision_hand_eye"].find_one({"device_id": device_id})
    )


def _strip_or_none(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if doc is None:
        return None
    doc.pop("_id", None)
    return doc


# ============================================================================
# 4. Ingestion
# ============================================================================
def _synthetic_pixels(width: int, height: int, seed: int) -> bytes:
    """Deterministic PRNG pixel buffer — same seed => same bytes.

    Used both to fabricate a payload for the `synthetic` format and by
    the detector chain when it needs pixels for a hashing step.
    """
    rng = np.random.default_rng(seed)
    buf = rng.integers(0, 256, size=height * width * 3, dtype=np.uint8)
    return bytes(buf.tobytes())


def ingest_frame_payload(
    *,
    width: int,
    height: int,
    channels: int,
    fmt: str,
    payload_b64: Optional[str],
    seed: Optional[int],
) -> Tuple[int, str, Optional[str]]:
    """Return (bytes_size, sha256_checksum, stored_ref).

    For `synthetic` frames we don't persist pixels (they're regeneratable
    from the seed) — `stored_ref` is None. For real payloads we return a
    data URI-style reference. The full binary lives in Mongo GridFS only
    if the architect wires that in later; for now we keep the reference
    small.
    """
    if fmt == "synthetic":
        s = seed if seed is not None else 0
        blob = _synthetic_pixels(width, height, s)
        return len(blob), hashlib.sha256(blob).hexdigest(), None
    if not payload_b64:
        raise ValueError("payload_b64 required for non-synthetic format")
    import base64
    raw = base64.b64decode(payload_b64)
    return len(raw), hashlib.sha256(raw).hexdigest(), f"inline:{fmt}"


async def store_frame(frame: Frame) -> Frame:
    await _db()["vision_frames"].insert_one(frame.model_dump())
    return frame


async def get_frame(frame_id: str) -> Optional[Dict[str, Any]]:
    return _strip_or_none(await _db()["vision_frames"].find_one({"id": frame_id}))


async def list_frames(device_id: Optional[str], limit: int = 50) -> List[Dict[str, Any]]:
    q = {"device_id": device_id} if device_id else {}
    return await _db()["vision_frames"].find(q, {"_id": 0}).sort("captured_at", -1).to_list(limit)


# ============================================================================
# 5. Detection
# ============================================================================
def _clip_bbox(bbox: BoundingBox, W: int, H: int) -> BoundingBox:
    x = max(0.0, min(float(W - 1), bbox.x))
    y = max(0.0, min(float(H - 1), bbox.y))
    w = max(1.0, min(float(W - x), bbox.w))
    h = max(1.0, min(float(H - y), bbox.h))
    return BoundingBox(x=x, y=y, w=w, h=h)


def _hash_seed(frame: Frame) -> int:
    """Derive a stable seed from a frame so detectors are deterministic
    per-frame regardless of storage state."""
    ck = (frame.checksum or "") + "|" + str(frame.seed or 0)
    return struct.unpack("<Q", hashlib.blake2b(ck.encode(), digest_size=8).digest())[0]


def synthetic_grid_detector(frame: Frame, max_detections: int) -> List[Detection]:
    """Grid-sampling stand-in for a real detector. Places 1-N boxes on
    a coarse grid; label chosen from a fixed vocabulary via hash."""
    rng = np.random.default_rng(_hash_seed(frame))
    W, H = frame.width, frame.height
    n = int(rng.integers(1, max(2, min(max_detections + 1, 6))))
    labels = ["part_a", "part_b", "screw", "pcb_component", "defect", "hand_tool"]
    detections: List[Detection] = []
    for _ in range(n):
        w = float(rng.integers(W // 12, max(W // 6, W // 12 + 1)))
        h = float(rng.integers(H // 12, max(H // 6, H // 12 + 1)))
        x = float(rng.integers(0, max(1, int(W - w))))
        y = float(rng.integers(0, max(1, int(H - h))))
        bbox = _clip_bbox(BoundingBox(x=x, y=y, w=w, h=h), W, H)
        detections.append(Detection(
            frame_id=frame.id,
            device_id=frame.device_id,
            label=labels[int(rng.integers(0, len(labels)))],
            confidence=float(0.6 + 0.4 * rng.random()),
            bbox=bbox,
            meta={"detector": "synthetic_grid"},
        ))
    return detections


def synthetic_center_detector(frame: Frame, max_detections: int) -> List[Detection]:
    """Always returns exactly one high-confidence detection at the
    centre — useful for pose/inspection pipelines that need a
    guaranteed anchor."""
    W, H = frame.width, frame.height
    w = W // 4
    h = H // 4
    bbox = BoundingBox(x=(W - w) / 2, y=(H - h) / 2, w=w, h=h)
    return [Detection(
        frame_id=frame.id,
        device_id=frame.device_id,
        label="center_target",
        confidence=0.99,
        bbox=bbox,
        meta={"detector": "synthetic_center"},
    )]


def twin_hint_detector(frame: Frame, max_detections: int,
                       twin_labels: Iterable[str]) -> List[Detection]:
    """Emit one detection per label the linked Digital Twin knows
    about — lets Weaver's Twin drive perception without a real model."""
    rng = np.random.default_rng(_hash_seed(frame))
    W, H = frame.width, frame.height
    detections: List[Detection] = []
    for lbl in list(twin_labels)[:max_detections]:
        w = float(W // 6)
        h = float(H // 6)
        x = float(rng.integers(0, max(1, int(W - w))))
        y = float(rng.integers(0, max(1, int(H - h))))
        bbox = _clip_bbox(BoundingBox(x=x, y=y, w=w, h=h), W, H)
        detections.append(Detection(
            frame_id=frame.id,
            device_id=frame.device_id,
            label=str(lbl),
            confidence=0.85,
            bbox=bbox,
            meta={"detector": "twin_hint"},
        ))
    return detections


async def run_detector(frame: Frame, detector: str, max_detections: int) -> List[Detection]:
    if detector == "synthetic_center":
        dets = synthetic_center_detector(frame, max_detections)
    elif detector == "twin_hint":
        # Fetch twin labels from the linked twin's `manifest.labels` if any.
        labels: List[str] = []
        cam = await _db()["vision_cameras"].find_one({"id": frame.device_id})
        if cam and cam.get("twin_id"):
            twin = await _db()["twins"].find_one({"id": cam["twin_id"]})
            labels = (twin or {}).get("manifest", {}).get("labels", []) or ["part_a"]
        dets = twin_hint_detector(frame, max_detections, labels or ["part_a"])
    else:
        dets = synthetic_grid_detector(frame, max_detections)
    if dets:
        await _db()["vision_detections"].insert_many([d.model_dump() for d in dets])
    return dets


async def list_detections(frame_id: str) -> List[Dict[str, Any]]:
    return await _db()["vision_detections"].find({"frame_id": frame_id}, {"_id": 0}).to_list(200)


# ============================================================================
# 6. Tracking
# ============================================================================
def iou(a: BoundingBox, b: BoundingBox) -> float:
    ax2, ay2 = a.x + a.w, a.y + a.h
    bx2, by2 = b.x + b.w, b.y + b.h
    ix = max(0.0, min(ax2, bx2) - max(a.x, b.x))
    iy = max(0.0, min(ay2, by2) - max(a.y, b.y))
    inter = ix * iy
    union = a.w * a.h + b.w * b.h - inter
    return inter / union if union > 0 else 0.0


async def _find_track_for_detection(det: Detection, iou_threshold: float) -> Optional[Dict[str, Any]]:
    cursor = _db()["vision_tracks"].find(
        {"device_id": det.device_id, "label": det.label, "active": True},
        {"_id": 0},
    ).sort("last_seen_at", -1)
    async for t in cursor:
        samples = t.get("samples") or []
        if not samples:
            continue
        last_bbox = BoundingBox(**samples[-1]["bbox"])
        if iou(last_bbox, det.bbox) >= iou_threshold:
            return t
    return None


async def link_detections_into_tracks(frame_id: str, iou_threshold: float) -> List[Track]:
    dets_raw = await list_detections(frame_id)
    if not dets_raw:
        return []
    out: List[Track] = []
    for raw in dets_raw:
        raw["bbox"] = BoundingBox(**raw["bbox"])
        det = Detection(**raw)
        sample = TrackSample(
            frame_id=det.frame_id, detection_id=det.id, bbox=det.bbox,
        )
        existing = await _find_track_for_detection(det, iou_threshold)
        if existing:
            existing["samples"].append(sample.model_dump())
            existing["last_seen_at"] = sample.t
            await _db()["vision_tracks"].update_one(
                {"id": existing["id"]},
                {"$set": {"samples": existing["samples"], "last_seen_at": sample.t}},
            )
            out.append(Track(**existing))
        else:
            tr = Track(
                label=det.label, device_id=det.device_id,
                samples=[sample], last_seen_at=sample.t,
            )
            await _db()["vision_tracks"].insert_one(tr.model_dump())
            out.append(tr)
    return out


async def get_track(track_id: str) -> Optional[Dict[str, Any]]:
    return _strip_or_none(await _db()["vision_tracks"].find_one({"id": track_id}))


# ============================================================================
# 7. Pose estimation
# ============================================================================
async def estimate_pose(detection_id: str, method: str) -> Optional[Pose]:
    det_doc = await _db()["vision_detections"].find_one({"id": detection_id}, {"_id": 0})
    if not det_doc:
        return None
    det_doc["bbox"] = BoundingBox(**det_doc["bbox"])
    det = Detection(**det_doc)
    calib = await get_intrinsic(det.device_id)
    # Center pixel of the bounding box, projected through pinhole model.
    cx_px = det.bbox.x + det.bbox.w / 2
    cy_px = det.bbox.y + det.bbox.h / 2
    if calib and method == "pnp_stub":
        fx, fy = calib["fx"], calib["fy"]
        cx0, cy0 = calib["cx"], calib["cy"]
        # Assume a fixed working distance z = 1.0 m for this stub — real
        # PnP would need >=4 correspondences. This gives a stable metric
        # translation the rest of the pipeline can consume.
        z = 1.0
        tx = (cx_px - cx0) / fx * z
        ty = (cy_px - cy0) / fy * z
        residual = 0.5
    else:
        # `synthetic` — normalised NDC space, no metric guarantee.
        tx = cx_px / max(1.0, det.bbox.w)
        ty = cy_px / max(1.0, det.bbox.h)
        z = 1.0
        residual = 1.5
    pose = Pose(
        frame_id=det.frame_id, device_id=det.device_id,
        label=det.label, detection_id=det.id,
        translation=[float(tx), float(ty), float(z)],
        residual_px=float(residual),
    )
    await _db()["vision_poses"].insert_one(pose.model_dump())
    return pose


async def list_poses(frame_id: str) -> List[Dict[str, Any]]:
    return await _db()["vision_poses"].find({"frame_id": frame_id}, {"_id": 0}).to_list(200)


# ============================================================================
# 8. Inspection
# ============================================================================
_INDUSTRIAL_DEFECT_LABELS = {"defect", "scratch", "crack", "misalignment"}
_PCB_COMPONENT_LABELS = {"pcb_component", "solder_joint", "resistor", "capacitor", "ic"}


async def run_industrial_inspection(
    device_id: str, frame_id: str, part_id: Optional[str],
    thresholds: Dict[str, float],
) -> InspectionResult:
    dets = await list_detections(frame_id)
    defects: List[InspectionDefect] = []
    for d in dets:
        if d["label"] in _INDUSTRIAL_DEFECT_LABELS:
            severity = "fail" if d["confidence"] >= thresholds.get("fail", 0.75) else "warn"
            defects.append(InspectionDefect(
                label=d["label"], severity=severity,
                bbox=BoundingBox(**d["bbox"]),
                detail=f"confidence={d['confidence']:.2f}",
            ))
    verdict = "pass"
    if any(d.severity == "fail" for d in defects):
        verdict = "fail"
    elif defects:
        verdict = "warn"
    result = InspectionResult(
        kind="industrial", device_id=device_id, frame_id=frame_id,
        part_id=part_id, verdict=verdict, defects=defects,
        metrics={"defect_count": float(len(defects)), "sampled": float(len(dets))},
    )
    await _db()["vision_inspections"].insert_one(result.model_dump())
    return result


async def run_pcb_inspection(
    device_id: str, frame_id: str, part_id: Optional[str],
    thresholds: Dict[str, float],
) -> InspectionResult:
    dets = await list_detections(frame_id)
    components = [d for d in dets if d["label"] in _PCB_COMPONENT_LABELS]
    missing = int(thresholds.get("min_components", 2)) - len(components)
    defects: List[InspectionDefect] = []
    if missing > 0:
        defects.append(InspectionDefect(
            label="missing_components",
            severity="fail",
            detail=f"expected>={int(thresholds.get('min_components', 2))} found={len(components)}",
        ))
    for c in components:
        if c["confidence"] < thresholds.get("component_confidence", 0.6):
            defects.append(InspectionDefect(
                label=f"low_conf_{c['label']}",
                severity="warn",
                bbox=BoundingBox(**c["bbox"]),
                detail=f"confidence={c['confidence']:.2f}",
            ))
    verdict = "fail" if any(d.severity == "fail" for d in defects) else (
        "warn" if defects else "pass"
    )
    result = InspectionResult(
        kind="pcb", device_id=device_id, frame_id=frame_id, part_id=part_id,
        verdict=verdict, defects=defects,
        metrics={
            "components_found": float(len(components)),
            "components_expected": float(thresholds.get("min_components", 2)),
        },
    )
    await _db()["vision_inspections"].insert_one(result.model_dump())
    return result


async def get_inspection(result_id: str) -> Optional[Dict[str, Any]]:
    return _strip_or_none(await _db()["vision_inspections"].find_one({"id": result_id}))


async def list_inspections(device_id: Optional[str], limit: int = 50) -> List[Dict[str, Any]]:
    q = {"device_id": device_id} if device_id else {}
    return await _db()["vision_inspections"].find(q, {"_id": 0}).sort("inspected_at", -1).to_list(limit)


# ============================================================================
# 9. Fusion
# ============================================================================
def _nms(dets: Sequence[Dict[str, Any]], iou_threshold: float) -> List[Dict[str, Any]]:
    """Non-max suppression across all detections passed in (potentially
    from multiple frames/devices)."""
    sorted_dets = sorted(dets, key=lambda d: -d["confidence"])
    kept: List[Dict[str, Any]] = []
    for cand in sorted_dets:
        cand_bb = BoundingBox(**cand["bbox"])
        drop = False
        for k in kept:
            if k["label"] != cand["label"]:
                continue
            if iou(BoundingBox(**k["bbox"]), cand_bb) >= iou_threshold:
                drop = True
                break
        if not drop:
            kept.append(cand)
    return kept


async def fuse_detections(frame_ids: List[str], strategy: str,
                          iou_threshold: float) -> Dict[str, Any]:
    all_dets: List[Dict[str, Any]] = []
    for fid in frame_ids:
        all_dets.extend(await list_detections(fid))
    if strategy == "union":
        fused = all_dets
    else:
        fused = _nms(all_dets, iou_threshold)
    return {
        "strategy": strategy,
        "input_frames": len(frame_ids),
        "input_detections": len(all_dets),
        "fused_detections": fused,
        "count": len(fused),
    }


# ============================================================================
# 10. Twin link
# ============================================================================
async def link_to_twin(link: TwinLink) -> TwinLink:
    # De-dupe on (twin_id, entity_kind, entity_id)
    await _db()["vision_twin_links"].update_one(
        {"twin_id": link.twin_id, "entity_kind": link.entity_kind, "entity_id": link.entity_id},
        {"$set": link.model_dump()},
        upsert=True,
    )
    # Also mirror the twin_id onto the camera/sensor row for fast reads.
    if link.entity_kind == "camera":
        await _db()["vision_cameras"].update_one(
            {"id": link.entity_id}, {"$set": {"twin_id": link.twin_id}}
        )
    elif link.entity_kind == "sensor":
        await _db()["vision_sensors"].update_one(
            {"id": link.entity_id}, {"$set": {"twin_id": link.twin_id}}
        )
    return link


async def links_for_twin(twin_id: str) -> List[Dict[str, Any]]:
    return await _db()["vision_twin_links"].find({"twin_id": twin_id}, {"_id": 0}).to_list(200)
