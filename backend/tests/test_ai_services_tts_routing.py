"""Tests for ElevenLabs/OpenAI routing in /api/ai/tts.

Provider-backed audio generation is a live integration concern. CI deliberately
uses sentinel credentials, so it must not call external providers or interpret
a sentinel key as proof that audio generation is operational. Contract tests
that do not require a provider remain active in CI; live TTS checks run only
when ATLAS_LIVE_TTS_TESTS=1 is explicitly enabled with real credentials.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"

LIVE_TTS = os.environ.get("ATLAS_LIVE_TTS_TESTS", "").strip().lower() in {"1", "true", "yes"}
LIVE_TTS_REASON = "live TTS provider tests require ATLAS_LIVE_TTS_TESTS=1 and real provider credentials"


@pytest.fixture(scope="module")
def client():
    return requests.Session()


def test_voices_full_shape(client):
    r = client.get(f"{BASE_URL}/api/ai/voices", timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    for key in ("voices", "elevenlabs_voices", "persona_language",
                "active_provider", "elevenlabs_model"):
        assert key in data, f"/api/ai/voices missing key {key}"
    assert data["active_provider"] in {"elevenlabs", "openai"}, data
    assert data["persona_language"].get("ajani") == "zu"
    assert data["persona_language"].get("minerva") == "yo"
    assert data["persona_language"].get("hermes") == "maa"
    el = data["elevenlabs_voices"]
    for p in ("ajani", "minerva", "hermes", "trinity"):
        assert el.get(p), f"missing elevenlabs voice for {p}"
    assert data["elevenlabs_model"] == "eleven_multilingual_v2"


@pytest.mark.skipif(not LIVE_TTS, reason=LIVE_TTS_REASON)
def test_tts_falls_back_to_openai_when_elevenlabs_lacks_permission(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "hello", "persona": "ajani"},
        timeout=45,
    )
    assert r.status_code == 200, r.text
    assert r.headers.get("content-type", "").startswith("audio/")
    assert r.headers.get("X-AI-Provider") == "openai", r.headers
    assert r.headers.get("X-AI-Voice") == "onyx"
    assert r.headers.get("X-AI-Language") == "zu"
    assert len(r.content) > 5_000


@pytest.mark.skipif(not LIVE_TTS, reason=LIVE_TTS_REASON)
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


def test_tts_empty_text_returns_400(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "", "persona": "ajani"},
        timeout=10,
    )
    assert r.status_code == 400, r.text


@pytest.mark.skipif(not LIVE_TTS, reason=LIVE_TTS_REASON)
def test_voices_elevenlabs_returns_json_error_not_html(client):
    r = client.get(f"{BASE_URL}/api/ai/voices/elevenlabs", timeout=30)
    assert r.status_code in (200, 401, 403, 502, 503), r.status_code
    ct = r.headers.get("content-type", "")
    assert "json" in ct.lower(), f"Expected JSON error body, got content-type={ct}, body={r.text[:200]}"
    body = r.json()
    if r.status_code == 200:
        assert "voices" in body
    else:
        assert "detail" in body or "error" in body or "message" in body, body


@pytest.mark.skipif(not LIVE_TTS, reason=LIVE_TTS_REASON)
def test_tts_language_override_header(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "language override", "persona": "ajani", "language": "en", "provider": "openai"},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    assert r.headers.get("X-AI-Language") == "en"
    assert r.headers.get("X-AI-Provider") == "openai"
