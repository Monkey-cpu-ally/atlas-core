"""
Persona Chat — Phase 8a EXTRAS (iteration_18 testing).

These tests cover bullets in review_request that aren't yet asserted in
test_persona_chat.py:

  * KB wiring with force_agent='ajani' — cited_knowledge_ids contains the
    ingested record id when Ajani chats about a related topic.
  * Council fan-out writes FOUR Memory Bank rows (3 sub-voices + 1 council).
  * DELETE session removes session+messages but preserves Memory Bank entries.
  * Persona voice character — Ajani's reply reflects engineer vocabulary.
  * Regression: /api/robot/devices and /api/membank/list still respond.
  * Response shape is JSON-serialisable & stable for HUD voice bar.
"""
from __future__ import annotations

import os
import time
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
API = f"{BACKEND.rstrip('/')}/api/persona"
MEMBANK = f"{BACKEND.rstrip('/')}/api/membank"
KBASE = f"{BACKEND.rstrip('/')}/api/kbase"
ROBOT = f"{BACKEND.rstrip('/')}/api/robot"

TIMEOUT = httpx.Timeout(180.0, connect=10.0)


# --- KB wiring: ingest → chat → cited_knowledge_ids -----------------------
_INGEST_URLS_AJANI = [
    # Order from most-likely-allowed-by-egress to fallback.
    "https://github.com/openai/openai-python",
    "https://raw.githubusercontent.com/openai/openai-python/main/README.md",
    "https://arxiv.org/abs/1706.03762",
]


def _find_or_ingest_record(agent: str, urls):
    """Return a kbase record tagged with `agent`.

    Strategy: search existing → if missing, ingest each candidate URL with
    force_agent=<agent> until one succeeds. Skip the test if none work
    (egress blocked from this preview env).
    """
    r = httpx.get(f"{KBASE}/search", params={"q": "", "agent": agent, "limit": 5}, timeout=TIMEOUT)
    if r.status_code == 200:
        items = (r.json() or {}).get("items") or []
        if items:
            return items[0]
    for url in urls:
        payload = {"url": url, "force_agent": agent, "extra_tags": ["TEST_persona_kb_wiring"]}
        ri = httpx.post(f"{KBASE}/ingest", json=payload, timeout=httpx.Timeout(180.0))
        if ri.status_code in (200, 201):
            rec = ri.json()
            return rec.get("record") or rec
    pytest.skip(f"could not ingest any seed URL for agent={agent} (egress blocked)")


def _pick_keyword(rec):
    """Choose a single token that (a) actually appears in title/summary and
    (b) is selective enough to find THIS record via kbase.search regex.

    kbase.search re.escapes the query and matches as a substring against
    title/summary/tags/concepts — so the token must be a literal substring
    of those fields.
    """
    import re as _re
    haystack = " ".join([
        rec.get("title") or "", rec.get("summary") or "",
    ]).lower()
    # Try concepts first (typically multi-word phrases that are in summary too)
    for c in (rec.get("concepts") or []):
        tok = str(c).strip().lower()
        if tok and tok in haystack and 4 <= len(tok) <= 40:
            return tok
    # Then any 5+ char alpha word from the title
    for word in _re.findall(r"[A-Za-z]{5,}", rec.get("title") or ""):
        if word.lower() in haystack:
            return word
    return "whisper"


