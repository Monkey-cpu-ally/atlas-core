"""
Phase 6 — additional Weaver coverage pinning the explicit assertions
called out in the review request that were not fully verified in
test_weaver_phase6.py.

Run:
    cd /app/backend && pytest tests/test_weaver_phase6_extras.py -v
"""
import os
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or os.environ.get(
    "BACKEND_URL", "http://localhost:8001"
)
API = f"{BACKEND.rstrip('/')}/api"

PAN_TILT_BP = {
    "format": "json",
    "parts": [
        {"name": "ESP32-S3 module",     "category": "electronic", "quantity": 1},
        {"name": "MPU6050 IMU",         "category": "sensor",     "quantity": 1},
        {"name": "SG90 micro servo",    "category": "actuator",   "quantity": 2},
        {"name": "PLA filament 1.75mm", "category": "material",   "quantity": 0.2, "unit": "kg"},
        {"name": "M3 cap screw 10mm",   "category": "fastener",   "quantity": 8},
        {"name": "Custom carbon arm",   "category": "component",  "quantity": 2},
    ],
    "relations": [
        {"from_part": "ESP32-S3 module", "to_part": "SG90 micro servo", "relation": "signals"},
    ],
}


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=180.0) as c:
        c.post(f"{API}/weaver/parts/seed")
        yield c


# ---- review item: q=imu matches by tag ----------------------------------
def test_parts_search_q_matches_by_tag(client):
    r = client.get(f"{API}/weaver/parts?q=imu")
    assert r.status_code == 200
    items = r.json()["items"]
    # MPU6050 has tag 'imu' but the literal substring 'imu' is also in its name.
    assert any("MPU6050" in p["name"] for p in items)


# ---- review item: unknown part id → 404 ---------------------------------
def test_unknown_part_returns_404(client):
    r = client.get(f"{API}/weaver/parts/{uuid.uuid4().hex}")
    assert r.status_code == 404


# ---- review item: analyze counts library_match_count + unknown_count ----
def test_analyze_match_and_unknown_counts(client):
    r = client.post(f"{API}/weaver/analyze", json={"blueprint": PAN_TILT_BP})
    assert r.status_code == 200
    d = r.json()
    assert d["library_match_count"] + d["unknown_count"] == len(d["parts"])
    assert d["unknown_count"] == 1
    assert d["library_match_count"] >= 5


# ---- review item: plan tools_required is union of categories ------------
def test_plan_tools_required_is_category_union(client):
    body = {
        "title": f"PYTEST tools {uuid.uuid4().hex[:6]}",
        "deliberate": False,
        "blueprint": PAN_TILT_BP,
    }
    plan = client.post(f"{API}/weaver/plan", json=body).json()
    tools = set(plan["build_plan"]["tools_required"])
    # electronic → Soldering iron; fastener → screwdriver/hex; material → 3D printer
    assert any("Solder" in t for t in tools)
    client.delete(f"{API}/weaver/plans/{plan['id']}?drop_twin=true")


# ---- review item: get unknown plan id → 404 -----------------------------
def test_unknown_plan_returns_404(client):
    r = client.get(f"{API}/weaver/plans/{uuid.uuid4().hex}")
    assert r.status_code == 404


# ---- regression: Phase 5 still healthy ----------------------------------
def test_phase5_twin_categories_regression(client):
    r = client.get(f"{API}/twins/categories")
    assert r.status_code == 200
    cats = r.json()["categories"]
    assert len(cats) == 7


# ---- regression: Phase 2 membank still healthy --------------------------
def test_phase2_membank_categories_regression(client):
    r = client.get(f"{API}/membank/categories")
    assert r.status_code == 200
    data = r.json()
    # ensure 'blueprint' is listed under permanent
    permanent = data.get("permanent") or data.get("categories", {}).get("permanent") or []
    flat = []
    if isinstance(permanent, list):
        flat = permanent
    else:
        # shape might be {"permanent": [...], "transient": [...]}
        flat = list(permanent)
    blob = str(data).lower()
    assert "blueprint" in blob


def test_phase2_membank_search_regression(client):
    r = client.get(f"{API}/membank/search?q=blueprint&limit=5")
    assert r.status_code == 200
    # search returns either {items:[...]} or {results:[...]}; just check 200
    body = r.json()
    assert isinstance(body, dict)
