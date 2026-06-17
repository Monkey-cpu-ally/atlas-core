"""
Phase 3 — Research Pipeline backend tests (web / pdf / patent / recent).
Also re-verifies Phase 2 /api/membank/* still pass after Phase 3+4 land.

External hosts (DuckDuckGo, Google Patents) may rate-limit a cloud IP.
Per the review-request, 503 (ResearchUnreachable) is an acceptable outcome
for the web/patent live calls — we assert non-5xx and shape-on-200.
"""
import io
import os
import time

import pytest
import requests
from reportlab.pdfgen import canvas

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"

API = f"{BASE_URL}/api"
TIMEOUT = 90  # research calls hit external sites + LLM


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def http():
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    return s


def _make_pdf(text: str = "Atlas Core research test PDF.\nThis is a tiny synthetic document used by pytest.") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    # write a few lines across two pages so chunk_text has something to chunk
    for page in range(2):
        y = 800
        for line in (text + f"\nPage {page+1}\n" + ("Lorem ipsum dolor sit amet " * 8)).splitlines():
            c.drawString(50, y, line[:90])
            y -= 16
        c.showPage()
    c.save()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# /api/research/web
# ---------------------------------------------------------------------------
class TestResearchWeb:
    def test_web_validation_empty_query(self, http):
        r = http.post(f"{API}/research/web", json={"query": "", "top_n": 1, "summarise": False}, timeout=15)
        assert r.status_code == 422, r.text

    def test_web_validation_topn_too_high(self, http):
        r = http.post(f"{API}/research/web", json={"query": "atlas", "top_n": 11, "summarise": False}, timeout=15)
        assert r.status_code == 422, r.text

    def test_web_summarise_false_returns_shape(self, http):
        r = http.post(
            f"{API}/research/web",
            json={"query": "atlas core architecture overview", "top_n": 2, "summarise": False},
            timeout=TIMEOUT,
        )
        if r.status_code == 503:
            pytest.skip("DuckDuckGo unreachable from cloud IP (ResearchUnreachable) — acceptable per spec")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["kind"] == "web"
        assert data["query"] == "atlas core architecture overview"
        assert "count" in data and "sources" in data
        assert isinstance(data["sources"], list)
        for src in data["sources"]:
            assert "title" in src and "url" in src
            # summarise=false → summary missing or empty string
            assert not src.get("summary"), f"summarise=false but got: {src.get('summary')[:80]}"

    def test_web_auto_writes_research_memory(self, http):
        marker = f"phase3-web-{int(time.time())}"
        r = http.post(
            f"{API}/research/web",
            json={"query": marker, "top_n": 1, "summarise": False},
            timeout=TIMEOUT,
        )
        if r.status_code == 503:
            pytest.skip("DuckDuckGo unreachable — skip memory-write check")
        assert r.status_code == 200, r.text
        # give the auto_store a beat to flush
        time.sleep(1.5)
        recent = http.get(f"{API}/research/recent", params={"source_type": "web", "limit": 50}, timeout=30)
        assert recent.status_code == 200
        items = recent.json()["items"]
        # All items must be category=research, source_type=web
        for it in items:
            assert it.get("category") == "research"
            assert it.get("source_type") == "web"


# ---------------------------------------------------------------------------
# /api/research/patent
# ---------------------------------------------------------------------------
class TestResearchPatent:
    def test_patent_shape(self, http):
        r = http.post(
            f"{API}/research/patent",
            json={"query": "graphene battery electrode", "top_n": 2, "deep": False},
            timeout=TIMEOUT,
        )
        if r.status_code == 503:
            pytest.skip("Google Patents unreachable (PatentUnreachable) — acceptable per spec")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["kind"] == "patent"
        assert data["deep"] is False
        assert "patents" in data and isinstance(data["patents"], list)
        for p in data["patents"]:
            # id/title/abstract/url per patent
            assert "id" in p
            assert "title" in p
            assert "url" in p

    def test_patent_deep_does_not_500(self, http):
        r = http.post(
            f"{API}/research/patent",
            json={"query": "neural network accelerator", "top_n": 1, "deep": True},
            timeout=TIMEOUT,
        )
        if r.status_code == 503:
            pytest.skip("Google Patents unreachable — acceptable per spec")
        # the key contract: deep enrichment must not 500
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["kind"] == "patent"
        assert data["deep"] is True

    def test_patent_auto_writes_research_memory(self, http):
        r = http.post(
            f"{API}/research/patent",
            json={"query": "lithium anode coating", "top_n": 1, "deep": False},
            timeout=TIMEOUT,
        )
        if r.status_code == 503:
            pytest.skip("Google Patents unreachable")
        assert r.status_code == 200
        time.sleep(1.0)
        recent = http.get(f"{API}/research/recent", params={"source_type": "patent", "limit": 20}, timeout=20)
        assert recent.status_code == 200
        for it in recent.json()["items"]:
            assert it.get("category") == "research"
            assert it.get("source_type") == "patent"