def test_kb_wiring_cited_in_ajani_chat():
    rec = _find_or_ingest_record("ajani", _INGEST_URLS_AJANI)
    rec_id = rec.get("id")
    assert rec_id, f"no kbase record id available: {rec}"
    keyword = _pick_keyword(rec)
    r = httpx.post(
        f"{API}/ajani/chat",
        json={"message": keyword,
              "memory_top_k": 0, "knowledge_top_k": 5},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["persona"] == "ajani"
    assert isinstance(body.get("cited_knowledge_ids"), list)
    assert rec_id in body["cited_knowledge_ids"], (
        f"expected kbase id {rec_id} in cited_knowledge_ids, got "
        f"{body['cited_knowledge_ids']!r}"
    )


def test_kb_wiring_cited_in_hermes_chat():
    """Verify KB→chat wiring using the persona of an EXISTING record
    (the seeded Whisper record is tagged 'hermes'). This decouples the
    contract test from external egress."""
    r = httpx.get(f"{KBASE}/search", params={"q": "", "agent": "hermes", "limit": 5}, timeout=TIMEOUT)
    items = (r.json() or {}).get("items") or []
    if not items:
        pytest.skip("no kbase record tagged hermes")
    rec = items[0]
    rec_id = rec["id"]
    keyword = _pick_keyword(rec)
    chat = httpx.post(
        f"{API}/hermes/chat",
        json={"message": keyword,
              "memory_top_k": 0, "knowledge_top_k": 5},
        timeout=TIMEOUT,
    )
    assert chat.status_code == 200, chat.text
    body = chat.json()
    assert rec_id in body["cited_knowledge_ids"], (
        f"expected {rec_id} in cited_knowledge_ids, got {body['cited_knowledge_ids']!r}"
    )


# --- Council fan-out writes 4 mb rows -------------------------------------
def test_council_writes_four_memory_rows():
    """council session_id must show up in MemoryBank for ajani, minerva,
    hermes (sub-voices, category=agent) AND council (synthesis, category=council).
    """
    r = httpx.post(
        f"{API}/council/chat",
        json={"message": f"Briefly: choose nylon vs 316L for saltwater housing. (tag {uuid.uuid4().hex[:6]})",
              "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]

    seen = {}
    for persona in ("ajani", "minerva", "hermes", "council"):
        sr = httpx.get(
            f"{MEMBANK}/by-tag",
            params={"tag": sid, "persona": persona, "limit": 5},
            timeout=TIMEOUT,
        )
        assert sr.status_code == 200, sr.text
        items = sr.json().get("items") or []
        seen[persona] = items
        assert items, f"no MemoryBank row for persona={persona} sid={sid}"
    # Sub-voices live in 'agent' (permanent); council in 'council' (permanent).
    for p in ("ajani", "minerva", "hermes"):
        assert seen[p][0]["category"] == "agent", seen[p][0]
        assert seen[p][0]["permanent"] is True
    assert seen["council"][0]["category"] == "council", seen["council"][0]
    assert seen["council"][0]["permanent"] is True
    # Total mb rows for this session_id = 4 (ajani + minerva + hermes + council)
    total = sum(len(seen[p]) for p in seen)
    assert total >= 4, f"expected >=4 mirrored rows, got {total}"


# --- DELETE preserves Memory Bank entries ---------------------------------
def test_delete_session_preserves_memory_bank():
    persona = "ajani"
    r = httpx.post(
        f"{API}/{persona}/chat",
        json={"message": "One-line delete-test message.", "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]

    # Pre-delete: mb row exists for this session
    pre = httpx.get(f"{MEMBANK}/by-tag", params={"tag": sid, "persona": persona, "limit": 5},
                    timeout=TIMEOUT).json()
    assert pre.get("items"), "pre-delete mirror missing"

    # Delete the session
    rd = httpx.delete(f"{API}/sessions/{sid}", timeout=TIMEOUT)
    assert rd.status_code == 200
    # Session & messages gone
    g = httpx.get(f"{API}/sessions/{sid}", timeout=TIMEOUT)
    assert g.status_code == 404

    # Memory Bank row should STILL be there
    post = httpx.get(f"{MEMBANK}/by-tag", params={"tag": sid, "persona": persona, "limit": 5},
                     timeout=TIMEOUT).json()
    assert post.get("items"), \
        f"DELETE should not wipe Memory Bank entries; post-delete items={post}"


# --- Persona voice character ----------------------------------------------
ENGINEER_KEYWORDS = (
    "build", "material", "tolerance", "manufactur", "machine", "fail",
    "mechan", "supply", "weld", "stainless", "fabric", "steel", "stress",
    "load", "design", "componen", "robot", "metal",
)


def test_ajani_voice_sounds_like_engineer():
    """Ajani's voice prompt must steer the model away from the
    science/logic registers. We probe with a question that BOTH a
    scientist and an engineer could answer, and expect engineer-flavoured
    terminology in Ajani's reply."""
    r = httpx.post(
        f"{API}/ajani/chat",
        json={"message": "Pick a material for a robot arm in saltwater. One paragraph.",
              "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    reply = (r.json().get("reply") or "").lower()
    assert reply, "empty Ajani reply"
    hits = [kw for kw in ENGINEER_KEYWORDS if kw in reply]
    assert len(hits) >= 2, f"Ajani reply does not sound like an engineer (hits={hits}): {reply[:300]}"


# --- Response shape stability --------------------------------------------
def test_response_shape_stable_for_hud():
    """The HUD voice bar will consume {session_id, message_id, reply,
    cited_memory_ids, cited_knowledge_ids, provider_used, model_used}.
    All must be top-level keys, JSON-serialisable, and of stable types.
    """
    r = httpx.post(
        f"{API}/hermes/chat",
        json={"message": "one short word", "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200
    body = r.json()
    expected = {
        "session_id": str, "message_id": str, "reply": str,
        "cited_memory_ids": list, "cited_knowledge_ids": list,
    }
    for k, t in expected.items():
        assert k in body, f"missing key {k}"
        assert isinstance(body[k], t), f"{k} should be {t}, got {type(body[k])}"
    # provider_used / model_used may be None on fallback paths, but the
    # KEYS must exist so the HUD never KeyErrors.
    assert "provider_used" in body
    assert "model_used" in body
    assert "council_voices" in body  # empty list for single-persona


# --- Regression: other routers still respond -----------------------------
def test_regression_robot_devices_still_responds():
    r = httpx.get(f"{ROBOT}/devices", timeout=TIMEOUT)
    # Allow 200 OR 401/403 (role-gated); the important thing is the router
    # is mounted and routes haven't been shadowed by /api/persona.
    assert r.status_code in (200, 401, 403), r.text


def test_regression_membank_list_still_responds():
    r = httpx.get(f"{MEMBANK}/list", params={"limit": 5}, timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "items" in body
    assert isinstance(body["items"], list)
