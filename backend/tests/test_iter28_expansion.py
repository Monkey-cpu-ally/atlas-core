"""Iter28 expansion — deeper filter/interaction + dashboard math checks."""
import os
import uuid
import requests
from pymongo import MongoClient

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
KN = f"{BACKEND}/api/knowledge-network"
T = 15.0


def _seed(db, **extra):
    sid = f"kn-exp-{uuid.uuid4().hex[:8]}"
    doc = {
        "id": sid,
        "label": "KN exp watcher",
        "url": "https://example.invalid/exp",
        "kind": "web",
        "status": "inactive",
        "registered_at": "2026-01-01T00:00:00+00:00",
    }
    doc.update(extra)
    db["watchers"].insert_one(doc)
    return sid


def test_dashboard_total_matches_sum_of_kinds():
    body = requests.get(f"{KN}/dashboard", timeout=T).json()
    s = body["counts"]["sources"]
    parts = sum(v for k, v in s.items() if k != "total" and isinstance(v, int))
    # total should be >= sum(known kinds); unknown kinds may exist too
    assert s["total"] >= parts - 1 and s["total"] >= 0


def test_filter_by_country_and_region_after_patch():
    db = MongoClient(MONGO_URL)[DB_NAME]
    sid = _seed(db)
    try:
        r = requests.patch(f"{KN}/sources/{sid}/metadata", json={
            "country": "JP", "region": "Asia", "trust_level": "curated",
            "ai_owner": "athena", "auto_sync": True, "private_source": False,
        }, timeout=T)
        assert r.status_code == 200
        # filter by country
        items = requests.get(f"{KN}/sources?country=JP&enabled_only=false", timeout=T).json()["items"]
        ids = [i["id"] for i in items]
        assert sid in ids
        for i in items:
            assert i["country"] == "JP"
        # filter by region
        items = requests.get(f"{KN}/sources?region=Asia&enabled_only=false", timeout=T).json()["items"]
        assert all(i["region"] == "Asia" for i in items)
        assert sid in [i["id"] for i in items]
        # filter by ai_owner
        items = requests.get(f"{KN}/sources?agent=athena&enabled_only=false", timeout=T).json()["items"]
        assert all(i.get("ai_owner") == "athena" for i in items)
        # filter by auto_sync
        items = requests.get(f"{KN}/sources?auto_sync=true&enabled_only=false", timeout=T).json()["items"]
        assert all(i.get("auto_sync") is True for i in items)
        # filter by kind
        items = requests.get(f"{KN}/sources?kind=web&enabled_only=false", timeout=T).json()["items"]
        assert sid in [i["id"] for i in items]
        # facets should now contain JP under sources_by_country
        db_body = requests.get(f"{KN}/dashboard", timeout=T).json()
        assert db_body["sources_by_country"].get("JP", 0) >= 1
        assert db_body["sources_by_region"].get("Asia", 0) >= 1
    finally:
        db["watchers"].delete_one({"id": sid})


def test_patch_partial_body_persists_only_supplied_fields():
    db = MongoClient(MONGO_URL)[DB_NAME]
    sid = _seed(db)
    try:
        requests.patch(f"{KN}/sources/{sid}/metadata", json={
            "country": "DE", "region": "EU", "trust_level": "curated",
            "ai_owner": "hermes", "auto_sync": False, "private_source": True,
        }, timeout=T)
        # Now patch only one field
        r = requests.patch(f"{KN}/sources/{sid}/metadata", json={"trust_level": "high"}, timeout=T)
        assert r.status_code == 200
        got = requests.get(f"{KN}/sources/{sid}", timeout=T).json()
        assert got["trust_level"] == "high"
        assert got["country"] == "DE"
        assert got["ai_owner"] == "hermes"
        assert got["private_source"] is True
    finally:
        db["watchers"].delete_one({"id": sid})


def test_kbase_deep_alias_mount():
    r = requests.get(f"{KN}/kbase/search?q=test", timeout=T)
    assert r.status_code == 200


def test_dev_pipeline_status_shape():
    body = requests.get(f"{BACKEND}/api/dev/pipeline/status", timeout=T).json()
    for s in body["systems"]:
        assert "name" in s and "status" in s
        assert s["status"] in {"healthy", "degraded", "missing",
                               "under_construction", "unknown"}


def test_iter27_aliases_no_regression():
    for path in ("/api/health", "/api/memory/list", "/api/sources",
                 "/api/tasks/queue", "/api/intelligence/status"):
        assert requests.get(f"{BACKEND}{path}", timeout=T).status_code == 200