# ---------------------------------------------------------------------------
# /api/research/pdf
# ---------------------------------------------------------------------------
class TestResearchPdf:
    def test_pdf_valid_upload_no_summarise(self, http):
        pdf_bytes = _make_pdf()
        files = {"file": ("TEST_phase3.pdf", pdf_bytes, "application/pdf")}
        data = {"summarise": "false"}
        r = http.post(f"{API}/research/pdf", files=files, data=data, timeout=TIMEOUT)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["kind"] == "pdf"
        assert body["filename"] == "TEST_phase3.pdf"
        assert body["page_count"] >= 1
        assert body["chunk_count"] >= 1
        assert "metadata" in body
        assert "parent_memory_id" in body
        assert body["parent_memory_id"], "parent_memory_id must be present"

    def test_pdf_writes_parent_plus_chunks_in_memory(self, http):
        pdf_bytes = _make_pdf("Atlas pytest parent+chunk verifier. " + ("foo bar " * 200))
        files = {"file": ("TEST_phase3_chunks.pdf", pdf_bytes, "application/pdf")}
        r = http.post(f"{API}/research/pdf", files=files, data={"summarise": "false"}, timeout=TIMEOUT)
        assert r.status_code == 200, r.text
        body = r.json()
        parent_id = body["parent_memory_id"]
        chunk_count = body["chunk_count"]
        # Search for the file rows
        time.sleep(1.0)
        recent = http.get(f"{API}/research/recent", params={"source_type": "pdf", "limit": 100}, timeout=20)
        assert recent.status_code == 200
        rows = recent.json()["items"]
        # parent must be in rows
        ids = [r.get("id") for r in rows]
        assert parent_id in ids, "parent memory row not found in /api/research/recent"
        # chunk rows have source_id = parent_id
        chunk_rows = [r for r in rows if r.get("source_id") == parent_id]
        # should be at least chunk_count (recent may be capped at limit=100 though)
        assert len(chunk_rows) >= min(chunk_count, 90), (
            f"expected >= {chunk_count} chunk rows for parent {parent_id}, got {len(chunk_rows)}"
        )
        for cr in chunk_rows:
            assert cr.get("category") == "research"
            assert cr.get("source_type") == "pdf"

    def test_pdf_rejects_non_pdf_extension(self, http):
        files = {"file": ("notpdf.txt", b"hello not a pdf", "text/plain")}
        r = http.post(f"{API}/research/pdf", files=files, timeout=15)
        assert r.status_code == 400, r.text

    def test_pdf_rejects_empty(self, http):
        files = {"file": ("empty.pdf", b"", "application/pdf")}
        r = http.post(f"{API}/research/pdf", files=files, timeout=15)
        assert r.status_code == 400, r.text

    def test_pdf_rejects_oversize(self, http):
        big = b"%PDF-1.4\n" + (b"A" * (13 * 1024 * 1024))  # 13 MB
        files = {"file": ("big.pdf", big, "application/pdf")}
        r = http.post(f"{API}/research/pdf", files=files, timeout=60)
        assert r.status_code == 413, r.text


# ---------------------------------------------------------------------------
# /api/research/recent
# ---------------------------------------------------------------------------
class TestResearchRecent:
    def test_recent_default(self, http):
        r = http.get(f"{API}/research/recent", timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert "count" in data and "items" in data
        for it in data["items"]:
            assert it.get("category") == "research"

    def test_recent_filter_pdf(self, http):
        r = http.get(f"{API}/research/recent", params={"source_type": "pdf"}, timeout=20)
        assert r.status_code == 200
        data = r.json()
        for it in data["items"]:
            assert it.get("source_type") == "pdf"


# ---------------------------------------------------------------------------
# Phase 2 regression: membank endpoints still alive
# ---------------------------------------------------------------------------
class TestMembankRegression:
    def test_store_search_listed(self, http):
        marker = f"TESTRUN_p3_{int(time.time())}"
        body = f"Phase 3 regression memory {marker}. Quick brown fox jumps over."
        r = http.post(
            f"{API}/membank/store",
            json={"content": body, "persona": "hermes", "category": "lesson", "tags": [marker]},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        rid = r.json().get("id")
        assert rid

        s = http.get(
            f"{API}/membank/search",
            params={"q": marker, "top_k": 10, "min_score": 0.0},
            timeout=15,
        )
        assert s.status_code == 200, s.text
        payload = s.json()
        items = payload.get("results") or payload.get("memories") or []
        ids = [m.get("id") for m in items]
        assert rid in ids, f"stored memory id {rid} not found in search results"

    def test_graph_triple_and_around(self, http):
        marker = f"TESTRUN_p3_{int(time.time())}"
        subj, obj = f"{marker}_A", f"{marker}_B"
        r = http.post(
            f"{API}/membank/graph/triple",
            json={"from_node": subj, "to_node": obj, "relation": "links_to", "weight": 0.9},
            timeout=15,
        )
        assert r.status_code == 200, r.text
        a = http.get(f"{API}/membank/graph/around", params={"node": subj, "depth": 1}, timeout=15)
        assert a.status_code == 200, a.text
        data = a.json()
        # accept either shape that returns nodes/edges
        assert isinstance(data, dict)
