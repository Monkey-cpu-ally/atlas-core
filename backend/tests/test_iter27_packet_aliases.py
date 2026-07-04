"""Iteration 27 — Packet-aligned API aliases.

Verifies that EMERGENT_MASTER_PROMPT.md endpoints are exposed by the
alias layer added in `routes/packet_aliases.py`, while all existing
routes the HUD is wired to remain live.
"""
import os

import requests

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
TIMEOUT = 15.0


# ---------------------------------------------------------------------------
# /api/health  — brand-new liveness endpoint required by the packet.
# ---------------------------------------------------------------------------
def test_health_root_returns_ok_with_systems_list():
    r = requests.get(f"{BACKEND}/api/health", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert body.get("service") == "atlas-backend"
    assert isinstance(body.get("systems"), list)
    assert "memory-bank" in body["systems"]
    assert "teaching-engine" in body["systems"]


def test_health_ping_returns_pong():
    r = requests.get(f"{BACKEND}/api/health/ping", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json() == {"pong": "ok"}


# ---------------------------------------------------------------------------
# /api/intelligence — aggregate LLM + persona introspection.
# ---------------------------------------------------------------------------
def test_intelligence_status_reports_personas_and_routes():
    r = requests.get(f"{BACKEND}/api/intelligence/status", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert isinstance(body.get("personas"), list)
    routes = body.get("routes") or {}
    for expected in ("memory", "knowledge", "sources", "tasks", "teaching",
                     "research", "intelligence", "health"):
        assert expected in routes, f"missing route mapping: {expected}"


def test_intelligence_personas_endpoint():
    r = requests.get(f"{BACKEND}/api/intelligence/personas", timeout=TIMEOUT)
    assert r.status_code == 200
    assert "personas" in r.json()


def test_intelligence_providers_endpoint():
    r = requests.get(f"{BACKEND}/api/intelligence/providers", timeout=TIMEOUT)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# /api/memory  — alias of /api/membank
# ---------------------------------------------------------------------------
def test_memory_alias_list_matches_membank_list():
    r_alias = requests.get(f"{BACKEND}/api/memory/list", timeout=TIMEOUT)
    r_orig = requests.get(f"{BACKEND}/api/membank/list", timeout=TIMEOUT)
    assert r_alias.status_code == 200
    assert r_orig.status_code == 200
    # Both should hit the same handler → identical shape.
    assert list(r_alias.json().keys()) == list(r_orig.json().keys())


def test_memory_alias_categories():
    r = requests.get(f"{BACKEND}/api/memory/categories", timeout=TIMEOUT)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# /api/sources  — alias of /api/research-sources
# ---------------------------------------------------------------------------
def test_sources_alias_root_lists():
    r = requests.get(f"{BACKEND}/api/sources", timeout=TIMEOUT)
    assert r.status_code == 200


def test_sources_alias_stats():
    r = requests.get(f"{BACKEND}/api/sources/stats", timeout=TIMEOUT)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# /api/tasks  — alias of /api/research-orch
# ---------------------------------------------------------------------------
def test_tasks_queue_alias():
    r = requests.get(f"{BACKEND}/api/tasks/queue", timeout=TIMEOUT)
    assert r.status_code == 200


def test_tasks_queue_status_alias():
    r = requests.get(f"{BACKEND}/api/tasks/queue/status", timeout=TIMEOUT)
    assert r.status_code == 200


def test_tasks_projects_alias():
    r = requests.get(f"{BACKEND}/api/tasks/projects", timeout=TIMEOUT)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# /api/teaching  — alias of /api/atlas/teach (POST). We verify registration
# via the OpenAPI schema and a GET → 405 probe so we avoid firing the actual
# LLM job during the test suite (it would monopolise the executor for the
# remaining tests).
# ---------------------------------------------------------------------------
def test_teaching_alias_registered_in_openapi():
    r = requests.get(f"{BACKEND}/openapi.json", timeout=TIMEOUT)
    assert r.status_code == 200
    paths = set(r.json().get("paths", {}).keys())
    assert "/api/teaching" in paths, "packet-aligned /api/teaching alias missing"
    assert "/api/atlas/teach" in paths, "original /api/atlas/teach must remain"


def test_teaching_alias_rejects_get():
    # 405 = route exists but GET not allowed → confirms POST alias mounted.
    r = requests.get(f"{BACKEND}/api/teaching", timeout=TIMEOUT)
    assert r.status_code == 405


# ---------------------------------------------------------------------------
# /api/knowledge  — the pre-existing knowledge router stays operational,
# and Knowledge Bank subjects/transcripts are additionally exposed under
# /api/knowledge/subjects-bank and /api/knowledge/transcripts.
# ---------------------------------------------------------------------------
def test_knowledge_root_subjects_still_live():
    # Pre-existing endpoint used by the HUD — must remain intact.
    r = requests.get(f"{BACKEND}/api/knowledge/subjects", timeout=TIMEOUT)
    assert r.status_code == 200


def test_knowledge_subjects_bank_alias():
    r = requests.get(f"{BACKEND}/api/knowledge/subjects-bank", timeout=TIMEOUT)
    assert r.status_code == 200


def test_knowledge_transcripts_alias():
    r = requests.get(f"{BACKEND}/api/knowledge/transcripts", timeout=TIMEOUT)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Non-destructive guarantee — originals must still respond.
# ---------------------------------------------------------------------------
def test_original_routes_still_operational():
    for path in (
        "/api/membank/list",
        "/api/research-sources",
        "/api/research-orch/queue",
        "/api/subjects",
        "/api/transcripts",
    ):
        r = requests.get(f"{BACKEND}{path}", timeout=TIMEOUT)
        assert r.status_code == 200, f"original route {path} broke: {r.status_code}"
