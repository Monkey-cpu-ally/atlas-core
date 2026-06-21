"""Iteration 24 — Knowledge Bank architecture tests.

Covers Phases A (Subjects), B (YT Channel Watchlists), C (Unified Research
Sources), D (Agent Memory Partitions)."""
import os
import time

import requests

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
TIMEOUT = 20.0


# === A. Subject taxonomy ====================================================
def test_subjects_seeded_22():
    r = requests.get(f"{BACKEND}/api/subjects", timeout=TIMEOUT)
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 22, f"expected 22 subjects, got {d['count']}"
    families = {s["family"] for s in d["items"]}
    assert {"science", "engineering", "humanities", "craft"} <= families
    # Required slugs:
    slugs = {s["slug"] for s in d["items"]}
    must_have = {"physics", "biology", "chemistry", "mathematics",
                 "artificial_intelligence", "robotics",
                 "aerospace_engineering", "mechanical_engineering",
                 "electrical_engineering", "materials_science",
                 "computer_science", "agriculture", "sustainability",
                 "energy_systems", "medicine_health", "psychology_cognition",
                 "creative_writing", "history_philosophy",
                 "business", "architecture", "game_design", "earth_climate"}
    assert must_have == slugs, f"unexpected subject set: missing={must_have-slugs} extra={slugs-must_have}"


def test_subjects_stats_includes_all_22():
    r = requests.get(f"{BACKEND}/api/subjects/stats", timeout=TIMEOUT)
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 22


def test_subject_get_by_slug_and_id():
    r = requests.get(f"{BACKEND}/api/subjects/robotics", timeout=TIMEOUT)
    assert r.status_code == 200
    sid = r.json()["id"]
    r2 = requests.get(f"{BACKEND}/api/subjects/{sid}", timeout=TIMEOUT)
    assert r2.status_code == 200
    assert r2.json()["slug"] == "robotics"


def test_subject_404_for_unknown():
    r = requests.get(f"{BACKEND}/api/subjects/NOT_A_SUBJECT_XYZ", timeout=TIMEOUT)
    assert r.status_code == 404


# === B. YouTube channel watchlist ==========================================
def test_youtube_channel_register_persists():
    """Even if YouTube can't be reached, the channel row must persist."""
    payload = {
        "channel_url": f"https://www.youtube.com/@test-{int(time.time())}",
        "name": "EPHEMERAL test channel",
        "agent": "minerva",
        "tags": ["test", "iter24"],
        "subject_slug": "computer_science",
    }
    r = requests.post(f"{BACKEND}/api/youtube/channels",
                      json=payload, timeout=30.0)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("id")
    cid = body["id"]

    # Should appear in listing
    r2 = requests.get(f"{BACKEND}/api/youtube/channels", timeout=TIMEOUT)
    assert r2.status_code == 200
    found = next((c for c in r2.json()["items"] if c["id"] == cid), None)
    assert found is not None

    # Cleanup
    r3 = requests.delete(f"{BACKEND}/api/youtube/channels/{cid}", timeout=TIMEOUT)
    assert r3.status_code == 200


def test_youtube_channels_stats_shape():
    r = requests.get(f"{BACKEND}/api/youtube/channels/stats", timeout=TIMEOUT)
    assert r.status_code == 200
    d = r.json()
    for k in ("channels_total", "channels_enabled",
              "total_new_videos_seen_lifetime", "transcripts_ingested"):
        assert k in d, f"missing stats field: {k}"


# === C. Unified Research Sources ==========================================
def test_research_sources_stats_aggregates_3_registries():
    r = requests.get(f"{BACKEND}/api/research-sources/stats", timeout=TIMEOUT)
    assert r.status_code == 200
    d = r.json()
    by_kind = d["by_kind"]
    for k in ("rss", "patent", "web", "git", "youtube_channel", "total"):
        assert k in by_kind
    # WorldWatch already seeded 11 RSS + 6 patent on startup
    assert by_kind["rss"] >= 10
    assert by_kind["patent"] >= 6


def test_research_sources_list_filter_by_kind():
    r = requests.get(f"{BACKEND}/api/research-sources",
                     params={"kind": "rss"}, timeout=TIMEOUT)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 10
    assert all(it["kind"] == "rss" for it in items)


def test_research_sources_list_filter_by_agent():
    r = requests.get(f"{BACKEND}/api/research-sources",
                     params={"agent": "minerva"}, timeout=TIMEOUT)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 1
    assert all(it["agent"] == "minerva" for it in items)


# === D. Agent memory partitions ===========================================
def test_membank_agents_summary_shape():
    r = requests.get(f"{BACKEND}/api/membank/agents", timeout=TIMEOUT)
    assert r.status_code == 200
    d = r.json()
    assert d["grand_total"] > 0
    personas = {row["persona"] for row in d["items"]}
    # Must have at least the four canonical personas (council included).
    assert {"ajani", "minerva", "hermes", "council"} <= personas


def test_membank_agent_detail_per_persona():
    for persona in ("ajani", "minerva", "hermes", "council"):
        r = requests.get(f"{BACKEND}/api/membank/agents/{persona}",
                         params={"limit": 5}, timeout=TIMEOUT)
        assert r.status_code == 200, f"{persona}: {r.text}"
        d = r.json()
        assert d["persona"] == persona
        assert isinstance(d["by_category"], dict)
        # At least one of the canonical personas should have non-empty content
        # but we don't assert per-persona because some personas may have
        # zero memories yet.
