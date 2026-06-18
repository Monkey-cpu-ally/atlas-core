"""
Phase 7 — Robot Control Layer smoke tests.

Exercises the architect's strict spec:
  * roles enum + owner-only allow-list visible
  * seed bootstraps POSEIDON-BUOY / AETHER-STATION / SOIL-WATCH (each twin-bound)
  * device registration is owner-only (guest header => 403)
  * telemetry push roundtrip + history retrieval + ONLINE status flip
  * command pipeline:
      - guest ACTUATE on a twin-bound device => REJECTED (owner-only)
      - owner PING                            => EXECUTED (no twin sim needed)
      - owner ACTUATE on a twin-bound device  => goes through Twin → Sim → Validate → Execute
      - device inbox returns the executed command then empties (delivered=true)
  * EMERGENCY_STOP flips device to SAFE_STATE; subsequent ACTUATE blocked until cleared

Run:
    cd /app/backend && pytest tests/test_robot_phase7.py -v
"""
from __future__ import annotations

import os
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or os.environ.get(
    "BACKEND_URL", "http://localhost:8001"
)
API = f"{BACKEND.rstrip('/')}/api/robot"

OWNER = {"X-Atlas-Role": "owner"}
GUEST = {"X-Atlas-Role": "guest"}
HERMES = {"X-Atlas-Role": "hermes"}

TIMEOUT = httpx.Timeout(60.0, connect=10.0)


# --- Bootstrap -------------------------------------------------------------
def test_roles_endpoint():
    r = httpx.get(f"{API}/roles", timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body["roles"]) >= {"owner", "council", "ajani", "minerva", "hermes", "guest"}
    assert "actuate" in body["owner_only_commands"]
    assert "motion" in body["owner_only_commands"]
    assert "bind_twin" in body["owner_only_commands"]
    assert "firmware_update" in body["owner_only_commands"]


def test_seed_devices_present():
    # The startup hook seeds these; an explicit /seed call is idempotent.
    r = httpx.post(f"{API}/seed", timeout=TIMEOUT)
    assert r.status_code == 200

    r = httpx.get(f"{API}/devices?limit=200", timeout=TIMEOUT)
    assert r.status_code == 200
    names = {d["name"] for d in r.json()["items"]}
    assert {"POSEIDON-BUOY", "AETHER-STATION", "SOIL-WATCH"} <= names

    # Every seed device must be twin-bound (Simulation-First requires a twin).
    for d in r.json()["items"]:
        if d["name"] in {"POSEIDON-BUOY", "AETHER-STATION", "SOIL-WATCH"}:
            assert d.get("twin_id"), f"{d['name']} missing twin binding"


