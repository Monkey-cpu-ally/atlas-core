"""
Phase 8 extras — coverage gaps from the review_request not in test_phase8_quad.py.

Covers:
- anomaly-tagged MemoryBank row when sentinel flips a device
- ask-council healthy-state branch (question framing differs from anomaly branch)
- arXiv ingest pulls authors into record.extra.authors (or source_author)
- arXiv unknown-id graceful fallback (no crash)
- by-tag membank endpoint returns the anomaly row
"""
from __future__ import annotations

import os
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
API = BACKEND.rstrip("/") + "/api"
TIMEOUT = httpx.Timeout(120.0, connect=10.0)
OWNER = {"X-Atlas-Role": "owner"}


@pytest.fixture(scope="module")
def healthy_device():
    name = f"HEALTHY-TEST-{uuid.uuid4().hex[:6]}"
    r = httpx.post(
        f"{API}/robot/devices",
        json={"name": name, "kind": "esp32",
              "hardware_profile": {"sensors": ["temperature"], "actuators": []},
              "tags": ["test", "healthy"]},
        headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def anomalous_device():
    """Register a fresh device, push 12 baseline + 1 outlier so envelope is in
    anomaly state for the duration of the test module."""
    name = f"ANOM-EX-{uuid.uuid4().hex[:6]}"
    r = httpx.post(
        f"{API}/robot/devices",
        json={"name": name, "kind": "esp32",
              "hardware_profile": {"sensors": ["temperature"], "actuators": []},
              "tags": ["test", "anomaly"]},
        headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200
    dev = r.json()
    for i in range(12):
        httpx.post(
            f"{API}/robot/devices/{dev['id']}/telemetry",
            json={"payload": {"temperature": 20.0 + (i % 3) * 0.1}, "source": "test"},
            timeout=TIMEOUT,
        ).raise_for_status()
    httpx.post(
        f"{API}/robot/devices/{dev['id']}/telemetry",
        json={"payload": {"temperature": 500.0}, "source": "test"},
        timeout=TIMEOUT,
    ).raise_for_status()
    return dev


# --- Sentinel: MemoryBank gets tagged 'anomaly' on the outlier row ----------
def test_anomaly_row_tagged_in_membank(anomalous_device):
    dev = anomalous_device
    # Confirm device is currently anomalous before checking membank
    env = httpx.get(
        f"{API}/robot/devices/{dev['id']}/envelope", timeout=TIMEOUT
    ).json()
    assert env.get("anomaly"), "fixture should have left the device anomalous"

    # Look for at least one telemetry row tagged 'anomaly'.
    r = httpx.get(
        f"{API}/membank/by-tag",
        params={"tag": "anomaly", "limit": 50},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    rows = body["items"] if isinstance(body, dict) and "items" in body else body
    assert isinstance(rows, list) and rows, "expected anomaly-tagged rows"
    matching = [
        row for row in rows
        if dev["id"] in (row.get("tags") or [])
        or dev["name"] in (row.get("tags") or [])
        or dev["id"] in str(row.get("content", ""))
    ]
    assert matching, (
        "expected at least one anomaly-tagged membank row referencing "
        f"device {dev['id']}; got {len(rows)} 'anomaly' rows total"
    )


# --- ask-council: healthy branch still produces a council reply -------------
def test_ask_council_healthy_branch(healthy_device):
    dev = healthy_device
    # Push one normal sample
    httpx.post(
        f"{API}/robot/devices/{dev['id']}/telemetry",
        json={"payload": {"temperature": 21.0}, "source": "test"},
        timeout=TIMEOUT,
    ).raise_for_status()

    r = httpx.post(
        f"{API}/robot/devices/{dev['id']}/ask-council", timeout=TIMEOUT
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["device_id"] == dev["id"]
    # Healthy framing — anomaly may be absent or empty
    assert body.get("anomaly") in (None, {}, [])
    council = body["council"]
    assert council["persona"] == "council"
    voice_personas = {v["persona"] for v in council.get("council_voices") or []}
    assert voice_personas == {"ajani", "minerva", "hermes"}


# --- arXiv: authors carried through ----------------------------------------
def test_arxiv_authors_extracted_into_source_author():
    """Use a randomised arXiv URL each run so the test exercises the
    fresh-ingest path (the _reinforce path does NOT refresh source_author)."""
    # Pool of well-known arXiv papers — pick one not yet ingested.
    candidates = [
        "https://arxiv.org/abs/1706.03762",  # Attention is All You Need
        "https://arxiv.org/abs/2005.14165",  # GPT-3
        "https://arxiv.org/abs/1810.04805",  # BERT
        "https://arxiv.org/abs/1512.03385",  # ResNet
    ]
    rec = None
    last_resp = None
    for url in candidates:
        r = httpx.post(
            f"{API}/kbase/ingest", json={"url": url}, timeout=TIMEOUT,
        )
        last_resp = r
        if r.status_code == 503:
            continue
        if r.status_code != 200:
            continue
        body = r.json() or {}
        if not body.get("reused"):
            rec = body.get("record") or {}
            break
        # Already ingested previously — keep it as a fallback
        rec = body.get("record") or rec
    if rec is None:
        pytest.skip(f"all arXiv candidates failed; last={last_resp.status_code if last_resp else None}")

    extra = rec.get("extra") or {}
    candidates_for_authors = (
        extra.get("authors")
        or rec.get("source_author")
        or rec.get("authors")
        or []
    )
    if isinstance(candidates_for_authors, str):
        # Comma-joined author line — split into list for the assertion
        authors_list = [a.strip() for a in candidates_for_authors.split(",") if a.strip()]
    else:
        authors_list = candidates_for_authors
    assert authors_list, (
        f"expected non-empty authors; got source_author={rec.get('source_author')!r}, "
        f"extra={extra!r}"
    )
    assert any(isinstance(a, str) and a.strip() for a in authors_list), (
        f"authors should contain a non-empty string, got {authors_list!r}"
    )


# --- arXiv: unknown id falls back gracefully (no crash) ---------------------
def test_arxiv_unknown_id_falls_back_without_crashing():
    r = httpx.post(
        f"{API}/kbase/ingest",
        json={"url": "https://arxiv.org/abs/99999.99999"},
        timeout=TIMEOUT,
    )
    # Accept either: a (possibly thin) academic record OR a clean 503/4xx
    # with a helpful detail. The key requirement is: no 500 crash.
    assert r.status_code != 500, f"server crashed on unknown arXiv id: {r.text}"
    assert r.status_code in (200, 400, 404, 422, 502, 503), (
        f"unexpected status {r.status_code}: {r.text}"
    )
    if r.status_code == 200:
        rec = (r.json() or {}).get("record") or {}
        assert rec.get("source_type") in ("academic", "web", None)
    else:
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        # Detail should be a string when present
        if "detail" in body:
            assert isinstance(body["detail"], str) and body["detail"].strip()
