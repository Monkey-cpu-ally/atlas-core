"""Iter30 review verification via PUBLIC ingress (REACT_APP_BACKEND_URL).
Tests all contracts from the review request against the deployed backend."""
import base64
import os
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://youthful-archimedes-7.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


# ---------- Health & non-destructive ----------
def test_root_health(s):
    r = s.get(f"{API}/health", timeout=10)
    assert r.status_code == 200


def test_vision_health_capabilities(s):
    r = s.get(f"{API}/vision/health", timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    assert d["driver_count"] >= 12
    caps = d["capabilities"]
    for c in ("chunked_video_ingest", "vision_device_registry", "driver_plugin_interface"):
        assert c in caps, f"missing {c}"
    for k in ("camera", "thermal", "lidar", "imu", "nir_bridge"):
        assert k in d["supported_kinds"], f"missing kind {k}"


def test_knowledge_network_health(s):
    r = s.get(f"{API}/knowledge-network/health", timeout=10)
    assert r.status_code == 200


def test_dev_pipeline_status(s):
    r = s.get(f"{API}/dev/pipeline/status", timeout=10)
    assert r.status_code == 200


# ---------- Driver registry ----------
def test_drivers_list_full_kinds(s):
    r = s.get(f"{API}/vision/devices/drivers", timeout=10)
    assert r.status_code == 200
    payload = r.json()
    drivers = payload["drivers"] if isinstance(payload, dict) else payload
    assert len(drivers) == 12
    kinds = {d["kind"] for d in drivers}
    expected = {"camera", "thermal", "event_camera", "multispectral", "depth",
                "lidar", "radar", "sonar", "imu", "force", "torque", "nir_bridge"}
    assert kinds == expected
    for d in drivers:
        assert isinstance(d["capabilities"], list) and len(d["capabilities"]) >= 1


# ---------- Unified device registration ----------
def _reg(s, kind, name=None):
    payload = {"kind": kind, "name": name or f"TEST_{kind}_{uuid.uuid4().hex[:6]}"}
    return s.post(f"{API}/vision/devices", json=payload, timeout=10)


def test_register_lidar_driver_defaults(s):
    r = _reg(s, "lidar")
    assert r.status_code in (200, 201), r.text
    d = r.json()
    caps = d.get("capabilities", [])
    assert "point_cloud" in caps and "depth_map" in caps
    # driver defaults
    assert d.get("sample_rate_hz") == 10.0
    assert d.get("channels") == 32
    # cleanup
    s.delete(f"{API}/vision/devices/{d['id']}")


def test_register_thermal_defaults(s):
    r = _reg(s, "thermal")
    assert r.status_code in (200, 201)
    d = r.json()
    assert "heat_map" in d.get("capabilities", [])
    assert d.get("resolution") == [320, 240]
    s.delete(f"{API}/vision/devices/{d['id']}")


def test_register_unknown_kind_rejected(s):
    r = s.post(f"{API}/vision/devices", json={"kind": "totally_bogus", "name": "TEST_x"}, timeout=10)
    assert r.status_code in (400, 422)


# ---------- Legacy compat & capability filter ----------
def test_capability_filter_wrench(s):
    # register a force device
    r = _reg(s, "force")
    assert r.status_code in (200, 201)
    fid = r.json()["id"]
    r2 = s.get(f"{API}/vision/devices", params={"capability": "wrench"}, timeout=10)
    assert r2.status_code == 200
    payload = r2.json()
    devices = payload["devices"] if isinstance(payload, dict) else payload
    ids = [d["id"] for d in devices]
    assert fid in ids
    for d in devices:
        # Every returned device must actually carry wrench
        assert "wrench" in d.get("capabilities", [])
    s.delete(f"{API}/vision/devices/{fid}")


def test_legacy_camera_still_surfaces(s):
    cam_payload = {"name": f"TEST_legacycam_{uuid.uuid4().hex[:6]}", "resolution": [1920, 1080], "fps": 30}
    r = s.post(f"{API}/vision/devices/camera", json=cam_payload, timeout=10)
    assert r.status_code in (200, 201), r.text
    cam_id = r.json()["id"]
    r2 = s.get(f"{API}/vision/devices/{cam_id}", timeout=10)
    assert r2.status_code == 200
    r3 = s.delete(f"{API}/vision/devices/{cam_id}", timeout=10)
    assert r3.status_code in (200, 204)
    r4 = s.delete(f"{API}/vision/devices/{cam_id}", timeout=10)
    assert r4.status_code == 404


# ---------- Video ingest ----------
def test_video_ingest_config(s):
    r = s.get(f"{API}/vision/ingest/video/config", timeout=10)
    assert r.status_code == 200
    d = r.json()
    for k in ("max_mb", "max_seconds", "chunk_mb", "chunk_bytes", "max_bytes"):
        assert k in d
    assert d["chunk_bytes"] == d["chunk_mb"] * 1024 * 1024


@pytest.fixture(scope="module")
def video_device(s):
    r = _reg(s, "camera", name=f"TEST_vidcam_{uuid.uuid4().hex[:6]}")
    assert r.status_code in (200, 201)
    did = r.json()["id"]
    yield did
    s.delete(f"{API}/vision/devices/{did}")


def _start(s, device_id, total_bytes, fps_extract=2, codec="mp4"):
    return s.post(f"{API}/vision/ingest/video/start", json={
        "device_id": device_id, "total_bytes": total_bytes,
        "codec": codec, "fps_extract": fps_extract,
    }, timeout=10)


def test_video_start_unknown_device(s):
    r = _start(s, "nope-nonexistent", 1024)
    assert r.status_code == 404


def test_video_start_too_large(s, video_device):
    r = _start(s, video_device, 10 * 1024 * 1024 * 1024)  # 10 GB
    assert r.status_code == 400
    assert "too large" in r.text.lower()


def test_video_full_upload_creates_frames(s, video_device):
    # small 3-chunk payload
    chunks = [b"A" * 100, b"B" * 150, b"C" * 200]
    total = sum(len(c) for c in chunks)
    r = _start(s, video_device, total, fps_extract=2)
    assert r.status_code in (200, 201), r.text
    sess = r.json()
    assert sess["status"] == "open"
    sid = sess["id"] if "id" in sess else sess.get("session_id")
    # send out of order: 2, 0, 1
    order = [2, 0, 1]
    for i in order:
        payload = base64.b64encode(chunks[i]).decode()
        rc = s.post(f"{API}/vision/ingest/video/chunk", json={
            "session_id": sid, "index": i, "payload_b64": payload,
        }, timeout=10)
        assert rc.status_code in (200, 201), rc.text
    # complete
    rf = s.post(f"{API}/vision/ingest/video/complete", json={
        "session_id": sid, "duration_seconds": 3.0,
    }, timeout=15)
    assert rf.status_code in (200, 201), rf.text
    result = rf.json()
    assert result["status"] == "completed"
    assert "checksum" in result
    frame_ids = result.get("frame_ids") or result.get("frames") or []
    # fps_extract=2.0 * duration=3.0 => 6 frames
    assert len(frame_ids) == 6, f"expected 6 frames, got {len(frame_ids)}"
    # verify one frame fetchable with source=video
    fid = frame_ids[0] if isinstance(frame_ids[0], str) else frame_ids[0].get("id")
    fr = s.get(f"{API}/vision/frames/{fid}", timeout=10)
    assert fr.status_code == 200
    meta = fr.json().get("metadata", {})
    assert meta.get("source") == "video"


def test_video_overflow_chunk(s, video_device):
    r = _start(s, video_device, 100, fps_extract=1)
    assert r.status_code in (200, 201)
    sid = r.json().get("id") or r.json().get("session_id")
    big = base64.b64encode(b"X" * 500).decode()
    rc = s.post(f"{API}/vision/ingest/video/chunk", json={
        "session_id": sid, "index": 0, "payload_b64": big,
    }, timeout=10)
    assert rc.status_code == 400


def test_video_complete_empty_session(s, video_device):
    r = _start(s, video_device, 100, fps_extract=1)
    assert r.status_code in (200, 201)
    sid = r.json().get("id") or r.json().get("session_id")
    rf = s.post(f"{API}/vision/ingest/video/complete", json={
        "session_id": sid, "duration_seconds": 1.0,
    }, timeout=10)
    assert rf.status_code == 400
