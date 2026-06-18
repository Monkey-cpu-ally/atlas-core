"""Iteration 21 — ESP32 lifecycle + safety contract + HUD endpoint live-data audit.

Covers:
  * 18 HUD-backing GET endpoints — all must return 200 with non-empty primary collection.
  * /api/robot/mqtt/status — dormant when MQTT_BROKER_HOST unset.
  * ESP32 lifecycle: register → sim telemetry → command (actuate led) → state proven on device.
  * ESP32 safety: emergency_stop enqueues inbox command + safe_state is sticky + motion rejected.
"""
import os
import subprocess
import sys
import time

import pytest
import requests


def _load_backend_url() -> str:
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if url:
        return url.rstrip("/")
    # Fall back to frontend/.env (preview URL).
    try:
        with open("/app/frontend/.env") as f:
            for ln in f:
                if ln.startswith("REACT_APP_BACKEND_URL="):
                    return ln.split("=", 1)[1].strip().rstrip("/")
    except Exception:
        pass
    raise RuntimeError("REACT_APP_BACKEND_URL is not set")


BASE_URL = _load_backend_url()
LOCAL_BACKEND = "http://localhost:8001"
OWNER_HEADERS = {"X-Atlas-Role": "owner"}


# ----------------------------- HUD endpoints -----------------------------
HUD_ENDPOINTS = [
    ("/api/robot/devices", ["items", "devices"]),
    ("/api/research-orch/blueprints", ["items", "blueprints"]),
    ("/api/membank/list?limit=5", ["items", "memories"]),
    ("/api/knowledge/subjects", ["subjects", "items"]),
    ("/api/research-orch/queue/status", None),  # status doc
    ("/api/atlas/archive/list", ["items", "entries"]),
    ("/api/llm/health", None),
    ("/api/ai/voices", ["voices", "items"]),
    ("/api/themes/list", ["themes", "items"]),
    ("/api/intake/list", ["items"]),
    ("/api/worldwatch/updates", ["items", "updates"]),
    ("/api/self-improve/proposals", ["items", "proposals"]),
    ("/api/learning/lessons", ["lessons", "items"]),
    ("/api/manual/sections", ["sections", "items"]),
    ("/api/membank/graph/list", ["items"]),
    ("/api/research-orch/missions", ["items", "missions"]),
    ("/api/persona/list", ["__list__", "items", "personas"]),
    ("/api/twins/list", ["items", "twins"]),
]


@pytest.mark.parametrize("path,keys", HUD_ENDPOINTS)
def test_hud_endpoint_live(path, keys):
    """Every HUD-backing endpoint returns 200 and a non-empty primary collection."""
    r = requests.get(f"{BASE_URL}{path}", timeout=20)
    assert r.status_code == 200, f"{path} returned {r.status_code}: {r.text[:200]}"
    body = r.json()
    if keys is None:
        # health / status doc
        assert isinstance(body, dict) and len(body) > 0, f"{path}: empty response"
        return
    # If endpoint returns a bare list, accept the special "__list__" marker.
    if isinstance(body, list):
        assert "__list__" in keys, f"{path} returned a bare list but none of {keys} allow it"
        assert len(body) > 0, f"{path} bare list is empty"
        return
    assert isinstance(body, dict), f"{path} body not dict: {type(body)}"
    matched_key = next((k for k in keys if k in body and k != "__list__"), None)
    assert matched_key, f"{path} missing any of {keys}: {list(body.keys())[:10]}"
    coll = body[matched_key]
    if isinstance(coll, dict):
        assert len(coll) > 0, f"{path}.{matched_key} dict is empty"
        return
    assert isinstance(coll, list), f"{path}.{matched_key} not a list/dict"
    assert len(coll) > 0, f"{path}.{matched_key} is empty"


