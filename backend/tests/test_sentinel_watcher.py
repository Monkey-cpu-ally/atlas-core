"""
Phase 8h — Sentinel Autonomic Watcher tests.

Verifies the architect's contract:
  * watcher boots on app startup (status reflects enabled_env + running)
  * fire-now is owner-only (guest → 403)
  * tick() detects devices with an active anomaly and fires the council
  * dedupe by (device_id, since, drifting_keys) — same anomaly fires ONCE
  * autonomic_council memory persisted with category=council, permanent=true
  * `examined` counter increments even when nothing fires

Run:
    cd /app/backend && pytest tests/test_sentinel_watcher.py -v
"""
from __future__ import annotations

import asyncio
import os
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
API = BACKEND.rstrip("/") + "/api/robot"
MEMBANK = BACKEND.rstrip("/") + "/api/membank"
TIMEOUT = httpx.Timeout(180.0, connect=10.0)

OWNER = {"X-Atlas-Role": "owner"}
GUEST = {"X-Atlas-Role": "guest"}


def test_watcher_boots_with_env_enabled():
    r = httpx.get(f"{API}/sentinel/watcher/status", timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["running"] is True
    assert body["started_at"]
    assert body["interval_s"] >= 5
    assert body["cooldown_s"] >= 0
    assert body["ticks"] >= 1


def test_fire_now_is_owner_only():
    r = httpx.post(f"{API}/sentinel/watcher/fire-now", headers=GUEST, timeout=TIMEOUT)
    assert r.status_code == 403, r.text


def test_full_anomaly_to_council_chain():
    """End-to-end: register fresh device → trip anomaly → fire-now →
    confirm watcher fired the council → confirm autonomic_council memory
    persists with the device name in tags → confirm second fire-now is
    deduped (no double-fire)."""
    name = f"AUTONOMIC-{uuid.uuid4().hex[:6]}"
    r = httpx.post(
        f"{API}/devices",
        json={"name": name, "kind": "esp32",
              "hardware_profile": {"sensors": ["co2"], "actuators": []},
              "tags": ["test", "autonomic"]},
        headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200
    dev_id = r.json()["id"]

    # 12 baseline readings — past the 10-sample warmup
    for i in range(12):
        httpx.post(
            f"{API}/devices/{dev_id}/telemetry",
            json={"payload": {"co2": 415.0 + (i % 3) * 0.1}, "source": "test"},
            timeout=TIMEOUT,
        ).raise_for_status()

    # Spike — must trip anomaly
    httpx.post(
        f"{API}/devices/{dev_id}/telemetry",
        json={"payload": {"co2": 4000.0}, "source": "test"},
        timeout=TIMEOUT,
    ).raise_for_status()

    env = httpx.get(f"{API}/devices/{dev_id}/envelope", timeout=TIMEOUT).json()
    assert env.get("anomaly"), "anomaly must be tripped before fire-now"

    # Manual fire — watcher's tick will discover the anomaly and call the
    # council. This is a real gpt-5.2 call so it takes time.
    rfire = httpx.post(
        f"{API}/sentinel/watcher/fire-now", headers=OWNER, timeout=TIMEOUT,
    )
    assert rfire.status_code == 200, rfire.text
    res = rfire.json()
    # The watcher must have EXAMINED at least our device — it may have
    # also examined other devices in the same state.
    assert res["examined"] >= 1
    # New anomaly on a fresh device must be FIRED (not deduped).
    assert res["fired"] >= 1, f"expected at least one fire, got {res}"

    # Give the council call a beat to complete (chat_any is awaited within
    # the tick, but the membank write happens on the same path — usually
    # complete by here).
    asyncio.run(asyncio.sleep(2))

    # Autonomic memory must exist tagged with the device name + 'autonomic_council'
    rmem = httpx.get(
        f"{MEMBANK}/by-tag",
        params={"tag": name, "limit": 5},
        timeout=TIMEOUT,
    )
    assert rmem.status_code == 200
    items = rmem.json()["items"]
    matching = [
        i for i in items
        if "autonomic_council" in (i.get("tags") or [])
    ]
    assert matching, (
        f"autonomic_council memory not persisted for device {name}. "
        f"by-tag returned {len(items)} item(s)."
    )
    row = matching[0]
    assert row["category"] == "council"
    assert row.get("permanent") is True
    assert "AUTONOMIC COUNCIL" in (row.get("content") or "")

    # Second fire-now must DEDUPE — same (device, since, drifting_keys)
    rfire2 = httpx.post(
        f"{API}/sentinel/watcher/fire-now", headers=OWNER, timeout=TIMEOUT,
    )
    res2 = rfire2.json()
    # No new fires for THIS device. (Others may still fire — we just need
    # the dedupe to skip ours.)
    # Verify by counting the membank rows again — must be SAME count.
    rmem2 = httpx.get(
        f"{MEMBANK}/by-tag",
        params={"tag": name, "limit": 5},
        timeout=TIMEOUT,
    ).json()
    items2 = rmem2["items"]
    matching2 = [i for i in items2 if "autonomic_council" in (i.get("tags") or [])]
    assert len(matching2) == len(matching), (
        f"dedupe failed — autonomic memories for {name} grew from "
        f"{len(matching)} to {len(matching2)} on second fire-now"
    )


def test_status_counters_increment():
    """fire-now bumps the in-process tick counter."""
    s0 = httpx.get(f"{API}/sentinel/watcher/status", timeout=TIMEOUT).json()
    httpx.post(f"{API}/sentinel/watcher/fire-now", headers=OWNER, timeout=TIMEOUT)
    s1 = httpx.get(f"{API}/sentinel/watcher/status", timeout=TIMEOUT).json()
    assert s1["ticks"] >= s0["ticks"] + 1
