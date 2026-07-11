"""Iteration 16 tests.

Covers:
1. Voice → Ingest end-to-end via POST /api/kbase/ingest:
   - Returned record carries summary, key_points, tags, source_url,
     source_type='github', related_agents, related_projects, memory_bank_id.
2. Memory Bank wiring — GET /api/membank/search?q=whisper finds the record.
3. Robot Control permission verification — guest cannot ACTUATE, owner can.
4. Sentinel SAFE_STATE — emergency_stop flips device status to safe_state.
"""
import os
import time
import uuid
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fall back to reading frontend/.env directly when run inside the container.
    with open("/app/frontend/.env") as fh:
        for line in fh:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                break
assert BASE_URL, "REACT_APP_BACKEND_URL required"


# ---------------------------------------------------------------------------
# 1) Voice → Ingest end-to-end
# ---------------------------------------------------------------------------
def test_ingest_url_returns_full_record_shape():
    """POST /api/kbase/ingest with a github URL — verify record schema."""
    payload = {"url": "https://github.com/openai/whisper"}
    r = requests.post(f"{BASE_URL}/api/kbase/ingest", json=payload, timeout=60)
    assert r.status_code == 200, f"got {r.status_code}: {r.text[:300]}"
    body = r.json()
    assert "record" in body, body
    rec = body["record"]
    # Schema fields required by Phase 7 spec:
    for field in ("summary", "key_points", "tags", "source_url",
                  "source_type", "related_agents", "related_projects"):
        assert field in rec, f"missing field {field}: {list(rec.keys())}"
    assert rec["source_url"] == "https://github.com/openai/whisper"
    assert rec["source_type"] == "github", rec["source_type"]
    assert isinstance(rec["key_points"], list)
    assert isinstance(rec["tags"], list)
    assert isinstance(rec["related_agents"], list)
    assert isinstance(rec["related_projects"], list)
    assert "memory_bank_id" in body and body["memory_bank_id"], body


# ---------------------------------------------------------------------------
# 2) Memory Bank search wiring
# ---------------------------------------------------------------------------
def test_membank_search_finds_whisper_record():
    # Make sure the record exists (idempotent).
    requests.post(f"{BASE_URL}/api/kbase/ingest",
                  json={"url": "https://github.com/openai/whisper"}, timeout=60)
    # Small delay to allow indexing.
    time.sleep(1)
    r = requests.get(f"{BASE_URL}/api/membank/search",
                     params={"q": "whisper"}, timeout=20)
    assert r.status_code == 200, r.text[:300]
    data = r.json()
    items = data.get("items") or data.get("results") or data
    assert items, f"no items in membank for 'whisper': {data}"
    # at least one row must reference whisper / the URL
    blob = str(items).lower()
    assert "whisper" in blob, blob[:500]


# ---------------------------------------------------------------------------
# 3) Robot Control permission verification (guest vs owner ACTUATE)
# ---------------------------------------------------------------------------
def _get_device_id(name):
    # Seed devices are older than test-created devices, so the default
    # limit=50 buries them past the pagination cutoff. Ask for a full
    # page so the roll-up stays deterministic.
    r = requests.get(f"{BASE_URL}/api/robot/devices", params={"limit": 200}, timeout=10)
    assert r.status_code == 200, r.text[:200]
    for d in r.json().get("items", []):
        if d["name"] == name:
            return d["id"]
    raise AssertionError(f"{name} seed device not found")


def _get_poseidon_id():
    return _get_device_id("POSEIDON-BUOY")


def test_guest_cannot_actuate_owner_can_actuate():
    # Use AETHER-STATION so POSEIDON-BUOY can be left in safe_state by the
    # next test without polluting this one.
    dev_id = _get_device_id("AETHER-STATION")

    # Guest ACTUATE — must be rejected
    guest_cmd = {"kind": "actuate", "args": {"channel": "lamp", "value": 1}}
    g = requests.post(
        f"{BASE_URL}/api/robot/devices/{dev_id}/command",
        json=guest_cmd,
        headers={"X-Atlas-Role": "guest"},
        timeout=10,
    )
    # Spec: returns 200 with status='rejected' OR 403
    assert g.status_code in (200, 403), g.text[:300]
    if g.status_code == 200:
        gj = g.json()
        cmd = gj.get("command") or gj
        assert cmd.get("status") == "rejected", gj
        reason = (cmd.get("reason") or cmd.get("rejection_reason") or "").lower()
        assert "owner" in reason or "role" in reason, gj
    print(f"[guest ACTUATE rejected] {g.status_code} :: {g.text[:200]}")

    # Owner ACTUATE — must succeed (simulated, since twin-bound)
    o = requests.post(
        f"{BASE_URL}/api/robot/devices/{dev_id}/command",
        json=guest_cmd,
        headers={"X-Atlas-Role": "owner"},
        timeout=15,
    )
    assert o.status_code == 200, o.text[:300]
    oj = o.json()
    cmd = oj.get("command") or oj
    assert cmd.get("status") != "rejected", oj
    print(f"[owner ACTUATE accepted] status={cmd.get('status')}")


# ---------------------------------------------------------------------------
# 4) Emergency-stop flips device into safe_state (for Sentinel visual)
# ---------------------------------------------------------------------------
def test_emergency_stop_owner_flips_safe_state():
    dev_id = _get_poseidon_id()
    r = requests.post(
        f"{BASE_URL}/api/robot/devices/{dev_id}/emergency-stop",
        headers={"X-Atlas-Role": "owner"},
        timeout=10,
    )
    assert r.status_code == 200, r.text[:300]
    # Verify status reflects safe_state
    g = requests.get(f"{BASE_URL}/api/robot/devices", timeout=10)
    for d in g.json().get("items", []):
        if d["id"] == dev_id:
            assert d.get("status") == "safe_state", d
            return
    raise AssertionError("device row missing after e-stop")