# --- Device registration ----------------------------------------------------
def test_register_device_is_owner_only():
    payload = {
        "name": f"TEST-DEV-{uuid.uuid4().hex[:6]}",
        "kind": "esp32",
        "hardware_profile": {"sensors": ["temp"], "actuators": ["led"]},
        "tags": ["test"],
    }
    # Guest → 403
    r = httpx.post(f"{API}/devices", json=payload, headers=GUEST, timeout=TIMEOUT)
    assert r.status_code == 403, r.text
    # Owner → 200
    r = httpx.post(f"{API}/devices", json=payload, headers=OWNER, timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    dev = r.json()
    assert dev["name"] == payload["name"]
    assert dev["status"] == "registered"
    assert dev["id"]


@pytest.fixture(scope="module")
def owner_device():
    """An ESP32 owned by us with an actuator, NOT twin-bound (so we can test
    the 'no twin → simulate is skipped → execute' branch)."""
    payload = {
        "name": f"FIX-DEV-{uuid.uuid4().hex[:6]}",
        "kind": "esp32",
        "hardware_profile": {"sensors": ["temp"], "actuators": ["led", "relay"]},
        "tags": ["fixture", "test"],
    }
    r = httpx.post(f"{API}/devices", json=payload, headers=OWNER, timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture(scope="module")
def twin_bound_device():
    """Use the seeded POSEIDON-BUOY (twin-bound)."""
    r = httpx.get(f"{API}/devices?limit=200", timeout=TIMEOUT)
    assert r.status_code == 200
    for d in r.json()["items"]:
        if d["name"] == "POSEIDON-BUOY":
            assert d.get("twin_id"), "POSEIDON-BUOY must be twin-bound"
            return d
    pytest.fail("POSEIDON-BUOY not found — seed step failed")


# --- Telemetry --------------------------------------------------------------
def test_telemetry_roundtrip(owner_device):
    dev_id = owner_device["id"]
    payload = {"temp": 23.4, "led_state": "off"}
    r = httpx.post(
        f"{API}/devices/{dev_id}/telemetry",
        json={"payload": payload, "source": "mqtt"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["device_id"] == dev_id
    assert body["payload"] == payload

    # device should now be ONLINE
    r = httpx.get(f"{API}/devices/{dev_id}", timeout=TIMEOUT)
    assert r.json()["status"] == "online"
    assert r.json()["last_seen"]

    # history returns at least one record
    r = httpx.get(f"{API}/devices/{dev_id}/telemetry?limit=5", timeout=TIMEOUT)
    assert r.status_code == 200
    assert len(r.json()["items"]) >= 1


# --- Command pipeline -------------------------------------------------------
def test_guest_actuate_rejected_owner_only(twin_bound_device):
    dev_id = twin_bound_device["id"]
    r = httpx.post(
        f"{API}/devices/{dev_id}/command",
        json={"kind": "actuate", "payload": {"target": "pump", "value": 1}},
        headers=GUEST,
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text          # body carries full context
    cmd = r.json()
    assert cmd["status"] == "rejected"
    assert "owner-only" in (cmd["rejection_reason"] or "")
    # Pipeline must record the authorise step rejection.
    steps = [p["step"] for p in cmd["pipeline_log"]]
    assert "authorise" in steps


def test_owner_ping_executes(owner_device):
    dev_id = owner_device["id"]
    r = httpx.post(
        f"{API}/devices/{dev_id}/command",
        json={"kind": "ping", "payload": {}},
        headers=OWNER,
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    cmd = r.json()
    assert cmd["status"] == "executed", cmd
    steps = [p["step"] for p in cmd["pipeline_log"]]
    assert "authorise" in steps
    assert "execute" in steps


def test_owner_actuate_runs_simulation_first(twin_bound_device):
    """Owner-only ACTUATE on a twin-bound device must hit
    Twin → Simulate → Validate → Execute (or REJECT)."""
    dev_id = twin_bound_device["id"]
    r = httpx.post(
        f"{API}/devices/{dev_id}/command",
        json={"kind": "actuate", "payload": {"target": "valve", "value": "open"}},
        headers=OWNER,
        timeout=httpx.Timeout(120.0, connect=10.0),
    )
    assert r.status_code == 200, r.text
    cmd = r.json()
    # Sim must have produced a score (twin is bound).
    assert cmd["sim_score"] is not None, f"expected a sim score, got {cmd}"
    steps = [p["step"] for p in cmd["pipeline_log"]]
    assert "simulate" in steps
    # Terminal status must be one of these (depending on sim outcome).
    assert cmd["status"] in {"executed", "rejected"}, cmd["status"]


def test_inbox_delivers_executed_commands_once(owner_device):
    """After an EXECUTED command, the device's inbox returns it then empties."""
    dev_id = owner_device["id"]
    # Fire a PING (no twin needed → guaranteed EXECUTED).
    r = httpx.post(
        f"{API}/devices/{dev_id}/command",
        json={"kind": "ping", "payload": {"seq": 1}},
        headers=OWNER,
        timeout=TIMEOUT,
    )
    assert r.status_code == 200
    cmd_id = r.json()["id"]
    assert r.json()["status"] == "executed"

    inbox = httpx.get(f"{API}/devices/{dev_id}/commands/inbox", timeout=TIMEOUT).json()
    assert any(c["id"] == cmd_id for c in inbox["items"]), inbox

    # Second poll must NOT return the same command again (delivered flag).
    inbox2 = httpx.get(f"{API}/devices/{dev_id}/commands/inbox", timeout=TIMEOUT).json()
    assert all(c["id"] != cmd_id for c in inbox2["items"]), inbox2


# --- Emergency stop ---------------------------------------------------------
def test_emergency_stop_blocks_subsequent_actuation(owner_device):
    dev_id = owner_device["id"]
    # Guest cannot trigger EMERGENCY_STOP.
    r = httpx.post(f"{API}/devices/{dev_id}/emergency-stop", headers=GUEST, timeout=TIMEOUT)
    assert r.status_code == 403

    # Owner can.
    r = httpx.post(f"{API}/devices/{dev_id}/emergency-stop", headers=OWNER, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json()["status"] == "safe_state"

    # In SAFE_STATE, non-PING/EMERGENCY actuate must be rejected.
    r = httpx.post(
        f"{API}/devices/{dev_id}/command",
        json={"kind": "actuate", "payload": {"target": "relay", "value": 1}},
        headers=OWNER,
        timeout=TIMEOUT,
    )
    cmd = r.json()
    assert cmd["status"] == "rejected"
    assert "SAFE_STATE" in (cmd["rejection_reason"] or "").upper() or \
           "safe_state" in (cmd["rejection_reason"] or "")


# --- Commands listing -------------------------------------------------------
def test_commands_listing(owner_device):
    dev_id = owner_device["id"]
    r = httpx.get(f"{API}/devices/{dev_id}/commands?limit=20", timeout=TIMEOUT)
    assert r.status_code == 200
    assert len(r.json()["items"]) >= 1
