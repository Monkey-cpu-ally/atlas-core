"""Iteration 28 — Knowledge Network unified layer + Engineering Console.

Covers:
  * /api/knowledge-network/*  (dashboard, sources+metadata, wrapping surface)
  * /api/dev/pipeline/status  (Engineering Console live probes)

Nothing here should mutate persistent state beyond a single test-created
source doc, which is patched + left in place (the row is inert).
"""
from __future__ import annotations

import os
import uuid

import requests
from pymongo import MongoClient

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
TIMEOUT = 15.0

KN = f"{BACKEND}/api/knowledge-network"


# ---------------------------------------------------------------------------
# /api/knowledge-network/health + /dashboard
# ---------------------------------------------------------------------------
def test_kn_health_lists_wrapped_subsystems():
    r = requests.get(f"{KN}/health", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    wraps = set(body.get("wraps") or [])
    for prefix in (
        "/api/research-sources",
        "/api/kbase",
        "/api/youtube",
        "/api/subjects",
        "/api/membank/research",
    ):
        assert prefix in wraps, f"KN layer should wrap {prefix}"


def test_kn_dashboard_returns_aggregate_counts():
    r = requests.get(f"{KN}/dashboard", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    counts = body.get("counts") or {}
    for key in ("sources", "subjects", "youtube_channels",
                "knowledge_records", "research_memories", "transcripts"):
        assert key in counts, f"dashboard missing {key}"
    # Sources bucket must itself have a shape.
    src = counts.get("sources") or {}
    for kind in ("rss", "patent", "web", "git", "youtube_channel", "total"):
        assert kind in src, f"source counts missing {kind}"
    # Metadata facets must be present (may be empty dicts).
    for facet in ("sources_by_country", "sources_by_region",
                  "sources_by_trust", "sources_by_ai_owner"):
        assert facet in body


# ---------------------------------------------------------------------------
# /api/knowledge-network/sources — proxy + metadata shape.
# ---------------------------------------------------------------------------
def test_kn_sources_expose_full_metadata_block():
    r = requests.get(f"{KN}/sources?enabled_only=false", timeout=TIMEOUT)
    assert r.status_code == 200
    items = r.json().get("items") or []
    if not items:
        # No sources yet — skip the schema check; still passes.
        return
    row = items[0]
    required = {
        "source_name", "source_type", "country", "region", "source_language",
        "trust_level", "ai_owner", "update_frequency", "access_method",
        "auto_sync", "private_source", "culture_tag", "enabled", "last_sync",
        "tags",
    }
    missing = required - set(row.keys())
    assert not missing, f"source row missing fields: {missing}"


def test_kn_sources_filter_by_trust_level():
    r = requests.get(f"{KN}/sources?trust_level=curated&enabled_only=false", timeout=TIMEOUT)
    assert r.status_code == 200
    for item in (r.json().get("items") or []):
        assert item.get("trust_level") == "curated"


def test_kn_sources_stats_matches_underlying():
    r_kn = requests.get(f"{KN}/sources/stats", timeout=TIMEOUT)
    r_src = requests.get(f"{BACKEND}/api/research-sources/stats", timeout=TIMEOUT)
    assert r_kn.status_code == 200 and r_src.status_code == 200
    assert r_kn.json() == r_src.json()


# ---------------------------------------------------------------------------
# /api/knowledge-network/sources/{id}/metadata PATCH
# ---------------------------------------------------------------------------
def _seed_watcher(db) -> str:
    """Insert a disposable watcher row we can safely patch."""
    sid = f"kn-test-{uuid.uuid4().hex[:10]}"
    db["watchers"].insert_one({
        "id": sid,
        "label": "KN pytest watcher",
        "url": "https://example.invalid/kn-test",
        "kind": "web",
        "status": "inactive",
        "registered_at": "2026-01-01T00:00:00+00:00",
    })
    return sid


def test_kn_patch_metadata_persists_new_fields():
    db = MongoClient(MONGO_URL)[DB_NAME]
    sid = _seed_watcher(db)
    try:
        payload = {
            "country": "US",
            "region": "North America",
            "source_language": "en",
            "trust_level": "high",
            "ai_owner": "hermes",
            "update_frequency": "daily",
            "access_method": "public",
            "auto_sync": True,
            "private_source": False,
            "culture_tag": "western_scientific",
        }
        r = requests.patch(f"{KN}/sources/{sid}/metadata", json=payload, timeout=TIMEOUT)
        assert r.status_code == 200, r.text
        updated = r.json()
        for key, val in payload.items():
            assert updated.get(key) == val, f"{key} did not persist: got {updated.get(key)!r}"
        # Follow-up GET should see the same values.
        r2 = requests.get(f"{KN}/sources/{sid}", timeout=TIMEOUT)
        assert r2.status_code == 200
        for key, val in payload.items():
            assert r2.json().get(key) == val
    finally:
        db["watchers"].delete_one({"id": sid})


def test_kn_patch_metadata_rejects_unknown_id():
    r = requests.patch(
        f"{KN}/sources/does-not-exist-{uuid.uuid4().hex}/metadata",
        json={"country": "US"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 404


def test_kn_patch_metadata_rejects_empty_body():
    r = requests.patch(f"{KN}/sources/anything/metadata", json={}, timeout=TIMEOUT)
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /api/knowledge-network/{subjects,youtube,kbase,research-memory,...}
# convenience + deep-alias surface.
# ---------------------------------------------------------------------------
def test_kn_convenience_proxies_respond_200():
    for path in (
        f"{KN}/subjects",
        f"{KN}/youtube/dashboard",
        f"{KN}/kbase/search?q=test",
        f"{KN}/research-sources",       # deep-alias mount
        f"{KN}/subjects-registry",      # deep-alias mount for subjects_router
        f"{KN}/youtube/channels",       # deep-alias mount for youtube_router
    ):
        r = requests.get(path, timeout=TIMEOUT)
        assert r.status_code == 200, f"{path} -> {r.status_code}"


def test_kn_research_memory_alias_stores():
    payload = {
        "content": "KN pytest research memory entry",
        "persona": "hermes",
        "tags": ["kn-test"],
    }
    r = requests.post(f"{KN}/research-memory", json=payload, timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert body.get("category") == "research"


# ---------------------------------------------------------------------------
# Engineering Console — /api/dev/pipeline/status
# ---------------------------------------------------------------------------
def test_dev_pipeline_status_reports_real_health():
    r = requests.get(f"{BACKEND}/api/dev/pipeline/status", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body.get("system") == "ATLAS Engineering Console"
    assert body.get("overall_status") in {
        "healthy", "degraded", "missing", "under_construction", "unknown"
    }
    systems = body.get("systems") or []
    names = {s.get("name") for s in systems}
    for expected in (
        "MongoDB", "Memory Bank", "Knowledge Network", "Research Queue",
        "AI Routing", "Teaching Engine", "Research Engine", "GitHub",
        "Test Suite",
    ):
        assert expected in names, f"engineering console missing {expected}"
    # None of the statuses should be the packet's placeholder string.
    for s in systems:
        assert s.get("status") != "needs_runtime_check"


def test_dev_pipeline_ping_ok():
    r = requests.get(f"{BACKEND}/api/dev/pipeline/ping", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json() == {"pong": "ok"}


# ---------------------------------------------------------------------------
# Backward-compat guarantee — nothing was renamed or deleted.
# ---------------------------------------------------------------------------
def test_all_wrapped_originals_still_respond():
    for path in (
        "/api/research-sources",
        "/api/kbase/search?q=test",
        "/api/youtube/dashboard",
        "/api/subjects",
        "/api/membank/list",
    ):
        r = requests.get(f"{BACKEND}{path}", timeout=TIMEOUT)
        assert r.status_code == 200, f"original {path} broke: {r.status_code}"


# ---------------------------------------------------------------------------
# KN v1 spec — /stats, /by-agent, /by-country + source_language + culture_tag
# ---------------------------------------------------------------------------
def test_kn_stats_root_returns_facet_breakdown():
    r = requests.get(f"{KN}/stats", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    for key in (
        "by_kind", "by_country", "by_region", "by_language",
        "by_trust", "by_ai_owner", "by_culture",
        "auto_sync_enabled", "private_sources", "total_sources",
    ):
        assert key in body, f"KN /stats missing facet: {key}"
    # by_kind must expose the same 5-kind + total shape as source_stats.
    for kind in ("rss", "patent", "web", "git", "youtube_channel", "total"):
        assert kind in body["by_kind"]


def test_kn_by_agent_returns_matching_sources():
    # Every source should have an ai_owner (defaults to persona), so at
    # least one agent bucket must be non-empty.
    r_all = requests.get(f"{KN}/sources?enabled_only=false", timeout=TIMEOUT)
    all_items = r_all.json().get("items") or []
    if not all_items:
        return  # No sources yet — skip
    owner = next((i.get("ai_owner") for i in all_items if i.get("ai_owner")), None)
    if not owner:
        return
    r = requests.get(f"{KN}/by-agent/{owner}", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body.get("agent") == owner
    assert body.get("count") >= 1
    for row in body.get("items", []):
        assert (row.get("agent") == owner) or (row.get("ai_owner") == owner)


def test_kn_by_country_filters_correctly():
    # Seed a source with a distinctive country and then look it up.
    db = MongoClient(MONGO_URL)[DB_NAME]
    sid = _seed_watcher(db)
    try:
        marker = f"KN-{uuid.uuid4().hex[:6]}"
        requests.patch(
            f"{KN}/sources/{sid}/metadata",
            json={"country": marker},
            timeout=TIMEOUT,
        )
        r = requests.get(f"{KN}/by-country/{marker}", timeout=TIMEOUT)
        assert r.status_code == 200
        body = r.json()
        assert body.get("country") == marker
        assert body.get("count") == 1
        assert body["items"][0].get("id") == sid
    finally:
        db["watchers"].delete_one({"id": sid})


def test_kn_source_language_field_defaults_to_en():
    r = requests.get(f"{KN}/sources?enabled_only=false", timeout=TIMEOUT)
    items = r.json().get("items") or []
    if not items:
        return
    # Every row must carry the field (default 'en').
    for row in items:
        assert "source_language" in row
        assert row["source_language"] is not None


def test_kn_culture_tag_patch_persists():
    db = MongoClient(MONGO_URL)[DB_NAME]
    sid = _seed_watcher(db)
    try:
        r = requests.patch(
            f"{KN}/sources/{sid}/metadata",
            json={"culture_tag": "west_african_scholarly", "source_language": "yo"},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200
        body = r.json()
        assert body.get("culture_tag") == "west_african_scholarly"
        assert body.get("source_language") == "yo"
    finally:
        db["watchers"].delete_one({"id": sid})


def test_kn_dashboard_now_includes_language_and_culture_facets():
    r = requests.get(f"{KN}/dashboard", timeout=TIMEOUT)
    body = r.json()
    for facet in ("sources_by_language", "sources_by_culture"):
        assert facet in body, f"dashboard missing {facet}"
