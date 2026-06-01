"""Iteration 7 — Tests for ElevenLabs routing + OpenAI fallback in /api/ai/tts.

The user's ElevenLabs key intentionally LACKS `text_to_speech` and `voices_read`
scopes. Expected behaviour:
  • POST /api/ai/tts  → ElevenLabs 401 missing_permissions → fallback to OpenAI
    → returns audio/mpeg + X-AI-Provider=openai
  • GET  /api/ai/voices → active_provider=='elevenlabs' (key is set), full shape
  • GET  /api/ai/voices/elevenlabs → 502/503 with JSON error body (not HTML)
  • POST /api/ai/tts provider='openai' override → always uses OpenAI
  • POST /api/ai/tts empty text → 400
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"


@pytest.fixture(scope="module")
def client():
    return requests.Session()


# ---------- GET /api/ai/voices shape -----------------------------------------
def test_voices_full_shape(client):
    r = client.get(f"{BASE_URL}/api/ai/voices", timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    for key in ("voices", "elevenlabs_voices", "persona_language",
                "active_provider", "elevenlabs_model"):
        assert key in data, f"/api/ai/voices missing key {key}"
    # ElevenLabs key IS set in .env, so active_provider should be 'elevenlabs'
    assert data["active_provider"] == "elevenlabs", data
    # persona_language defaults
    assert data["persona_language"].get("ajani") == "zu"
    assert data["persona_language"].get("minerva") == "yo"
    assert data["persona_language"].get("hermes") == "maa"
    # elevenlabs voice IDs present per persona
    el = data["elevenlabs_voices"]
    for p in ("ajani", "minerva", "hermes", "trinity"):
        assert el.get(p), f"missing elevenlabs voice for {p}"
    assert data["elevenlabs_model"] == "eleven_multilingual_v2"


# ---------- POST /api/ai/tts ElevenLabs → OpenAI fallback --------------------
def test_tts_falls_back_to_openai_when_elevenlabs_lacks_permission(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "hello", "persona": "ajani"},
        timeout=45,
    )
    assert r.status_code == 200, r.text
    assert r.headers.get("content-type", "").startswith("audio/")
    # Critical: ElevenLabs failed → fallback to OpenAI
    assert r.headers.get("X-AI-Provider") == "openai", r.headers
    assert r.headers.get("X-AI-Voice") == "onyx"
    assert r.headers.get("X-AI-Language") == "zu"
    assert len(r.content) > 5_000


# ---------- POST /api/ai/tts provider='openai' explicit override -------------
def test_tts_explicit_openai_provider(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "explicit openai", "persona": "minerva", "provider": "openai"},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    assert r.headers.get("X-AI-Provider") == "openai"
    assert r.headers.get("X-AI-Voice") == "nova"
    assert r.headers.get("content-type", "").startswith("audio/")


# ---------- POST /api/ai/tts empty text → 400 --------------------------------
def test_tts_empty_text_returns_400(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "", "persona": "ajani"},
        timeout=10,
    )
    assert r.status_code == 400, r.text


# ---------- GET /api/ai/voices/elevenlabs — JSON error body ------------------
def test_voices_elevenlabs_returns_json_error_not_html(client):
    """The configured ElevenLabs key lacks voices_read. The endpoint should
    return a JSON error body (not a Python traceback HTML)."""
    r = client.get(f"{BASE_URL}/api/ai/voices/elevenlabs", timeout=30)
    # Accept any 4xx/5xx but must be JSON, not HTML
    assert r.status_code in (200, 401, 403, 502, 503), r.status_code
    ct = r.headers.get("content-type", "")
    assert "json" in ct.lower(), f"Expected JSON error body, got content-type={ct}, body={r.text[:200]}"
    # JSON body must parse
    body = r.json()
    if r.status_code == 200:
        assert "voices" in body
    else:
        # FastAPI HTTPException returns {"detail": ...}
        assert "detail" in body or "error" in body or "message" in body, body


# ---------- Language override propagates to header ---------------------------
def test_tts_language_override_header(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "language override", "persona": "ajani", "language": "en", "provider": "openai"},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    assert r.headers.get("X-AI-Language") == "en"
    assert r.headers.get("X-AI-Provider") == "openai"
