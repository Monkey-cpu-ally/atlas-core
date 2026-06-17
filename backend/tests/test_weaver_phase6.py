"""
Phase 6 — Weaver smoke tests.

Exercises:
  * parts library CRUD + search + idempotent seed
  * blueprint analyze (structured)
  * full plan pipeline (structured) without LLM deliberation for speed
  * full plan pipeline (deliberate=true) is covered by ONE slow test
  * plans list + get + delete (with and without twin cascade)

Run:
    cd /app/backend && pytest tests/test_weaver_phase6.py -v
"""
import os
import time
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
        {"from_part": "ESP32-S3 module", "to_part": "MPU6050 IMU",      "relation": "signals"},
        {"from_part": "Custom carbon arm","to_part": "SG90 micro servo","relation": "mounts"},
    ],
}


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=180.0) as c:
        # ensure library has the starter rows
        c.post(f"{API}/weaver/parts/seed")
        yield c


def test_part_categories(client):
    r = client.get(f"{API}/weaver/parts/categories")
    assert r.status_code == 200
    cats = r.json()["categories"]
    for c in ("component", "material", "fastener", "electronic",
              "sensor", "actuator", "tool", "consumable"):
        assert c in cats


def test_seed_idempotent(client):
    r1 = client.post(f"{API}/weaver/parts/seed").json()
    r2 = client.post(f"{API}/weaver/parts/seed").json()
    assert r2["seeded"] == 0    # second call seeds nothing


def test_parts_search_by_category(client):
    r = client.get(f"{API}/weaver/parts?category=actuator&limit=50")
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    for p in items:
        assert p["category"] == "actuator"


def test_parts_search_by_q(client):
    r = client.get(f"{API}/weaver/parts?q=esp32")
    assert r.status_code == 200
    items = r.json()["items"]
    assert any("ESP32" in p["name"] for p in items)


def test_add_and_delete_part(client):
    payload = {
        "name": f"PYTEST_part_{uuid.uuid4().hex[:6]}",
        "category": "electronic",
        "default_cost": 1.23,
    }
    r = client.post(f"{API}/weaver/parts", json=payload)
    assert r.status_code == 200, r.text
    pid = r.json()["id"]
    g = client.get(f"{API}/weaver/parts/{pid}")
    assert g.status_code == 200 and g.json()["name"] == payload["name"]
    d = client.delete(f"{API}/weaver/parts/{pid}")
    assert d.status_code == 200
    assert client.get(f"{API}/weaver/parts/{pid}").status_code == 404


def test_analyze_structured(client):
    r = client.post(f"{API}/weaver/analyze", json={"blueprint": PAN_TILT_BP})
    assert r.status_code == 200, r.text
    d = r.json()
    assert len(d["parts"]) == 6
    # 5 of 6 should match library; "Custom carbon arm" is the misfit
    assert d["library_match_count"] >= 5
    assert d["unknown_count"] == 1
    assert any(p["name"] == "Custom carbon arm" and p["library_part_id"] is None
               for p in d["parts"])


def test_analyze_invalid_category_coerces(client):
    bp = {
        "format": "json",
        "parts": [{"name": "Test thing", "category": "nonsense"}],
    }
    r = client.post(f"{API}/weaver/analyze", json={"blueprint": bp})
    # Bad category coerces to 'component' rather than 400 — that's the
    # blueprint_parser._coerce_part contract.
    assert r.status_code == 200
    assert r.json()["parts"][0]["category"] == "component"


def test_plan_full_pipeline_no_council(client):
    body = {
        "title": f"PYTEST plan {uuid.uuid4().hex[:6]}",
        "description": "Test pan/tilt rig",
        "owner_agent": "ajani",
        "deliberate": False,
        "blueprint": PAN_TILT_BP,
    }
    r = client.post(f"{API}/weaver/plan", json=body)
    assert r.status_code == 200, r.text
    plan = r.json()
    assert plan["twin_id"]
    assert plan["parts_extracted"] and len(plan["parts_extracted"]) == 6
    bp = plan["build_plan"]
    assert bp["difficulty"] in {"trivial", "easy", "medium", "hard", "expert"}
    assert bp["total_estimated_minutes"] > 0
    assert bp["assembly_order"]
    assert "Soldering iron" in bp["tools_required"]
    mp = plan["manufacturing_plan"]
    assert mp["total_cost"] > 0
    assert mp["critical_path_days"] > 0
    assert mp["longest_lead_part"]
    fp = plan["failure_prediction"]
    assert 0.0 <= fp["risk_score"] <= 1.0
    assert "Custom carbon arm" in fp["missing_parts"]
    assert plan["council"] is None    # deliberate=false
    # ----- cleanup
    client.delete(f"{API}/weaver/plans/{plan['id']}?drop_twin=true")


def test_plan_blank_blueprint_returns_400(client):
    body = {
        "title": "PYTEST empty",
        "blueprint": {"format": "text", "text": ""},
    }
    r = client.post(f"{API}/weaver/plan", json=body)
    assert r.status_code == 400


def test_plan_title_validation(client):
    body = {
        "title": "x",          # min_length=2 → 422
        "blueprint": {"format": "json", "parts": [{"name": "a"}]},
    }
    r = client.post(f"{API}/weaver/plan", json=body)
    assert r.status_code == 422


def test_plans_list_filter_and_delete(client):
    body = {
        "title": f"PYTEST listable {uuid.uuid4().hex[:6]}",
        "owner_agent": "minerva",
        "deliberate": False,
        "blueprint": PAN_TILT_BP,
    }
    plan = client.post(f"{API}/weaver/plan", json=body).json()
    r = client.get(f"{API}/weaver/plans?owner_agent=minerva&limit=10")
    assert r.status_code == 200
    ids = {p["id"] for p in r.json()["items"]}
    assert plan["id"] in ids
    # delete WITHOUT cascading twin — twin should still exist
    r = client.delete(f"{API}/weaver/plans/{plan['id']}")
    assert r.status_code == 200
    assert client.get(f"{API}/weaver/plans/{plan['id']}").status_code == 404
    twin_resp = client.get(f"{API}/twins/{plan['twin_id']}")
    assert twin_resp.status_code == 200   # twin survived
    client.delete(f"{API}/twins/{plan['twin_id']}")   # cleanup


def test_plan_memory_wiring(client):
    body = {
        "title": f"PYTEST mem {uuid.uuid4().hex[:6]}",
        "deliberate": False,
        "blueprint": PAN_TILT_BP,
    }
    plan = client.post(f"{API}/weaver/plan", json=body).json()
    time.sleep(0.5)
    r = httpx.get(f"{API}/membank/list?category=blueprint&limit=50", timeout=15)
    rows = r.json()["items"]
    assert any(row.get("source_id") == plan["id"] for row in rows), \
        "expected a blueprint memory row anchored to the new plan"
    client.delete(f"{API}/weaver/plans/{plan['id']}?drop_twin=true")


@pytest.mark.slow
def test_plan_with_council_deliberation(client):
    """LLM-bound — ~30-60s. Verifies the council outcome is attached."""
    body = {
        "title": f"PYTEST council {uuid.uuid4().hex[:6]}",
        "owner_agent": "ajani",
        "deliberate": True,
        "blueprint": PAN_TILT_BP,
    }
    plan = client.post(f"{API}/weaver/plan", json=body, timeout=180).json()
    assert plan.get("council") is not None
    c = plan["council"]
    assert c["verdict"] in {"approve", "revise", "reject", "pending"}
    assert len(c["voices"]) == 4
    assert c["final_text"]
    client.delete(f"{API}/weaver/plans/{plan['id']}?drop_twin=true")
