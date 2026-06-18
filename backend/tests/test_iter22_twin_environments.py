"""Phase D2 — Twin Environments backend integration test."""
import os
import requests

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")


def test_envs_seeded_and_listed():
    """The startup hook must have seeded ≥ 5 environments."""
    r = requests.get(f"{BACKEND}/api/environments", timeout=15.0)
    assert r.status_code == 200
    d = r.json()
    assert d["count"] >= 5
    names = {e["name"] for e in d["items"]}
    assert {"Atlas Lab A", "Outdoor Test Field",
            "Aerial Low Airspace", "Aquatic Surface (Lake Test)",
            "Simulated Lunar Sandbox"} <= names


def test_env_categories_present():
    for cat in ("indoor_lab", "outdoor_terrain", "aerial_low",
                "aquatic_surface", "lunar"):
        r = requests.get(f"{BACKEND}/api/environments", params={"category": cat}, timeout=15.0)
        assert r.status_code == 200
        assert r.json()["count"] >= 1, f"no env in category {cat}"


def test_env_create_delete_round_trip():
    payload = {
        "name": "EPHEMERAL test env D2",
        "category": "simulated",
        "bounds_m": [5, 5, 5],
        "gravity_m_s2": 9.81,
        "tags": ["test", "ephemeral"],
    }
    r = requests.post(f"{BACKEND}/api/environments", json=payload, timeout=15.0)
    assert r.status_code == 200, r.text
    env_id = r.json()["id"]

    r = requests.get(f"{BACKEND}/api/environments/{env_id}", timeout=15.0)
    assert r.status_code == 200
    assert r.json()["name"] == "EPHEMERAL test env D2"

    r = requests.delete(f"{BACKEND}/api/environments/{env_id}", timeout=15.0)
    assert r.status_code == 200
    assert r.json()["deleted"] == 1

    r = requests.get(f"{BACKEND}/api/environments/{env_id}", timeout=15.0)
    assert r.status_code == 404


def test_bind_compatibility_blocks_then_force_succeeds():
    """The compat checker must reject incompatible binds without
    `force=True`, surface every issue, and allow override with force.

    Note: `spec.needs` and `spec.footprint_m` are extension fields the
    architect can attach to any twin via direct Mongo write — they are
    NOT part of the canonical DigitalTwin pydantic model (state-only),
    so we inject them through the database after registration."""
    import os as _os
    from pymongo import MongoClient
    mongo_url = _os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = _os.environ.get("DB_NAME", "test_database")

    twin_payload = {
        "name": "TEST_D2_compat_twin",
        "category": "robot",
        "owner_agent": "ajani",
        "description": "Phase D2 compat test",
        "tags": ["test", "d2"],
    }
    r = requests.post(f"{BACKEND}/api/twins/register", json=twin_payload, timeout=15.0)
    assert r.status_code == 200, r.text
    twin_id = r.json()["id"]

    # Inject extension spec fields directly so the compat checker can read them.
    cli = MongoClient(mongo_url)
    cli[db_name]["digital_twins"].update_one(
        {"id": twin_id},
        {"$set": {
            "spec.needs": {"gravity_m_s2": 9.81, "min_o2_pct": 18.0,
                           "temp_c_range": [15.0, 30.0]},
            "spec.footprint_m": [0.5, 0.4, 0.6],
        }},
    )

    r = requests.get(f"{BACKEND}/api/environments", params={"category": "lunar"}, timeout=15.0)
    assert r.status_code == 200
    lunar_id = r.json()["items"][0]["id"]

    # Bind without force → must fail
    r = requests.post(
        f"{BACKEND}/api/environments/{lunar_id}/bind",
        json={"twin_id": twin_id}, timeout=15.0,
    )
    assert r.status_code == 200
    d = r.json()
    assert d["ok"] is False, f"expected blocked bind, got {d}"
    issues = d["compatibility_issues"]
    assert any("O2" in i for i in issues), f"missing O2 issue, got {issues}"
    assert any("Gravity" in i for i in issues), f"missing Gravity issue, got {issues}"
    assert any("Temperature" in i for i in issues), f"missing Temperature issue, got {issues}"

    # Bind with force → must succeed
    r = requests.post(
        f"{BACKEND}/api/environments/{lunar_id}/bind",
        json={"twin_id": twin_id, "force": True}, timeout=15.0,
    )
    assert r.status_code == 200
    d = r.json()
    assert d["ok"] is True
    assert len(d["compatibility_issues"]) >= 3

    # Twin should carry bound_environment_id
    r = requests.get(f"{BACKEND}/api/twins/{twin_id}", timeout=15.0)
    assert r.status_code == 200
    assert r.json()["bound_environment_id"] == lunar_id

    # Unbind round-trip
    r = requests.post(
        f"{BACKEND}/api/environments/{lunar_id}/unbind",
        json={"twin_id": twin_id}, timeout=15.0,
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r = requests.get(f"{BACKEND}/api/twins/{twin_id}", timeout=15.0)
    val = r.json().get("bound_environment_id")
    assert val is None, f"twin still bound: {val}"

    # Cleanup
    cli[db_name]["digital_twins"].delete_one({"id": twin_id})
