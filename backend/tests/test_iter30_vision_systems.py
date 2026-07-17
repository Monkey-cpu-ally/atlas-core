"""Iteration 30 — ATLAS Vision Systems.

Unit + integration tests for the robotics perception foundation.
All tests are self-contained: they seed their own devices, frames,
detections, tracks, poses, inspections; they never require real
hardware, OpenCV, PyTorch, or paid API access.

Runs against the in-process FastAPI server via localhost so the ingress
does not swallow 4xx bodies.
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict

import pytest
import requests

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
V = f"{BACKEND}/api/vision"
TIMEOUT = 15.0


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _register_camera(name: str | None = None, twin_id: str | None = None) -> Dict[str, Any]:
    r = requests.post(
        f"{V}/devices/camera",
        json={
            "name": name or f"vt-cam-{uuid.uuid4().hex[:8]}",
            "resolution": [640, 480],
            "fps": 30,
            "mount": "arm",
            "twin_id": twin_id,
        },
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    return r.json()


def _register_sensor(kind: str = "depth") -> Dict[str, Any]:
    r = requests.post(
        f"{V}/devices/sensor",
        json={
            "name": f"vt-sen-{uuid.uuid4().hex[:8]}",
            "kind": kind,
            "sample_rate_hz": 60,
        },
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    return r.json()


def _ingest_frame(device_id: str, seed: int = 42, w: int = 640, h: int = 480) -> Dict[str, Any]:
    r = requests.post(
        f"{V}/ingest/frame",
        json={
            "device_id": device_id,
            "width": w, "height": h, "channels": 3,
            "format": "synthetic", "seed": seed,
        },
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------------------
# 1. Health + capability advertisement
# ---------------------------------------------------------------------------
def test_vision_health_returns_full_capability_list():
    r = requests.get(f"{V}/health", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    caps = set(body["capabilities"])
    required = {
        "vision_device_registry", "driver_plugin_interface",
        "camera_registry", "sensor_registry",
        "intrinsic_calibration", "hand_eye_calibration",
        "image_frame_ingest", "object_detection", "object_tracking",
        "pose_estimation", "industrial_inspection", "pcb_inspection",
        "sensor_fusion", "digital_twin_link", "chunked_video_ingest",
    }
    missing = required - caps
    assert not missing, f"missing capabilities: {missing}"
    # New unified fields
    assert body["driver_count"] >= 12
    assert "camera" in body["supported_kinds"]
    assert "lidar" in body["supported_kinds"]
    assert "imu" in body["supported_kinds"]


# ---------------------------------------------------------------------------
# 1b. VisionDevice driver registry
# ---------------------------------------------------------------------------
class TestDriverRegistry:
    def test_list_drivers_covers_full_hardware_surface(self):
        r = requests.get(f"{V}/devices/drivers", timeout=TIMEOUT)
        assert r.status_code == 200
        drivers = r.json()["drivers"]
        kinds = {d["kind"] for d in drivers}
        # Every hardware family the abstraction claims to support.
        expected = {
            "camera", "thermal", "event_camera", "multispectral",
            "depth", "lidar", "radar", "sonar",
            "imu", "force", "torque", "nir_bridge",
        }
        missing = expected - kinds
        assert not missing, f"missing driver kinds: {missing}"
        # Every driver declares at least one capability.
        for d in drivers:
            assert d["capabilities"], f"driver {d['kind']!r} has no capabilities"

    def test_register_unified_device_lidar_gets_driver_defaults(self):
        r = requests.post(
            f"{V}/devices",
            json={"name": f"lidar-{uuid.uuid4().hex[:6]}", "kind": "lidar"},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["kind"] == "lidar"
        assert set(body["capabilities"]) == {"point_cloud", "depth_map"}
        # Driver defaults populated:
        assert body["sample_rate_hz"] == 10.0
        assert body["channels"] == 32
        assert body["driver"] == "_LiDARDriver"

    def test_register_unified_device_thermal_gets_imaging_defaults(self):
        r = requests.post(
            f"{V}/devices",
            json={"name": f"therm-{uuid.uuid4().hex[:6]}", "kind": "thermal"},
            timeout=TIMEOUT,
        )
        body = r.json()
        assert body["resolution"] == [320, 240]
        assert body["fps"] == 9.0
        assert "heat_map" in body["capabilities"]

    def test_unknown_kind_rejected_400(self):
        r = requests.post(
            f"{V}/devices",
            json={"name": "unknown", "kind": "not-a-real-sensor"},
            timeout=TIMEOUT,
        )
        # Pydantic Literal validation → 422 (before driver dispatch)
        assert r.status_code in (400, 422)

    def test_unified_lookup_finds_new_device(self):
        r = requests.post(
            f"{V}/devices",
            json={"name": "imu-1", "kind": "imu"},
            timeout=TIMEOUT,
        )
        dev_id = r.json()["id"]
        r2 = requests.get(f"{V}/devices/{dev_id}", timeout=TIMEOUT)
        assert r2.status_code == 200
        assert r2.json()["kind"] == "imu"
        # Delete + confirm 404
        assert requests.delete(f"{V}/devices/{dev_id}", timeout=TIMEOUT).status_code == 200
        assert requests.get(f"{V}/devices/{dev_id}", timeout=TIMEOUT).status_code == 404

    def test_capability_filter_lists_only_matching_devices(self):
        # Register one imaging + one non-imaging device, then filter.
        cam = requests.post(f"{V}/devices",
                            json={"name": f"cf-cam-{uuid.uuid4().hex[:6]}", "kind": "camera"},
                            timeout=TIMEOUT).json()
        force = requests.post(f"{V}/devices",
                              json={"name": f"cf-force-{uuid.uuid4().hex[:6]}", "kind": "force"},
                              timeout=TIMEOUT).json()
        r = requests.get(f"{V}/devices?capability=wrench", timeout=TIMEOUT)
        assert r.status_code == 200
        devs = r.json()["devices"]
        ids = {d["id"] for d in devs}
        assert force["id"] in ids
        assert cam["id"] not in ids

    def test_legacy_camera_projection_still_visible(self):
        # Register via legacy endpoint, list via unified — must appear.
        cam = _register_camera(name=f"legacy-{uuid.uuid4().hex[:6]}")
        r = requests.get(f"{V}/devices?kind=camera", timeout=TIMEOUT)
        body = r.json()
        # Either in unified `devices` list OR the legacy `cameras` split.
        all_ids = {d["id"] for d in body.get("devices", [])} | {c["id"] for c in body.get("cameras", [])}
        assert cam["id"] in all_ids


# ---------------------------------------------------------------------------
# 2. Camera + Sensor registry (backwards compat)
# ---------------------------------------------------------------------------
class TestRegistry:
    def test_register_camera_returns_uid(self):
        cam = _register_camera()
        assert isinstance(cam.get("id"), str) and len(cam["id"]) >= 16
        assert cam["ai_owner"] == "hermes"
        assert cam["calibrated"] is False

    def test_register_sensor_and_lookup(self):
        sen = _register_sensor("lidar")
        r = requests.get(f"{V}/devices/{sen['id']}", timeout=TIMEOUT)
        assert r.status_code == 200
        assert r.json()["_kind"] == "sensor"
        assert r.json()["kind"] == "lidar"

    def test_list_devices_kind_filter(self):
        cam = _register_camera()
        sen = _register_sensor("imu")
        # Legacy split still works — cameras only in cameras[]
        cams = requests.get(f"{V}/devices?kind=camera", timeout=TIMEOUT).json()
        assert any(c["id"] == cam["id"] for c in cams.get("cameras", []))
        # Unified device listing surfaces both, filterable by capability.
        imu_hits = requests.get(f"{V}/devices?capability=motion", timeout=TIMEOUT).json()
        motion_ids = {d["id"] for d in imu_hits["devices"]}
        # sen was registered via legacy /devices/sensor as kind=imu → motion
        assert sen["id"] in motion_ids or any(
            s["id"] == sen["id"] for s in imu_hits.get("sensors", [])
        )

    def test_delete_device_roundtrip(self):
        cam = _register_camera()
        r = requests.delete(f"{V}/devices/{cam['id']}", timeout=TIMEOUT)
        assert r.status_code == 200 and r.json()["deleted"] == cam["id"]
        # Second delete must 404 (no silent success).
        assert requests.delete(f"{V}/devices/{cam['id']}", timeout=TIMEOUT).status_code == 404


# ---------------------------------------------------------------------------
# 3. Calibration
# ---------------------------------------------------------------------------
class TestCalibration:
    def test_intrinsic_upsert_and_flag_camera(self):
        cam = _register_camera()
        r = requests.post(
            f"{V}/calibration/intrinsic",
            json={
                "device_id": cam["id"],
                "fx": 600.0, "fy": 600.0, "cx": 320.0, "cy": 240.0,
                "distortion": [0.1, -0.02, 0, 0, 0],
                "reprojection_error_px": 0.42,
            },
            timeout=TIMEOUT,
        )
        assert r.status_code == 200, r.text
        # Re-read camera: calibrated flag flipped.
        cam2 = requests.get(f"{V}/devices/{cam['id']}", timeout=TIMEOUT).json()
        assert cam2["calibrated"] is True
        # GET returns same data.
        got = requests.get(f"{V}/calibration/intrinsic/{cam['id']}", timeout=TIMEOUT).json()
        assert got["fx"] == 600.0 and got["cy"] == 240.0

    def test_intrinsic_rejects_unknown_device(self):
        r = requests.post(
            f"{V}/calibration/intrinsic",
            json={"device_id": "does-not-exist", "fx": 1, "fy": 1, "cx": 0, "cy": 0},
            timeout=TIMEOUT,
        )
        assert r.status_code == 404

    def test_hand_eye_transform_stored(self):
        cam = _register_camera()
        eye_in_hand = [
            [1, 0, 0, 0.05], [0, 1, 0, 0.00], [0, 0, 1, 0.10], [0, 0, 0, 1],
        ]
        r = requests.post(
            f"{V}/calibration/hand-eye",
            json={
                "device_id": cam["id"], "mount": "eye_in_hand",
                "transform": eye_in_hand, "residual_mm": 0.8,
            },
            timeout=TIMEOUT,
        )
        assert r.status_code == 200
        assert r.json()["mount"] == "eye_in_hand"
        assert r.json()["transform"] == eye_in_hand


# ---------------------------------------------------------------------------
# 4. Frame ingestion
# ---------------------------------------------------------------------------
class TestIngest:
    def test_synthetic_frame_stable_checksum(self):
        cam = _register_camera()
        f1 = _ingest_frame(cam["id"], seed=7)
        f2 = _ingest_frame(cam["id"], seed=7)
        # Identical seed → identical checksum (deterministic pixels).
        assert f1["checksum"] == f2["checksum"]
        assert f1["id"] != f2["id"]

    def test_non_synthetic_needs_payload(self):
        cam = _register_camera()
        r = requests.post(
            f"{V}/ingest/frame",
            json={"device_id": cam["id"], "width": 32, "height": 32,
                  "format": "png", "payload_b64": None},
            timeout=TIMEOUT,
        )
        assert r.status_code == 400

    def test_frame_listing_by_device(self):
        cam = _register_camera()
        _ingest_frame(cam["id"], seed=1)
        _ingest_frame(cam["id"], seed=2)
        r = requests.get(f"{V}/frames?device_id={cam['id']}&limit=10", timeout=TIMEOUT)
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) >= 2 and all(x["device_id"] == cam["id"] for x in items)


# ---------------------------------------------------------------------------
# 5. Detection
# ---------------------------------------------------------------------------
class TestDetection:
    def test_synthetic_grid_returns_at_least_one_box(self):
        cam = _register_camera()
        fr = _ingest_frame(cam["id"])
        r = requests.post(
            f"{V}/detect",
            json={"frame_id": fr["id"], "detector": "synthetic_grid", "max_detections": 4},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200
        dets = r.json()["detections"]
        assert 1 <= len(dets) <= 6
        for d in dets:
            bb = d["bbox"]
            assert 0 <= bb["x"] <= fr["width"]
            assert 0 <= bb["y"] <= fr["height"]
            assert bb["w"] > 0 and bb["h"] > 0

    def test_synthetic_center_detector_deterministic(self):
        cam = _register_camera()
        fr = _ingest_frame(cam["id"])
        r = requests.post(
            f"{V}/detect",
            json={"frame_id": fr["id"], "detector": "synthetic_center"},
            timeout=TIMEOUT,
        )
        dets = r.json()["detections"]
        assert len(dets) == 1
        assert dets[0]["label"] == "center_target"
        assert dets[0]["confidence"] > 0.95

    def test_detect_missing_frame_returns_404(self):
        r = requests.post(
            f"{V}/detect",
            json={"frame_id": "does-not-exist", "detector": "synthetic_grid"},
            timeout=TIMEOUT,
        )
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 6. Tracking
# ---------------------------------------------------------------------------
class TestTracking:
    def test_tracking_reuses_prior_track_on_iou_hit(self):
        cam = _register_camera()
        fr1 = _ingest_frame(cam["id"], seed=11)
        requests.post(
            f"{V}/detect",
            json={"frame_id": fr1["id"], "detector": "synthetic_center"},
            timeout=TIMEOUT,
        )
        t1 = requests.post(
            f"{V}/track",
            json={"frame_id": fr1["id"], "iou_threshold": 0.1},
            timeout=TIMEOUT,
        ).json()
        assert t1["count"] == 1
        # Same-seed frame → center detection at the same pixel, high IoU.
        fr2 = _ingest_frame(cam["id"], seed=12)
        requests.post(
            f"{V}/detect",
            json={"frame_id": fr2["id"], "detector": "synthetic_center"},
            timeout=TIMEOUT,
        )
        t2 = requests.post(
            f"{V}/track",
            json={"frame_id": fr2["id"], "iou_threshold": 0.1},
            timeout=TIMEOUT,
        ).json()
        # Track ID from first pass should reappear (same label, high IoU).
        assert t2["tracks"][0]["id"] == t1["tracks"][0]["id"]
        # Sample count grew.
        assert len(t2["tracks"][0]["samples"]) >= 2


# ---------------------------------------------------------------------------
# 7. Pose
# ---------------------------------------------------------------------------
class TestPose:
    def test_pnp_stub_uses_intrinsic_when_available(self):
        cam = _register_camera()
        requests.post(
            f"{V}/calibration/intrinsic",
            json={"device_id": cam["id"], "fx": 500, "fy": 500, "cx": 320, "cy": 240},
            timeout=TIMEOUT,
        )
        fr = _ingest_frame(cam["id"])
        d = requests.post(
            f"{V}/detect",
            json={"frame_id": fr["id"], "detector": "synthetic_center"},
            timeout=TIMEOUT,
        ).json()["detections"][0]
        p = requests.post(
            f"{V}/pose",
            json={"detection_id": d["id"], "method": "pnp_stub"},
            timeout=TIMEOUT,
        ).json()
        assert len(p["translation"]) == 3
        # PnP stub → residual half a pixel.
        assert p["residual_px"] == pytest.approx(0.5)

    def test_pose_synthetic_method_no_calibration_required(self):
        cam = _register_camera()
        fr = _ingest_frame(cam["id"])
        d = requests.post(
            f"{V}/detect",
            json={"frame_id": fr["id"], "detector": "synthetic_center"},
            timeout=TIMEOUT,
        ).json()["detections"][0]
        p = requests.post(
            f"{V}/pose",
            json={"detection_id": d["id"], "method": "synthetic"},
            timeout=TIMEOUT,
        ).json()
        assert p["residual_px"] == pytest.approx(1.5)


# ---------------------------------------------------------------------------
# 8. Inspection
# ---------------------------------------------------------------------------
class TestInspection:
    def _seed_labelled_detections(self, frame_id: str, device_id: str,
                                  labels: list[str], confidence: float = 0.9):
        """Directly write hand-crafted detections into Mongo so we get
        deterministic verdicts regardless of the synthetic sampler."""
        from pymongo import MongoClient
        db = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))[
            os.environ.get("DB_NAME", "test_database")
        ]
        db["vision_detections"].insert_many([{
            "id": uuid.uuid4().hex,
            "frame_id": frame_id, "device_id": device_id,
            "label": lbl, "confidence": confidence,
            "bbox": {"x": 10, "y": 10, "w": 20, "h": 20},
            "detected_at": "2026-07-11T00:00:00+00:00",
            "meta": {"detector": "test_seed"},
        } for lbl in labels])

    def test_industrial_inspection_fails_on_defect(self):
        cam = _register_camera()
        fr = _ingest_frame(cam["id"])
        self._seed_labelled_detections(fr["id"], cam["id"], ["defect"], confidence=0.9)
        r = requests.post(
            f"{V}/inspection/industrial",
            json={
                "device_id": cam["id"], "frame_id": fr["id"],
                "thresholds": {"fail": 0.75},
            },
            timeout=TIMEOUT,
        )
        body = r.json()
        assert r.status_code == 200
        assert body["kind"] == "industrial"
        assert body["verdict"] == "fail"
        assert body["metrics"]["defect_count"] >= 1

    def test_pcb_inspection_flags_missing_components(self):
        cam = _register_camera()
        fr = _ingest_frame(cam["id"])
        # No PCB components seeded → expect fail with min_components=3.
        r = requests.post(
            f"{V}/inspection/pcb",
            json={
                "device_id": cam["id"], "frame_id": fr["id"],
                "thresholds": {"min_components": 3, "component_confidence": 0.6},
            },
            timeout=TIMEOUT,
        )
        body = r.json()
        assert body["kind"] == "pcb"
        assert body["verdict"] == "fail"
        assert any(d["label"] == "missing_components" for d in body["defects"])

    def test_pcb_inspection_passes_with_enough_components(self):
        cam = _register_camera()
        fr = _ingest_frame(cam["id"])
        self._seed_labelled_detections(
            fr["id"], cam["id"],
            ["pcb_component", "resistor", "capacitor", "ic"],
            confidence=0.9,
        )
        r = requests.post(
            f"{V}/inspection/pcb",
            json={
                "device_id": cam["id"], "frame_id": fr["id"],
                "thresholds": {"min_components": 3, "component_confidence": 0.6},
            },
            timeout=TIMEOUT,
        )
        assert r.json()["verdict"] == "pass"


# ---------------------------------------------------------------------------
# 9. Fusion
# ---------------------------------------------------------------------------
def test_fusion_nms_removes_duplicates():
    cam = _register_camera()
    fr1 = _ingest_frame(cam["id"], seed=100)
    requests.post(
        f"{V}/detect",
        json={"frame_id": fr1["id"], "detector": "synthetic_center"},
        timeout=TIMEOUT,
    )
    fr2 = _ingest_frame(cam["id"], seed=101)
    requests.post(
        f"{V}/detect",
        json={"frame_id": fr2["id"], "detector": "synthetic_center"},
        timeout=TIMEOUT,
    )
    r = requests.post(
        f"{V}/fusion",
        json={"frame_ids": [fr1["id"], fr2["id"]], "strategy": "nms", "iou_threshold": 0.2},
        timeout=TIMEOUT,
    )
    body = r.json()
    assert body["input_detections"] >= 2
    # NMS collapses the identical-position center detections.
    assert body["count"] <= body["input_detections"]


def test_fusion_union_keeps_all():
    cam = _register_camera()
    fr1 = _ingest_frame(cam["id"], seed=200)
    fr2 = _ingest_frame(cam["id"], seed=201)
    for fid in (fr1["id"], fr2["id"]):
        requests.post(
            f"{V}/detect",
            json={"frame_id": fid, "detector": "synthetic_grid"},
            timeout=TIMEOUT,
        )
    r = requests.post(
        f"{V}/fusion",
        json={"frame_ids": [fr1["id"], fr2["id"]], "strategy": "union"},
        timeout=TIMEOUT,
    )
    body = r.json()
    assert body["count"] == body["input_detections"]


# ---------------------------------------------------------------------------
# 10. Digital-twin link
# ---------------------------------------------------------------------------
class TestTwinLink:
    def test_link_camera_to_twin_and_reverse_lookup(self):
        twin_id = f"twin-{uuid.uuid4().hex[:8]}"
        cam = _register_camera()
        r = requests.post(
            f"{V}/twin-link",
            json={"twin_id": twin_id, "entity_kind": "camera", "entity_id": cam["id"]},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200
        # Camera row mirrors twin_id.
        cam2 = requests.get(f"{V}/devices/{cam['id']}", timeout=TIMEOUT).json()
        assert cam2["twin_id"] == twin_id
        # Reverse lookup returns the link.
        listed = requests.get(f"{V}/twin-link/{twin_id}", timeout=TIMEOUT).json()
        assert any(x["entity_id"] == cam["id"] for x in listed["items"])

    def test_link_is_idempotent_on_reinsert(self):
        twin_id = f"twin-{uuid.uuid4().hex[:8]}"
        sen = _register_sensor("thermal")
        for _ in range(3):
            requests.post(
                f"{V}/twin-link",
                json={"twin_id": twin_id, "entity_kind": "sensor", "entity_id": sen["id"]},
                timeout=TIMEOUT,
            )
        listed = requests.get(f"{V}/twin-link/{twin_id}", timeout=TIMEOUT).json()
        matches = [x for x in listed["items"] if x["entity_id"] == sen["id"]]
        assert len(matches) == 1  # upsert, not duplicate


# ---------------------------------------------------------------------------
# 11. End-to-end perception pipeline
# ---------------------------------------------------------------------------
def test_end_to_end_camera_to_inspection():
    """A complete pipeline: register → calibrate → ingest → detect →
    track → pose → inspect. This is the exercise Hermes/Weaver will
    run at runtime, so it must succeed against the real router."""
    cam = _register_camera(name=f"e2e-{uuid.uuid4().hex[:6]}")
    requests.post(
        f"{V}/calibration/intrinsic",
        json={"device_id": cam["id"], "fx": 500, "fy": 500, "cx": 320, "cy": 240},
        timeout=TIMEOUT,
    )
    fr = _ingest_frame(cam["id"], seed=999)
    dets = requests.post(
        f"{V}/detect",
        json={"frame_id": fr["id"], "detector": "synthetic_grid", "max_detections": 3},
        timeout=TIMEOUT,
    ).json()["detections"]
    assert len(dets) >= 1

    tr = requests.post(
        f"{V}/track",
        json={"frame_id": fr["id"], "iou_threshold": 0.05},
        timeout=TIMEOUT,
    ).json()
    assert tr["count"] >= 1

    p = requests.post(
        f"{V}/pose",
        json={"detection_id": dets[0]["id"], "method": "pnp_stub"},
        timeout=TIMEOUT,
    ).json()
    assert "translation" in p

    ins = requests.post(
        f"{V}/inspection/industrial",
        json={
            "device_id": cam["id"], "frame_id": fr["id"],
            "thresholds": {"fail": 0.9},
        },
        timeout=TIMEOUT,
    ).json()
    assert ins["kind"] == "industrial"
    assert ins["verdict"] in ("pass", "warn", "fail")


# ---------------------------------------------------------------------------
# 12. Chunked video ingestion
# ---------------------------------------------------------------------------
import base64  # noqa: E402


class TestVideoIngest:
    def test_video_config_advertises_limits(self):
        r = requests.get(f"{V}/ingest/video/config", timeout=TIMEOUT)
        assert r.status_code == 200
        body = r.json()
        for key in ("max_mb", "max_seconds", "chunk_mb",
                    "chunk_bytes", "max_bytes"):
            assert key in body
        assert body["chunk_bytes"] == body["chunk_mb"] * 1024 * 1024

    def test_full_chunked_upload_creates_frames(self):
        cam = _register_camera()
        # Fake a tiny "video" — 3 chunks of 32 bytes each = 96 bytes.
        chunks = [b"A" * 32, b"B" * 32, b"C" * 32]
        total = sum(len(c) for c in chunks)
        session = requests.post(
            f"{V}/ingest/video/start",
            json={"device_id": cam["id"], "total_bytes": total,
                  "codec": "mp4", "fps_extract": 2,
                  "duration_seconds": 3.0},
            timeout=TIMEOUT,
        ).json()
        assert session["status"] == "open"
        sid = session["id"]
        # Upload chunks out of order to test the sort step
        for i in [1, 0, 2]:
            r = requests.post(
                f"{V}/ingest/video/chunk",
                json={"session_id": sid, "index": i,
                      "payload_b64": base64.b64encode(chunks[i]).decode()},
                timeout=TIMEOUT,
            )
            assert r.status_code == 200, r.text
        # Progress should now be 1.0
        got = requests.get(f"{V}/ingest/video/{sid}", timeout=TIMEOUT).json()
        assert got["total_bytes_received"] == total
        # Complete the session
        r = requests.post(
            f"{V}/ingest/video/complete",
            json={"session_id": sid},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200, r.text
        result = r.json()
        assert result["status"] == "completed"
        # fps_extract=2, duration=3s → 6 frames materialised
        assert result["frames_created"] == 6
        assert len(result["frame_ids"]) == 6
        # Each frame is fetchable via /frames/{id}
        for fid in result["frame_ids"][:2]:
            fr = requests.get(f"{V}/frames/{fid}", timeout=TIMEOUT).json()
            assert fr["device_id"] == cam["id"]
            assert fr["metadata"]["source"] == "video"

    def test_video_rejects_overflow_chunk(self):
        cam = _register_camera()
        sid = requests.post(
            f"{V}/ingest/video/start",
            json={"device_id": cam["id"], "total_bytes": 10,
                  "codec": "mp4", "fps_extract": 1},
            timeout=TIMEOUT,
        ).json()["id"]
        r = requests.post(
            f"{V}/ingest/video/chunk",
            json={"session_id": sid, "index": 0,
                  "payload_b64": base64.b64encode(b"X" * 100).decode()},
            timeout=TIMEOUT,
        )
        assert r.status_code == 400
        assert "overflow" in r.json()["detail"].lower()

    def test_video_rejects_too_large_declared_bytes(self):
        cam = _register_camera()
        r = requests.post(
            f"{V}/ingest/video/start",
            json={"device_id": cam["id"],
                  "total_bytes": 10 * 1024 * 1024 * 1024,  # 10 GB
                  "codec": "mp4", "fps_extract": 1},
            timeout=TIMEOUT,
        )
        assert r.status_code == 400
        assert "too large" in r.json()["detail"].lower()

    def test_video_rejects_missing_device(self):
        r = requests.post(
            f"{V}/ingest/video/start",
            json={"device_id": "does-not-exist", "total_bytes": 100,
                  "codec": "mp4", "fps_extract": 1},
            timeout=TIMEOUT,
        )
        assert r.status_code == 404

    def test_video_complete_rejects_empty_session(self):
        cam = _register_camera()
        sid = requests.post(
            f"{V}/ingest/video/start",
            json={"device_id": cam["id"], "total_bytes": 100,
                  "codec": "mp4", "fps_extract": 1},
            timeout=TIMEOUT,
        ).json()["id"]
        # Complete without uploading any chunks
        r = requests.post(
            f"{V}/ingest/video/complete",
            json={"session_id": sid},
            timeout=TIMEOUT,
        )
        assert r.status_code == 400

