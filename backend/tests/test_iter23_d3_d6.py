"""Iteration 23 — D3/D4/D5/D6 backend integration tests."""
import os
import time

import requests
from pymongo import MongoClient

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


# ============================================================================
# D3 — Weaver (already existed; verify still wired)
# ============================================================================
def test_d3_weaver_plans_and_parts_live():
    r = requests.get(f"{BACKEND}/api/weaver/plans", timeout=15)
    assert r.status_code == 200
    assert r.json()["count"] >= 1

    r = requests.get(f"{BACKEND}/api/weaver/parts", timeout=15)
    assert r.status_code == 200
    parts = r.json()["items"]
    assert len(parts) >= 10
    # Every part must have a category + name
    for p in parts:
        assert p.get("category")
        assert p.get("name")


# ============================================================================
# D4 — NIR Scanner
# ============================================================================
def test_d4_nir_library_seeded():
    r = requests.get(f"{BACKEND}/api/nir/library", timeout=15)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 12
    cats = {x["category"] for x in items}
    assert {"plastic", "biological", "agrichem", "organic_compound"} <= cats


def test_d4_nir_synthetic_pet_round_trip():
    """Synthetic PET scan must be identified as PET with confidence ≥ 0.85."""
    r = requests.post(
        f"{BACKEND}/api/nir/scan/synthetic",
        json={"material_name": "PET (polyethylene terephthalate)", "label": "test"},
        timeout=60,
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ok"] is True
    res = d["result"]
    assert len(res["detected_peaks_nm"]) >= 3
    best = res["best_match"]
    assert best is not None
    assert "PET" in best["library_name"]
    assert res["confidence"] >= 0.85, f"low confidence: {res['confidence']}"


def test_d4_nir_validation_rejects_bad_input():
    """Mismatched length or too-few-points must produce a 400."""
    r = requests.post(
        f"{BACKEND}/api/nir/scan",
        json={
            "wavelengths_nm": [900, 1100, 1300],
            "intensities":    [0.1, 0.2],     # length mismatch
        },
        timeout=15,
    )
    assert r.status_code == 400
    body = r.json()
    msg = str(body).lower()
    assert "length mismatch" in msg or "too few points" in msg


def test_d4_nir_results_list_includes_recent_scan():
    """After a synthetic scan the results endpoint must contain it."""
    label = f"test-list-{int(time.time())}"
    r = requests.post(
        f"{BACKEND}/api/nir/scan/synthetic",
        json={"material_name": "HDPE (high-density polyethylene)", "label": label},
        timeout=60,
    )
    assert r.status_code == 200
    spec_id = r.json()["spectrum"]["id"]

    r = requests.get(f"{BACKEND}/api/nir/results?limit=20", timeout=15)
    assert r.status_code == 200
    ids = [it["spectrum_id"] for it in r.json()["items"]]
    assert spec_id in ids


# ============================================================================
# D5 — Green Robot reference twin
# ============================================================================
def test_d5_agri_rover_registered():
    r = requests.get(f"{BACKEND}/api/twins/list", timeout=15)
    assert r.status_code == 200
    twins = r.json()["items"]
    rover = next((t for t in twins if t["name"] == "AGRI-ROVER-01"), None)
    assert rover is not None, "AGRI-ROVER-01 not seeded"
    assert "green_robot" in (rover.get("tags") or [])
    assert "d5" in (rover.get("tags") or [])
    state = rover["state"]
    # ≥ 10 components, has NIR sensor + water pump
    assert len(state["components"]) >= 10
    names = {c["name"] for c in state["components"]}
    assert any("NIR" in n for n in names)
    assert any("pump" in n.lower() for n in names)


def test_d5_agri_rover_blueprint_emitted():
    """A reference blueprint must accompany the rover spec."""
    db = MongoClient(MONGO_URL)[DB_NAME]
    bp = db["blueprints"].find_one({"title": "AGRI-ROVER-01 reference blueprint"})
    assert bp is not None
    assert bp.get("kind") == "reference_twin"
    assert len(bp.get("components") or []) >= 10


# ============================================================================
# D6 — Power Cell ODE thermal sim
# ============================================================================
def test_d6_power_cell_twins_registered():
    r = requests.get(f"{BACKEND}/api/twins/list", timeout=15)
    assert r.status_code == 200
    twins = r.json()["items"]
    names = {t["name"] for t in twins}
    assert "ATLAS-CELL-V1" in names
    assert "ATLAS-CELL-SS-V1" in names


def test_d6_thermal_sim_nominal_safe():
    r = requests.get(f"{BACKEND}/api/twins/list", timeout=15)
    cell = next((t for t in r.json()["items"] if t["name"] == "ATLAS-CELL-V1"))
    cell_id = cell["id"]

    # Ensure nominal 3 A config (other tests may have mutated it)
    db = MongoClient(MONGO_URL)[DB_NAME]
    db["digital_twins"].update_one(
        {"id": cell_id},
        {"$set": {
            "state.integrations.thermal.I_amps": 3.0,
            "state.integrations.thermal.h_w_m2_k": 15.0,
            "state.integrations.thermal.duration_s": 1800,
        }},
    )

    r = requests.post(f"{BACKEND}/api/twins/{cell_id}/simulate",
                      json={"kind": "thermal"}, timeout=60)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["kind"] == "thermal"
    assert d.get("failures") in ([], None), f"unexpected failures: {d.get('failures')}"
    m = d["metrics"]
    assert m["chemistry"] == "li_ion"
    assert m["T_init_c"] == 25.0
    # T_max should be safely under runaway threshold at nominal current
    assert m["T_max_c"] < 60.0, f"T_max too high at nominal: {m['T_max_c']}"
    assert m["headroom_to_runaway_c"] > 10.0
    # ODE integration produced ≥ 50 points
    assert m["ode_points"] >= 50
    # Timeline returned
    assert len(d.get("timeline") or []) >= 5


def test_d6_thermal_sim_detects_runaway():
    """Bump current to 25 A + reduce convection → T_max > threshold."""
    r = requests.get(f"{BACKEND}/api/twins/list", timeout=15)
    cell = next((t for t in r.json()["items"] if t["name"] == "ATLAS-CELL-V1"))
    cell_id = cell["id"]

    db = MongoClient(MONGO_URL)[DB_NAME]
    db["digital_twins"].update_one(
        {"id": cell_id},
        {"$set": {
            "state.integrations.thermal.I_amps": 25.0,
            "state.integrations.thermal.h_w_m2_k": 5.0,
            "state.integrations.thermal.duration_s": 600,
        }},
    )
    try:
        r = requests.post(f"{BACKEND}/api/twins/{cell_id}/simulate",
                          json={"kind": "thermal"}, timeout=60)
        assert r.status_code == 200, r.text
        d = r.json()
        assert any("RUNAWAY" in f for f in (d.get("failures") or [])), \
            f"expected runaway failure, got {d.get('failures')}"
        assert d["metrics"]["T_max_c"] >= 80.0
    finally:
        # Restore nominal
        db["digital_twins"].update_one(
            {"id": cell_id},
            {"$set": {
                "state.integrations.thermal.I_amps": 3.0,
                "state.integrations.thermal.h_w_m2_k": 15.0,
                "state.integrations.thermal.duration_s": 1800,
            }},
        )


def test_d6_solid_state_higher_threshold():
    """Solid-state variant must have a higher runaway threshold (100°C vs 80°C)."""
    r = requests.get(f"{BACKEND}/api/twins/list", timeout=15)
    ss = next((t for t in r.json()["items"] if t["name"] == "ATLAS-CELL-SS-V1"))
    ss_id = ss["id"]
    r = requests.post(f"{BACKEND}/api/twins/{ss_id}/simulate",
                      json={"kind": "thermal"}, timeout=60)
    assert r.status_code == 200
    m = r.json()["metrics"]
    assert m["chemistry"] == "solid_state"
    assert m["thermal_runaway_threshold_c"] == 100.0
