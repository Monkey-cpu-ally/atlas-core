"""AI services backend tests — TTS / Minerva / Hermes / Blueprint."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://youthful-archimedes-7.preview.emergentagent.com").rstrip("/")
LLM_TIMEOUT = 120


@pytest.fixture(scope="module")
def client():
    return requests.Session()


# ---------- Voices ----------
def test_voices_mapping(client):
    r = client.get(f"{BASE_URL}/api/ai/voices", timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "voices" in data
    voices = data["voices"]
    assert voices.get("ajani") == "onyx"
    assert voices.get("minerva") == "nova"
    assert voices.get("hermes") == "echo"
    assert voices.get("trinity") == "shimmer"


# ---------- TTS ----------
@pytest.mark.parametrize("persona,expected_voice", [
    ("ajani", "onyx"),
    ("minerva", "nova"),
    ("hermes", "echo"),
    ("trinity", "shimmer"),
])
def test_tts_per_persona(client, persona, expected_voice):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": f"Hello from {persona}.", "persona": persona},
        timeout=30,
    )
    if r.status_code == 503:
        pytest.skip("EMERGENT_LLM_KEY not configured")
    assert r.status_code == 200, r.text
    assert r.headers.get("content-type", "").startswith("audio/")
    assert r.headers.get("X-AI-Voice") == expected_voice
    assert len(r.content) > 10_000, f"audio too small: {len(r.content)} bytes"


def test_tts_explicit_voice_override(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "Override test.", "voice": "shimmer"},
        timeout=30,
    )
    if r.status_code == 503:
        pytest.skip("EMERGENT_LLM_KEY not configured")
    assert r.status_code == 200, r.text
    assert r.headers.get("X-AI-Voice") == "shimmer"
    assert r.headers.get("content-type", "").startswith("audio/")
    assert len(r.content) > 5_000


def test_tts_empty_text_400(client):
    r = client.post(f"{BASE_URL}/api/ai/tts", json={"text": "", "persona": "minerva"}, timeout=10)
    assert r.status_code == 400, r.text


def test_tts_too_long_400(client):
    r = client.post(
        f"{BASE_URL}/api/ai/tts",
        json={"text": "a" * 4097, "persona": "minerva"},
        timeout=10,
    )
    assert r.status_code == 400, r.text


# ---------- Minerva ----------
def test_minerva_approval(client):
    r = client.post(
        f"{BASE_URL}/api/ai/minerva/approve",
        json={"proposal": "Build a community library that lends seeds to local farmers."},
        timeout=LLM_TIMEOUT,
    )
    if r.status_code == 503:
        pytest.skip("EMERGENT_LLM_KEY not configured")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "review" in body and "raw" in body and "timestamp" in body
    rv = body["review"]
    assert rv["verdict"] in ("approve", "approve_with_conditions", "reject"), rv
    for k in ("summary", "ethical_score", "concerns", "conditions", "alternatives", "ancestral_wisdom"):
        assert k in rv, f"missing field {k}"
    assert isinstance(rv["concerns"], list)
    assert isinstance(rv["conditions"], list)
    assert isinstance(rv["alternatives"], list)


# ---------- Hermes ----------
def test_hermes_validation(client):
    r = client.post(
        f"{BASE_URL}/api/ai/hermes/validate",
        json={"proposal": "Use a Raspberry Pi to log temperature from a DS18B20 sensor every 60 seconds."},
        timeout=LLM_TIMEOUT,
    )
    if r.status_code == 503:
        pytest.skip("EMERGENT_LLM_KEY not configured")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "review" in body and "raw" in body and "timestamp" in body
    rv = body["review"]
    assert rv["verdict"] in ("valid", "valid_with_constraints", "invalid"), rv
    for k in ("summary", "feasibility_score", "safety_score",
              "failure_modes", "constraints", "patterns", "next_steps"):
        assert k in rv, f"missing field {k}"
    assert isinstance(rv["failure_modes"], list)
    assert isinstance(rv["next_steps"], list)


# ---------- Blueprint ----------
def test_blueprint_generate(client):
    r = client.post(
        f"{BASE_URL}/api/ai/blueprint/generate",
        json={"concept": "A solar-powered water purifier for off-grid villages."},
        timeout=LLM_TIMEOUT,
    )
    if r.status_code == 503:
        pytest.skip("EMERGENT_LLM_KEY not configured")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "blueprint" in body and "raw" in body and "timestamp" in body
    bp = body["blueprint"]
    assert "concept" in bp
    assert "phases" in bp
    phases = bp["phases"]
    for name in ("philosophy", "research", "blueprint", "simulation", "physical"):
        assert name in phases, f"missing phase {name}"
    # nested keys
    assert "core_belief" in phases["philosophy"]
    assert "known" in phases["research"] and "unknown" in phases["research"]
    assert "components" in phases["blueprint"]
    assert "test_plan" in phases["simulation"]
    assert "build_steps" in phases["physical"] and "safety_gates" in phases["physical"]
    assert isinstance(bp.get("minerva_concerns"), list)
    assert isinstance(bp.get("hermes_validations"), list)
