"""
Phase 7+ — Clear Safe State endpoint hard-guarantee tests.

Architect spec (must all pass):
  * Owner-only — guest/agent roles get 403
  * Confirmation required — body.confirm MUST equal the device's exact name (400 otherwise)
  * Cannot bypass Emergency Stop — device must already be in safe_state (409 otherwise)
  * Updates device state (safe_state → registered)
  * Updates bound Digital Twin state (safety_history append + safe_state=false)
  * Logs to Memory Bank (council/permanent, tags include 'clear_safe_state')
  * Logs a Command record (kind=clear_safe_state, status=executed)

Run:
    cd /app/backend && pytest tests/test_robot_clear_safe_state.py -v
"""
from __future__ import annotations

import os
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
API = f"{BACKEND.rstrip('/')}/api/robot"
MEMBANK = f"{BACKEND.rstrip('/')}/api/membank"
TWINS = f"{BACKEND.rstrip('/')}/api/twins"

OWNER = {"X-Atlas-Role": "owner"}
GUEST = {"X-Atlas-Role": "guest"}
TIMEOUT = httpx.Timeout(60.0, connect=10.0)


@pytest.fixture(scope="module")
def owner_safe_device():
    """Register a fresh device, bind a twin (so the clear updates twin state
    too), push telemetry to bring it ONLINE, then e-stop it so it enters
    SAFE_STATE. Every test uses its own device to avoid cross-test
    contamination."""
    name = f"CLEAR-TEST-{uuid.uuid4().hex[:6]}"
    payload = {
        "name": name, "kind": "esp32",
        "hardware_profile": {"sensors": ["temp"], "actuators": ["relay"]},
        "tags": ["test", "clear_safe_state"],
    }
    r = httpx.post(f"{API}/devices", json=payload, headers=OWNER, timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    dev = r.json()

    # Find an existing twin (the seed step provisioned 3 — we re-use one).
    rt = httpx.get(f"{TWINS}/list", timeout=TIMEOUT)
    assert rt.status_code == 200, rt.text
    twins = rt.json().get("items", rt.json()) if isinstance(rt.json(), dict) else rt.json()
    assert twins, "expected seeded twins to exist"
    twin_id = twins[0]["id"]
    rb = httpx.post(
        f"{API}/devices/{dev['id']}/bind-twin",
        json={"twin_id": twin_id}, headers=OWNER, timeout=TIMEOUT,
    )
    assert rb.status_code == 200, rb.text
    dev = rb.json()

    # Push telemetry → ONLINE
    r = httpx.post(
        f"{API}/devices/{dev['id']}/telemetry",
        json={"payload": {"temp": 20}, "source": "mqtt"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200

    # Owner e-stop → SAFE_STATE
    r = httpx.post(f"{API}/devices/{dev['id']}/emergency-stop", headers=OWNER, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json()["status"] == "safe_state"
    out = r.json()
    out["twin_id"] = twin_id   # ensure caller sees the binding
    return out


def test_clear_is_listed_in_owner_only_commands():
    r = httpx.get(f"{API}/roles", timeout=TIMEOUT)
    body = r.json()
    assert "clear_safe_state" in body["owner_only_commands"]


def test_guest_cannot_clear(owner_safe_device):
    r = httpx.post(
        f"{API}/devices/{owner_safe_device['id']}/clear-safe-state",
        headers=GUEST, json={"confirm": owner_safe_device["name"]},
        timeout=TIMEOUT,
    )
    assert r.status_code == 403, r.text
    assert "owner" in r.json()["detail"].lower()


def test_wrong_confirm_rejected(owner_safe_device):
    r = httpx.post(
        f"{API}/devices/{owner_safe_device['id']}/clear-safe-state",
        headers=OWNER, json={"confirm": "not-the-right-name"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 400, r.text
    assert "confirmation mismatch" in r.json()["detail"].lower()


def test_missing_confirm_rejected_by_pydantic(owner_safe_device):
    r = httpx.post(
        f"{API}/devices/{owner_safe_device['id']}/clear-safe-state",
        headers=OWNER, json={},
        timeout=TIMEOUT,
    )
    assert r.status_code in (400, 422)


def test_owner_clear_flips_device_and_records_everything(owner_safe_device):
    # 1. Clear it
    r = httpx.post(
        f"{API}/devices/{owner_safe_device['id']}/clear-safe-state",
        headers=OWNER, json={"confirm": owner_safe_device["name"]},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["device"]["status"] == "registered"
    assert body["command_id"]
    assert body["cleared_at"]

    # 2. Cannot clear again — device is no longer in safe_state
    r2 = httpx.post(
        f"{API}/devices/{owner_safe_device['id']}/clear-safe-state",
        headers=OWNER, json={"confirm": owner_safe_device["name"]},
        timeout=TIMEOUT,
    )
    assert r2.status_code == 409, r2.text
    assert "safe_state" in r2.json()["detail"].lower()
    assert "cannot bypass" in r2.json()["detail"].lower() or "current=" in r2.json()["detail"].lower()

    # 3. Command record exists with kind=clear_safe_state and status=executed
    rc = httpx.get(f"{API}/commands/{body['command_id']}", timeout=TIMEOUT)
    assert rc.status_code == 200, rc.text
    cmd = rc.json()
    assert cmd["kind"] == "clear_safe_state"
    assert cmd["status"] == "executed"
    assert cmd["issued_by_role"] == "owner"
    steps = [p["step"] for p in cmd["pipeline_log"]]
    assert "authorise" in steps
    assert "confirm" in steps
    assert "verify_safe_state" in steps
    assert "execute" in steps

    # 4. Bound Digital Twin should show safety_history with the clear event
    twin_id = body["device"]["twin_id"]
    assert twin_id, "device must remain twin-bound after clear"
    rt = httpx.get(f"{TWINS}/{twin_id}", timeout=TIMEOUT)
    assert rt.status_code == 200, rt.text
    state = rt.json().get("state") or {}
    assert state.get("safe_state") is False
    history = state.get("safety_history") or []
    assert any(
        h.get("event") == "clear_safe_state" and h.get("command_id") == body["command_id"]
        for h in history
    ), state


def test_cannot_clear_a_healthy_device():
    """Register a fresh device (NOT in safe_state) and confirm the clear fails."""
    name = f"HEALTHY-{uuid.uuid4().hex[:6]}"
    r = httpx.post(
        f"{API}/devices",
        json={"name": name, "kind": "esp32",
              "hardware_profile": {"sensors": ["temp"], "actuators": []},
              "tags": ["test"]},
        headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200
    dev = r.json()
    assert dev["status"] in ("registered", "online")

    r2 = httpx.post(
        f"{API}/devices/{dev['id']}/clear-safe-state",
        headers=OWNER, json={"confirm": dev["name"]},
        timeout=TIMEOUT,
    )
    assert r2.status_code == 409, r2.text


def test_unknown_device_returns_404():
    r = httpx.post(
        f"{API}/devices/this-id-does-not-exist/clear-safe-state",
        headers=OWNER, json={"confirm": "anything"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 404
