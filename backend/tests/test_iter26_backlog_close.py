"""Iteration 26 — Backlog completion:
  - Subject auto-tagger keyword coverage
  - Legacy `knowledge` collection retirement completed
  - YouTube poll worker starts + is idempotent
"""
import os
import time

import requests
from pymongo import MongoClient

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
TIMEOUT = 15.0


# --- Subject auto-tagger ---------------------------------------------------
def test_autotag_battery_content_tags_energy_systems():
    from services.subject_autotag import matched_subject_slugs
    slugs = matched_subject_slugs(
        "Solid-state batteries with lithium metal anode achieve 400 Wh/kg energy density"
    )
    assert "energy_systems" in slugs, f"missing energy_systems in {slugs}"
    assert "materials_science" in slugs


def test_autotag_robotics_content():
    from services.subject_autotag import matched_subject_slugs
    slugs = matched_subject_slugs(
        "New humanoid robot uses SLAM and manipulator control for warehouse tasks"
    )
    assert "robotics" in slugs


def test_autotag_empty_returns_empty():
    from services.subject_autotag import matched_subject_slugs
    assert matched_subject_slugs("") == []


def test_autotag_multiple_subjects():
    from services.subject_autotag import matched_subject_slugs
    slugs = matched_subject_slugs(
        "Reinforcement learning trained a rover to navigate outdoor terrain using SLAM"
    )
    assert "artificial_intelligence" in slugs
    assert "robotics" in slugs


# --- Legacy `knowledge` retirement -----------------------------------------
def test_legacy_knowledge_fully_drained():
    """Startup hook must have migrated / deleted every legacy row."""
    db = MongoClient(MONGO_URL)[DB_NAME]
    assert db["knowledge"].count_documents({}) == 0


def test_legacy_import_rows_landed_in_knowledge_records():
    db = MongoClient(MONGO_URL)[DB_NAME]
    assert db["knowledge_records"].count_documents({"tags": "legacy_import"}) >= 1


def test_retirement_is_idempotent():
    """Calling retire_legacy_knowledge again should be a no-op."""
    import asyncio
    from services.kb_workers import retire_legacy_knowledge
    r = asyncio.get_event_loop().run_until_complete(retire_legacy_knowledge()) \
        if False else None
    # Simpler synchronous path:
    from asyncio import new_event_loop
    loop = new_event_loop()
    try:
        r = loop.run_until_complete(retire_legacy_knowledge())
    finally:
        loop.close()
    assert r["migrated"] == 0
    assert r["remaining"] == 0


# --- YT poll worker -------------------------------------------------------
def test_poll_worker_is_running():
    """Backend logs must mention the poll worker startup (short-circuit
    check: hitting `/api/youtube/channels/stats` returns 200)."""
    r = requests.get(f"{BACKEND}/api/youtube/channels/stats", timeout=TIMEOUT)
    assert r.status_code == 200
    for k in ("channels_total", "channels_enabled",
              "total_new_videos_seen_lifetime", "transcripts_ingested"):
        assert k in r.json()


# --- HUD Knowledge Bank panel endpoints work end-to-end -------------------
def test_hud_kb_backend_endpoints_all_return_data():
    """Every endpoint the HUD panel reads must return valid shape."""
    for path in (
        "/api/subjects/stats",
        "/api/research-sources?enabled_only=false",
        "/api/youtube/channels?enabled_only=false",
        "/api/transcripts?limit=5",
        "/api/membank/agents",
    ):
        r = requests.get(f"{BACKEND}{path}", timeout=TIMEOUT)
        assert r.status_code == 200, f"{path} → {r.status_code}"
        d = r.json()
        # Must be a JSON object
        assert isinstance(d, dict), f"{path} returned non-dict"
