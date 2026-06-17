"""
Knowledge Ingestion smoke tests.

GitHub README path is fully exercised (works on cloud IPs). The YouTube
path tolerates a 503 because YouTube blocks most cloud-provider IPs; the
test still verifies that the route returns a clean, actionable error
rather than a 500 stack trace.

Run:
    cd /app/backend && pytest tests/test_knowledge_ingestion.py -v
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

# Public, captioned, stable URLs — never need credentials.
GH_URL = "https://github.com/openai/whisper"
YT_URL = "https://www.youtube.com/watch?v=aircAruvnKk"   # 3blue1brown Neural Nets


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=180.0) as c:
        yield c


def test_classify(client):
    cases = {
        "https://github.com/foo/bar":                "github",
        "https://www.youtube.com/watch?v=abcdefghij1": "youtube",
        "https://arxiv.org/abs/2401.12345":           "academic",
        "https://patents.google.com/patent/EP0":      "patent",
        "https://example.com/whitepaper.pdf":         "pdf",
        "https://example.com/article":                "web",
    }
    for u, expected in cases.items():
        r = client.get(f"{API}/kbase/classify", params={"url": u})
        assert r.status_code == 200, (u, r.text)
        assert r.json()["source_type"] == expected, (u, r.json())


def test_routing_preview(client):
    cases = {
        "Robotic actuator manufacturing strategy":          "ajani",
        "Photosynthesis in plant biology and ecology":      "minerva",
        "Compile-time type validation in software":         "hermes",
    }
    for text, expected in cases.items():
        r = client.get(f"{API}/kbase/agents/route", params={"text": text})
        assert r.json()["suggested_agent"] == expected, (text, r.json())


def test_github_ingest_creates_record(client):
    r = client.post(f"{API}/kbase/ingest", json={"url": GH_URL})
    assert r.status_code == 200, r.text
    d = r.json()
    rec = d["record"]
    # Required structured fields
    for f in ("id", "title", "summary", "key_points", "tags",
              "source_type", "source_url", "source_hash",
              "confidence_score", "related_agents", "created_at",
              "updated_at", "concepts"):
        assert f in rec, f
    assert rec["source_type"] == "github"
    assert rec["source_url"] == GH_URL
    assert rec["source_author"] == "openai"
    assert rec["summary"]
    assert 0.0 <= rec["confidence_score"] <= 1.0
    assert d["memory_bank_id"]
    # Idempotency — second ingest should reuse + reinforce.
    r2 = client.post(
        f"{API}/kbase/ingest",
        json={"url": GH_URL, "project_id": "proj-test", "extra_tags": ["pilot"]},
    )
    d2 = r2.json()
    assert d2["reused"] is True
    assert d2["record"]["reinforce_count"] >= 1
    assert "proj-test" in d2["record"]["related_projects"]
    assert "pilot" in d2["record"]["tags"]


def test_search_by_tag_and_agent(client):
    # The GitHub ingest above should have left at least one record we can find.
    r = client.get(f"{API}/kbase/search?limit=20")
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    # By source type
    r = client.get(f"{API}/kbase/search?source_type=github&limit=20")
    assert all(it["source_type"] == "github" for it in r.json()["items"])
    # By agent
    r = client.get(f"{API}/kbase/search?agent=hermes&limit=20")
    for it in r.json()["items"]:
        assert "hermes" in it["related_agents"]


def test_get_by_url_and_id(client):
    # Find the whisper record
    r = client.get(f"{API}/kbase/by-url", params={"url": GH_URL})
    assert r.status_code == 200
    rec = r.json()
    r2 = client.get(f"{API}/kbase/{rec['id']}")
    assert r2.status_code == 200
    assert r2.json()["id"] == rec["id"]


def test_youtube_ingest_clean_503_on_blocked_ip(client):
    """YouTube blocks most cloud IPs. We just verify the route surfaces
    a clean 503 with an actionable hint — NEVER a 500 stack trace."""
    r = client.post(f"{API}/kbase/ingest", json={"url": YT_URL})
    if r.status_code == 200:
        # Lucky day — the IP isn't blocked. Verify structure.
        rec = r.json()["record"]
        assert rec["source_type"] == "youtube"
        assert rec["source_url"] == YT_URL
        assert rec["summary"]
    else:
        assert r.status_code == 503
        assert "blocking" in r.text.lower() or "blocked" in r.text.lower()


def test_memory_bank_wiring(client):
    """After GitHub ingest we should be able to find the distilled text
    in /api/membank/search (NOT the raw README)."""
    time.sleep(0.5)
    r = httpx.get(
        f"{API}/membank/list?source_type=github&limit=30", timeout=15,
    )
    rows = r.json()["items"]
    assert rows, "expected at least one membank row of source_type=github"
    # Verify the content is the DISTILLED summary (≤ ~3000 chars), not the raw README.
    sample = rows[0]
    assert len(sample["content"]) < 5000, "content looks too large to be a distillation"
    assert "SUMMARY:" in sample["content"]


def test_graph_triples_wiring(client):
    """The whisper ingest should have written concept→tag triples."""
    r = httpx.get(f"{API}/membank/graph/list?relation=relates_to&limit=200", timeout=15)
    assert r.status_code == 200
    triples = r.json()["items"]
    assert triples, "expected concept→tag relates_to triples"


def test_invalid_url_returns_validation_error(client):
    r = client.post(f"{API}/kbase/ingest", json={"url": "not a url"})
    assert r.status_code == 422


def test_unknown_id_returns_404(client):
    r = client.get(f"{API}/kbase/does-not-exist")
    assert r.status_code == 404