# ----------------------------- MQTT bridge -----------------------------
def test_mqtt_status_dormant():
    r = requests.get(f"{BASE_URL}/api/robot/mqtt/status", timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert body.get("enabled") is False
    assert body.get("connected") is False
    assert body.get("topic_prefix") == "atlas"
    # last_error may be None or a string — must NOT throw
    assert "last_error" in body


# ----------------------------- ESP32 lifecycle & safety -----------------------------
@pytest.fixture(scope="module")
def registered_device():
    payload = {
        "name": "TEST_ESP32_iter21",
        "kind": "esp32",
        "description": "iter21 lifecycle + safety test device",
    }
    r = requests.post(
        f"{LOCAL_BACKEND}/api/robot/devices", json=payload, headers=OWNER_HEADERS, timeout=30
    )
    assert r.status_code in (200, 201), f"register failed {r.status_code}: {r.text[:300]}"
    body = r.json()
    assert "id" in body, body
    assert "mtls" in body and "cert_pem" in body["mtls"], "mtls cert missing"
    device_id = body["id"]
    device_name = body.get("name") or payload["name"]
    yield {"id": device_id, "name": device_name}
    # Teardown — best-effort delete
    try:
        requests.delete(
            f"{BASE_URL}/api/robot/devices/{device_id}", headers=OWNER_HEADERS, timeout=10
        )
    except Exception:
        pass


@pytest.fixture(scope="module")
def sim_process(registered_device):
    """Launch the python sim against the LOCAL backend (skip public ingress)."""
    log_path = "/tmp/sim_iter21.log"
    log_fh = open(log_path, "w")
    proc = subprocess.Popen(
        [
            sys.executable,
            "/app/hardware/esp32/sim/atlas_node_sim.py",
            "--device-id", registered_device["id"],
            "--backend", LOCAL_BACKEND,
            "--interval", "2",
        ],
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )
    time.sleep(6)  # let it push a few telemetry frames
    yield {"proc": proc, "log_path": log_path}
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    log_fh.close()


def _read_sim_log(log_path: str) -> str:
    try:
        with open(log_path) as f:
            return f.read()
    except Exception:
        return ""


def test_telemetry_ingested(registered_device, sim_process):
    """After ~5s the sim should have posted ≥3 telemetry frames with source=http_sim."""
    time.sleep(2)
    r = requests.get(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}/telemetry?limit=10",
        timeout=10,
    )
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    items = body.get("items") or body.get("telemetry") or []
    assert len(items) >= 3, f"only {len(items)} telemetry rows: {items[:2]}"
    sources = {it.get("source") for it in items}
    assert "http_sim" in sources, f"source set: {sources}"
    # numeric sensor_raw in payload
    pl = items[0].get("payload") or {}
    assert isinstance(pl.get("sensor_raw"), (int, float)), pl


def test_device_online(registered_device, sim_process):
    r = requests.get(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}", timeout=10
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "online", f"status={body.get('status')}"
    assert body.get("last_seen"), "last_seen missing"


def test_actuate_command_applied(registered_device, sim_process):
    """Send actuate led=true → sim should apply → next telemetry shows led_on=true."""
    r = requests.post(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}/command",
        json={"kind": "actuate", "payload": {"led": True}},
        headers=OWNER_HEADERS,
        timeout=10,
    )
    assert r.status_code in (200, 201), r.text[:300]
    body = r.json()
    assert body.get("status") == "executed", f"command status={body.get('status')}: {body}"

    time.sleep(5)  # give sim time to poll inbox (2s cadence) + push fresh telemetry
    r2 = requests.get(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}/telemetry?limit=5",
        timeout=10,
    )
    items = r2.json().get("items") or []
    assert items, "no telemetry after actuate"
    # newest item should show led_on=true
    payloads_seen = [(it.get("payload") or {}).get("led_on") for it in items]
    assert True in payloads_seen, f"led_on=True not seen in last 5 frames: {payloads_seen}"


def test_emergency_stop_enqueues_and_is_sticky(registered_device, sim_process):
    """A) emergency_stop returns safe_state; B) sim log shows EMERGENCY STOP;
    C) status stays safe_state despite ongoing telemetry; D) motion is rejected."""
    # (A) trigger
    r = requests.post(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}/emergency-stop",
        headers=OWNER_HEADERS,
        timeout=10,
    )
    assert r.status_code in (200, 201), r.text[:300]
    body = r.json()
    assert body.get("status") == "safe_state", f"emergency-stop status={body.get('status')}"

    # (B) sim should pick the inbox command up within ~4s
    time.sleep(5)
    log = _read_sim_log(sim_process["log_path"])
    assert "EMERGENCY STOP" in log, f"sim log missing EMERGENCY STOP marker. tail=\n{log[-1200:]}"

    # (C) telemetry continues to arrive but status must remain safe_state
    time.sleep(3)
    r2 = requests.get(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}", timeout=10
    )
    assert r2.status_code == 200
    assert r2.json().get("status") == "safe_state", (
        f"telemetry illegally promoted status back to {r2.json().get('status')}"
    )

    # (D) motion must be rejected
    r3 = requests.post(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}/command",
        json={"kind": "motion", "payload": {"duty_a": 120, "duty_b": 120}},
        headers=OWNER_HEADERS,
        timeout=10,
    )
    assert r3.status_code in (200, 201, 400, 409), r3.text[:300]
    rb = r3.json()
    assert rb.get("status") == "rejected", f"motion command not rejected: {rb}"
    reason = (rb.get("rejection_reason") or "").upper()
    assert "SAFE_STATE" in reason, f"rejection_reason missing SAFE_STATE: {rb}"


def test_clear_safe_state(registered_device, sim_process):
    r = requests.post(
        f"{BASE_URL}/api/robot/devices/{registered_device['id']}/clear-safe-state",
        json={"confirm": registered_device["name"]},
        headers=OWNER_HEADERS,
        timeout=10,
    )
    assert r.status_code in (200, 201), r.text[:300]
    body = r.json()
    assert body.get("ok") is True, body
