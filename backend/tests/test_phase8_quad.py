"""
Phase 8 b/c/d/e — Graph Traversal + Sentinel Anomaly + MQTT + arXiv.

Run:
    cd /app/backend && pytest tests/test_phase8_quad.py -v
"""
from __future__ import annotations

import os
import time
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
API = BACKEND.rstrip("/") + "/api"
TIMEOUT = httpx.Timeout(120.0, connect=10.0)

OWNER = {"X-Atlas-Role": "owner"}


# ===========================================================================
# P2 — Graph traversal (GET /api/membank/graph/expand)
# ===========================================================================
def _seed_graph_for_test() -> str:
    """Drop a small graph of triples around a unique root node so the test
    does not depend on whatever the ambient DB already has."""
    root = f"test-root-{uuid.uuid4().hex[:6]}"
    for to, rel, w in [
        ("test-leaf-a", "relates_to", 5.0),
        ("test-leaf-b", "relates_to", 1.0),  # low-weight: should be filtered
        ("test-leaf-c", "implements", 3.0),
    ]:
        r = httpx.post(
            f"{API}/membank/graph/triple",
            json={"from_node": root, "to_node": to, "relation": rel, "weight": w},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200, r.text
    # Add a hop-2 edge so depth=2 has somewhere to go
    httpx.post(
        f"{API}/membank/graph/triple",
        json={"from_node": "test-leaf-a", "to_node": "test-deep-1",
              "relation": "relates_to", "weight": 4.0},
        timeout=TIMEOUT,
    )
    return root


def test_graph_expand_returns_bfs_shape():
    root = _seed_graph_for_test()
    r = httpx.get(
        f"{API}/membank/graph/expand",
        params={"subject": root, "depth": 1, "min_weight": 0},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["subject"] == root
    assert body["depth"] == 1
    # vis-network-ready shape
    assert isinstance(body["nodes"], list)
    assert isinstance(body["edges"], list)
    assert body["node_count"] == len(body["nodes"])
    assert body["edge_count"] == len(body["edges"])
    # Root + 3 first-hop neighbours
    assert root in body["nodes"]
    assert "test-leaf-a" in body["nodes"]
    assert "test-leaf-b" in body["nodes"]
    assert "test-leaf-c" in body["nodes"]


def test_graph_expand_depth_grows_neighbourhood():
    root = _seed_graph_for_test()
    r1 = httpx.get(f"{API}/membank/graph/expand",
                   params={"subject": root, "depth": 1}, timeout=TIMEOUT).json()
    r2 = httpx.get(f"{API}/membank/graph/expand",
                   params={"subject": root, "depth": 2}, timeout=TIMEOUT).json()
    assert r2["node_count"] >= r1["node_count"]
    # depth=2 must reach test-deep-1 via test-leaf-a
    assert "test-deep-1" in r2["nodes"]


def test_graph_expand_min_weight_filters_low_confidence_edges():
    root = _seed_graph_for_test()
    high = httpx.get(f"{API}/membank/graph/expand",
                     params={"subject": root, "depth": 1, "min_weight": 2.0},
                     timeout=TIMEOUT).json()
    edge_to_nodes = {e["to_node"] for e in high["edges"]}
    # test-leaf-b had weight=1.0 → must NOT appear under min_weight=2.0
    assert "test-leaf-b" not in edge_to_nodes
    # test-leaf-a (w=5) and test-leaf-c (w=3) must appear
    assert "test-leaf-a" in edge_to_nodes
    assert "test-leaf-c" in edge_to_nodes


def test_graph_expand_unknown_node_returns_root_only():
    r = httpx.get(f"{API}/membank/graph/expand",
                  params={"subject": "no-such-node-zzz", "depth": 2},
                  timeout=TIMEOUT).json()
    assert r["nodes"] == ["no-such-node-zzz"]
    assert r["edges"] == []
    assert r["node_count"] == 1
    assert r["edge_count"] == 0


# ===========================================================================
# P3 — Sentinel anomaly detection + ask-council
# ===========================================================================
@pytest.fixture(scope="module")
def fresh_test_device():
    """Register a fresh test device — keeps the seed devices untouched."""
    name = f"ANOMALY-TEST-{uuid.uuid4().hex[:6]}"
    r = httpx.post(
        f"{API}/robot/devices",
        json={"name": name, "kind": "esp32",
              "hardware_profile": {"sensors": ["temperature"], "actuators": []},
              "tags": ["test", "anomaly"]},
        headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200
    return r.json()


def test_envelope_endpoint_404_for_unknown_device():
    r = httpx.get(f"{API}/robot/devices/no-such-id/envelope", timeout=TIMEOUT)
    assert r.status_code == 404


def test_envelope_warms_up_then_flags_outlier(fresh_test_device):
    dev_id = fresh_test_device["id"]
    # 12 normal readings around 20.0 (well above the 10-sample warmup)
    for i in range(12):
        httpx.post(
            f"{API}/robot/devices/{dev_id}/telemetry",
            json={"payload": {"temperature": 20.0 + (i % 3) * 0.1}, "source": "test"},
            timeout=TIMEOUT,
        ).raise_for_status()

    # Envelope should now be populated
    env = httpx.get(f"{API}/robot/devices/{dev_id}/envelope", timeout=TIMEOUT).json()
    assert env["envelopes"]["temperature"]["n"] == 12
    # No anomaly yet (all readings inside the envelope)
    assert env.get("anomaly") in (None, {})

    # Push a wild outlier — must flip the device into anomaly state
    httpx.post(
        f"{API}/robot/devices/{dev_id}/telemetry",
        json={"payload": {"temperature": 500.0}, "source": "test"},
        timeout=TIMEOUT,
    ).raise_for_status()

    env2 = httpx.get(f"{API}/robot/devices/{dev_id}/envelope", timeout=TIMEOUT).json()
    anomaly = env2.get("anomaly")
    assert anomaly, "expected anomaly block after pushing a 500-degree outlier"
    assert "temperature" in anomaly["drifting_keys"]
    z = anomaly["z_scores"]["temperature"]
    assert abs(z) >= 3.0, f"z-score should exceed sigma threshold, got {z}"
    assert anomaly["sigma_threshold"] == 3.0


def test_envelope_reset_is_owner_only(fresh_test_device):
    dev_id = fresh_test_device["id"]
    # Non-owner → 403
    r = httpx.post(
        f"{API}/robot/devices/{dev_id}/envelope/reset",
        headers={"X-Atlas-Role": "guest"}, timeout=TIMEOUT,
    )
    assert r.status_code == 403
    # Owner → 200, envelope wiped
    r = httpx.post(
        f"{API}/robot/devices/{dev_id}/envelope/reset",
        headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    env = httpx.get(f"{API}/robot/devices/{dev_id}/envelope", timeout=TIMEOUT).json()
    assert env.get("anomaly") in (None, {})
    assert env["envelopes"] == {}


def test_ask_council_uses_persona_chat(fresh_test_device):
    """Hit /api/robot/devices/{id}/ask-council → confirm a council
    response with sub-voices comes back."""
    dev_id = fresh_test_device["id"]
    # Push one telemetry so latest_payload is populated
    httpx.post(
        f"{API}/robot/devices/{dev_id}/telemetry",
        json={"payload": {"temperature": 20.5}, "source": "test"},
        timeout=TIMEOUT,
    ).raise_for_status()

    r = httpx.post(f"{API}/robot/devices/{dev_id}/ask-council", timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["device_id"] == dev_id
    assert body["question"]
    council = body["council"]
    assert council["persona"] == "council"
    assert council["reply"].strip()
    # Must have all three sub-voices
    voice_personas = {v["persona"] for v in council.get("council_voices") or []}
    assert voice_personas == {"ajani", "minerva", "hermes"}


# ===========================================================================
# P4 — MQTT bridge status (dormant when broker not configured)
# ===========================================================================
def test_mqtt_status_dormant_when_unconfigured():
    """No MQTT_BROKER_HOST env → adapter dormant, REST surface unchanged."""
    r = httpx.get(f"{API}/robot/mqtt/status", timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "enabled" in body
    assert "broker_host" in body
    assert "topic_prefix" in body
    # In this env we don't configure a broker, so:
    assert body["enabled"] is False
    assert body["broker_host"] is None
    assert body["connected"] is False
    # No prior error on a dormant boot
    assert body["last_error"] in (None, "")


def test_command_pipeline_still_works_with_mqtt_dormant(fresh_test_device):
    """Even with MQTT dormant, owner PING must still EXECUTE via HTTP-poll."""
    dev_id = fresh_test_device["id"]
    r = httpx.post(
        f"{API}/robot/devices/{dev_id}/command",
        json={"kind": "ping", "payload": {}}, headers=OWNER,
        timeout=TIMEOUT,
    )
    assert r.status_code == 200
    cmd = r.json()
    assert cmd["status"] == "executed"
    # mqtt_publish step should NOT appear when dormant (we don't push noise)
    steps = [p["step"] for p in cmd["pipeline_log"]]
    assert "execute" in steps


# ===========================================================================
# P5 — arXiv ingestion via /api/kbase/ingest
# ===========================================================================
def test_arxiv_extract_id_via_full_url():
    """arXiv URL ingest must produce an ACADEMIC KnowledgeRecord with
    proper title + authors + summary pulled from the Atom feed."""
    # Reuse the seminal Whisper paper — small, stable, no auth.
    r = httpx.post(
        f"{API}/kbase/ingest",
        json={"url": "https://arxiv.org/abs/2212.04356"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    rec = body.get("record") or {}
    assert rec.get("source_type") == "academic"
    assert "arxiv.org/abs/2212.04356" in (rec.get("source_url") or "")
    title = (rec.get("title") or "").lower()
    # The Whisper paper title contains 'speech recognition'
    assert "speech" in title or "whisper" in title, f"title looks wrong: {rec.get('title')!r}"
    summary = (rec.get("summary") or "").strip()
    assert len(summary) > 80, "expected a non-trivial distilled summary"
