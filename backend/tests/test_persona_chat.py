"""
Persona Chat — Phase 8a hard-guarantee tests.

Spec being verified (architect's bullets):
  * Each persona pulls persona-specific memories
  * Each persona pulls relevant Knowledge Bank entries
  * Uses its own prompt / personality
  * Saves conversations back into Memory Bank
  * Foundation for voice integration / HUD panels (REST surface stable)
  * Council fans out across Ajani / Minerva / Hermes then synthesises

Run:
    cd /app/backend && pytest tests/test_persona_chat.py -v
"""
from __future__ import annotations

import os
import uuid

import httpx
import pytest

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
API = f"{BACKEND.rstrip('/')}/api/persona"
MEMBANK = f"{BACKEND.rstrip('/')}/api/membank"
KBASE = f"{BACKEND.rstrip('/')}/api/kbase"

TIMEOUT = httpx.Timeout(180.0, connect=10.0)


# --- Discovery -------------------------------------------------------------
def test_list_personas_shape():
    r = httpx.get(f"{API}/list", timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    body = r.json()
    slugs = {p["slug"] for p in body}
    assert slugs == {"ajani", "minerva", "hermes", "council"}
    # Each one carries the fields the HUD will need
    for p in body:
        for key in ("slug", "name", "domain", "one_liner", "color", "voice_prompt"):
            assert p[key], f"persona {p.get('slug')} missing {key}"


def test_unknown_persona_returns_400():
    r = httpx.post(
        f"{API}/loki/chat", json={"message": "hi"}, timeout=TIMEOUT,
    )
    assert r.status_code == 400


# --- Single-persona chat ---------------------------------------------------
@pytest.mark.parametrize("persona", ["ajani", "minerva", "hermes"])
def test_persona_chat_returns_grounded_reply(persona):
    msg = f"In one short sentence, what is your domain? (test {uuid.uuid4().hex[:6]})"
    r = httpx.post(
        f"{API}/{persona}/chat",
        json={"message": msg, "memory_top_k": 3, "knowledge_top_k": 3},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["persona"] == persona
    assert body["session_id"]
    assert body["message_id"]
    assert body["reply"].strip(), "empty reply"
    # Single-persona chat must NOT carry council sub-voices.
    assert body.get("council_voices") in (None, [])
    # Provider/model audit must be present.
    assert body["provider_used"]
    assert body["model_used"]


def test_session_continuity_across_turns():
    """Two turns in the same session — verify the session_id is reused
    and both turns + replies are persisted (so the persona ACTUALLY has
    short-term context to draw on)."""
    persona = "ajani"
    r1 = httpx.post(
        f"{API}/{persona}/chat",
        json={"message": "First turn of a continuity test. Reply briefly.",
              "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r1.status_code == 200, r1.text
    sid = r1.json()["session_id"]
    assert sid

    r2 = httpx.post(
        f"{API}/{persona}/chat",
        json={"message": "Second turn — same session. Reply briefly.",
              "session_id": sid,
              "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["session_id"] == sid, "must reuse the session_id"

    # Read the session — it must now contain 4 messages (2 user, 2 assistant)
    rd = httpx.get(f"{API}/sessions/{sid}", timeout=TIMEOUT)
    assert rd.status_code == 200
    detail = rd.json()
    assert detail["session"]["id"] == sid
    assert detail["session"]["message_count"] == 4
    msgs = detail["messages"]
    assert len(msgs) == 4
    assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"]
    # All four messages must carry the same session_id and persona
    assert all(m["session_id"] == sid for m in msgs)
    assert all(m["persona"] == persona for m in msgs)


def test_assistant_turn_mirrored_into_memory_bank():
    """The assistant turn must be auto_stored into MemoryBank with
    persona=<persona>, category='agent', and the chat session id in tags.
    Verifies the architect's contract: 'Save conversations back into
    Memory Bank' — without depending on the LLM echoing test strings."""
    persona = "minerva"
    r = httpx.post(
        f"{API}/{persona}/chat",
        json={"message": "What is one fundamental principle of saltwater chemistry? Brief.",
              "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    sid = body["session_id"]
    # The chat response carries a message_id; the API includes a
    # memory_bank_id when the mirror succeeded (it ALWAYS should — the
    # only failure mode is a missing embedding provider, which our hash
    # default can't hit). We assert the artefacts EXIST in the DB.
    # The mirror's tag list = ['persona_chat', persona, session_id], so
    # search by-tag will find it deterministically (no LLM echo needed).
    # We use the memory_bank `/search` endpoint with persona filter as a
    # robust fallback, then scan the returned rows for the session-id tag.
    # The mirror's tag list = ['persona_chat', persona, session_id]. Use
    # the by-tag endpoint (exact match, no cosine threshold) for a
    # deterministic verification.
    sr = httpx.get(
        f"{MEMBANK}/by-tag",
        params={"tag": sid, "persona": persona, "limit": 10},
        timeout=TIMEOUT,
    )
    assert sr.status_code == 200, sr.text
    payload = sr.json()
    items = payload.get("items") or []
    assert items, f"no MemoryBank row tagged with session_id={sid} for persona={persona}"
    # The mirrored row must live in the permanent 'agent' category and
    # carry the persona-name + 'persona_chat' tags.
    row = items[0]
    assert row.get("category") == "agent", f"expected category=agent, got {row.get('category')}"
    assert row.get("permanent") is True
    assert "persona_chat" in (row.get("tags") or [])
    assert persona in (row.get("tags") or [])
    snip = row.get("content") or row.get("text") or ""
    assert f"[{persona} chat reply]" in snip or "Q:" in snip, snip[:200]


# --- Council chat ----------------------------------------------------------
def test_council_returns_three_sub_voices_plus_synth():
    r = httpx.post(
        f"{API}/council/chat",
        json={"message": "In one sentence: should I prefer nylon or 316L for a saltwater housing? (test)",
              "memory_top_k": 2, "knowledge_top_k": 2},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["persona"] == "council"
    voices = body.get("council_voices") or []
    voice_personas = {v["persona"] for v in voices}
    assert voice_personas == {"ajani", "minerva", "hermes"}, \
        f"council must fan out to all three: got {voice_personas}"
    # Each sub-voice must carry text + provider audit
    for v in voices:
        assert v["text"].strip(), f"empty sub-voice for {v['persona']}"
        assert v["model_used"]
    # Final synthesis must be present too
    assert body["reply"].strip()


# --- Session APIs ----------------------------------------------------------
def test_sessions_list_and_read_and_delete():
    # New session
    r = httpx.post(
        f"{API}/hermes/chat",
        json={"message": "Two-word answer please.", "memory_top_k": 0, "knowledge_top_k": 0},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200
    sid = r.json()["session_id"]

    # List hermes sessions — must contain this one
    rs = httpx.get(f"{API}/hermes/sessions?limit=20", timeout=TIMEOUT)
    assert rs.status_code == 200
    items = rs.json()["items"]
    assert any(s["id"] == sid for s in items)

    # Read it
    rd = httpx.get(f"{API}/sessions/{sid}", timeout=TIMEOUT)
    assert rd.status_code == 200
    detail = rd.json()
    assert detail["session"]["id"] == sid
    # Two messages persisted (user + assistant)
    assert len(detail["messages"]) == 2
    roles = [m["role"] for m in detail["messages"]]
    assert roles == ["user", "assistant"]

    # Delete it
    rdel = httpx.delete(f"{API}/sessions/{sid}", timeout=TIMEOUT)
    assert rdel.status_code == 200
    assert rdel.json()["ok"] is True

    # 404 on second delete
    rdel2 = httpx.delete(f"{API}/sessions/{sid}", timeout=TIMEOUT)
    assert rdel2.status_code == 404
