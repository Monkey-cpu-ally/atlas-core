"""
Phase 5 — Digital Twin Engine: additional coverage for the gaps not
covered by test_twins_phase5.py.

Covers:
  - 422 on invalid category and short name
  - list filter combinations (project_id + owner_agent + status)
  - assembly sim topological order
  - resource sim BOM + total_mass_kg + material_count
  - timeline sim critical_path_days + timeline path
  - cost sim materials_cost / labour_estimate / total_estimate / line_cost
  - deliberate with explicit simulation_id
  - GET /api/twins/simulations/<unknown> → 404
  - register writes a project memory tagged TWIN
  - Phase-2 membank + Phase-3 research regression smoke
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


ROBOT_SPEC = {
    "components": [
        {"id": "frame", "name": "Frame",   "quantity": 1, "unit": "unit", "material": "CFRP",
         "mass_kg": 0.12, "cost_per_unit": 42, "lead_time_days": 7},
        {"id": "mcu",   "name": "MCU",     "quantity": 1, "unit": "unit", "material": "Si",
         "mass_kg": 0.01, "cost_per_unit": 18, "lead_time_days": 5},
        {"id": "motor", "name": "Motor",   "quantity": 4, "unit": "unit", "material": "Cu",
         "mass_kg": 0.025, "cost_per_unit": 12, "lead_time_days": 10},
        {"id": "batt",  "name": "Battery", "quantity": 1, "unit": "unit", "material": "Li",
         "mass_kg": 0.06, "cost_per_unit": 22, "lead_time_days": 4},
    ],
    "materials": ["CFRP", "Si", "Cu", "Li"],
    "energy": {"peak_w": 40.0, "average_w": 12.0, "daily_wh": 35.0, "source": "battery"},
    "dimensions": {"length_m": 0.18, "width_m": 0.18, "height_m": 0.05, "mass_kg": 0.3},
    "dependencies": [
        {"from_component": "frame", "to_component": "motor", "kind": "mounts"},
        {"from_component": "batt",  "to_component": "motor", "kind": "powers"},
        {"from_component": "batt",  "to_component": "mcu",   "kind": "powers"},
        {"from_component": "mcu",   "to_component": "motor", "kind": "signals"},
    ],
    "sensor_inputs": [{"name": "IMU", "kind": "motion", "unit": "m/s2"}],
    "outputs": [{"name": "flight", "kind": "motion"}],
}


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=120.0) as c:
        yield c


@pytest.fixture
def twin_id(client):
    payload = {
        "name": f"PYTEST_extra_{uuid.uuid4().hex[:6]}",
        "category": "robot",
        "owner_agent": "ajani",
        "description": "Phase5 extras twin",
        "tags": ["pytest", "extras"],
        "state": ROBOT_SPEC,
    }
    r = client.post(f"{API}/twins/register", json=payload)
    assert r.status_code == 200, r.text
    tid = r.json()["id"]
    yield tid
    client.delete(f"{API}/twins/{tid}")


# ------------------------- Validation ---------------------------------

def test_register_invalid_category_returns_422(client):
    r = client.post(f"{API}/twins/register", json={
        "name": f"PYTEST_bad_{uuid.uuid4().hex[:6]}",
        "category": "spaceship",       # not in enum
        "state": {"components": [{"id": "a", "name": "A"}]},
    })
    assert r.status_code == 422, r.text


def test_register_short_name_returns_422(client):
    r = client.post(f"{API}/twins/register", json={
        "name": "X",                    # <2 chars
        "category": "device",
        "state": {"components": [{"id": "a", "name": "A"}]},
    })
    assert r.status_code == 422, r.text


# ------------------------- List filters -------------------------------

def test_list_filter_combination(client, twin_id):
    # owner_agent=ajani + category=robot + status=spec should include the
    # newly registered twin.
    r = client.get(
        f"{API}/twins/list",
        params={
            "category": "robot",
            "owner_agent": "ajani",
            "status": "spec",
            "limit": 50,
        },
    )
    assert r.status_code == 200, r.text
    items = r.json()["items"]
    assert any(t["id"] == twin_id for t in items)
    # And every returned twin matches the filter.
    for t in items:
        assert t["category"] == "robot"
        assert t["owner_agent"] == "ajani"
        assert t["state"]["status"] == "spec"


# ------------------------- Simulator metrics --------------------------

def test_assembly_topological_order(client, twin_id):
    r = client.post(f"{API}/twins/{twin_id}/simulate", json={"kind": "assembly"})
    assert r.status_code == 200, r.text
    d = r.json()
    timeline = d.get("timeline") or []
    assert len(timeline) == 4
    # Topological invariant: every dep parent appears at an index <= child.
    order = {step.get("component_id") or step.get("id") or step.get("name"): i
             for i, step in enumerate(timeline)}
    deps = ROBOT_SPEC["dependencies"]
    for dep in deps:
        a, b = dep["from_component"], dep["to_component"]
        if a in order and b in order:
            assert order[a] <= order[b], (
                f"assembly order violates dep {a}->{b}: {order}"
            )


def test_resource_bom_and_metrics(client, twin_id):
    r = client.post(f"{API}/twins/{twin_id}/simulate", json={"kind": "resource"})
    assert r.status_code == 200, r.text
    d = r.json()
    bom = d.get("bom") or []
    assert len(bom) == 4
    metrics = d["metrics"]
    assert "total_mass_kg" in metrics
    assert "material_count" in metrics
    assert metrics["material_count"] >= 4
    # Expected total = 0.12 + 0.01 + 0.025*4 + 0.06 = 0.29
    assert abs(metrics["total_mass_kg"] - 0.29) < 0.05


def test_timeline_metrics(client, twin_id):
    r = client.post(f"{API}/twins/{twin_id}/simulate", json={"kind": "timeline"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert "critical_path_days" in d["metrics"]
    assert d["metrics"]["critical_path_days"] > 0
    assert d.get("timeline") and len(d["timeline"]) >= 1


def test_cost_metrics_and_line_cost(client, twin_id):
    r = client.post(f"{API}/twins/{twin_id}/simulate", json={"kind": "cost"})
    assert r.status_code == 200, r.text
    d = r.json()
    m = d["metrics"]
    for key in ("materials_cost", "labour_estimate", "total_estimate"):
        assert key in m, f"missing metric {key}"
        assert m[key] >= 0
    bom = d.get("bom") or []
    assert bom
    assert all("line_cost" in row for row in bom)


# ------------------------- Sim history 404 ----------------------------

def test_simulation_unknown_id_404(client):
    r = client.get(f"{API}/twins/simulations/sim-does-not-exist")
    assert r.status_code == 404


# ------------------------- Deliberate w/ explicit sim_id --------------

def test_deliberate_with_explicit_simulation_id(client, twin_id):
    sim1 = client.post(
        f"{API}/twins/{twin_id}/simulate", json={"kind": "blueprint"}
    ).json()
    # second sim becomes last_simulation_id
    client.post(f"{API}/twins/{twin_id}/simulate", json={"kind": "failure"})
    # Force deliberation on sim1, not the latest.
    r = client.post(
        f"{API}/twins/{twin_id}/deliberate",
        json={"simulation_id": sim1["id"]},
        timeout=180,
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d.get("simulation_id") == sim1["id"]
    personas = [v["persona"] for v in d["voices"]]
    assert personas == ["ajani", "minerva", "hermes", "council"]
    # council voice should be the verdict role
    council = [v for v in d["voices"] if v["persona"] == "council"][0]
    assert council.get("role") == "verdict"
    assert d["verdict"] in {"approve", "revise", "reject", "pending"}
    assert d["final_text"]


# ------------------------- Memory wiring (project) --------------------

def test_register_writes_project_memory(client):
    payload = {
        "name": f"PYTEST_proj_{uuid.uuid4().hex[:6]}",
        "category": "device",
        "owner_agent": "ajani",
        "state": {"components": [{"id": "a", "name": "A"}]},
    }
    r = client.post(f"{API}/twins/register", json=payload)
    assert r.status_code == 200, r.text
    twin = r.json()
    try:
        time.sleep(0.5)
        r2 = httpx.get(
            f"{API}/membank/list",
            params={"category": "project", "limit": 100},
            timeout=15,
        )
        rows = r2.json()["items"]
        hit = next(
            (row for row in rows if row.get("source_id") == twin["id"]),
            None,
        )
        assert hit is not None, "no project memory referencing the new twin"
        # Tags should include a TWIN marker (case-insensitive). Either
        # 'twin' or 'twin-registered' style is acceptable.
        tags_lower = [str(t).lower() for t in (hit.get("tags") or [])]
        assert any("twin" in t for t in tags_lower), (
            f"project memory missing TWIN tag; tags={hit.get('tags')}"
        )
    finally:
        client.delete(f"{API}/twins/{twin['id']}")


# ------------------------- Phase-2 / Phase-3 regression ---------------

def test_membank_list_still_works(client):
    r = client.get(f"{API}/membank/list", params={"limit": 5})
    assert r.status_code == 200, r.text
    j = r.json()
    assert "items" in j and isinstance(j["items"], list)


def test_research_recent_still_works(client):
    r = client.get(f"{API}/research/recent", params={"limit": 5})
    # Some envs may return 503 if upstream missing; allow that.
    assert r.status_code in (200, 503), r.text
    if r.status_code == 200:
        assert "items" in r.json()
