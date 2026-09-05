"""Contract gates for the feature-gated HUD Intelligence V1 spine."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from models.hud_intelligence_models import HudIntelligenceRequest
from routes.hud_intelligence import router
import routes.hud_intelligence as route_module


def _payload(**overrides):
    data = {
        "request_id": "req-contract-0001", "intent": "chat", "persona": "ajani",
        "message": "Explain structural resonance.", "learning_level": "research",
        "resource_ids": [],
        "client_context": {"surface": "persona_chat", "reduced_motion": True},
    }
    data.update(overrides)
    return data


def test_all_seven_learning_levels_round_trip():
    levels = (
        "foundation", "beginner", "intermediate", "advanced",
        "undergraduate", "graduate", "research",
    )
    for level in levels:
        assert HudIntelligenceRequest(**_payload(learning_level=level)).learning_level == level


def test_invalid_persona_and_level_are_rejected():
    for update in ({"persona": "trinity"}, {"learning_level": "expert"}):
        try:
            HudIntelligenceRequest(**_payload(**update))
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid contract value accepted: {update}")


def test_route_is_default_off(monkeypatch):
    monkeypatch.delenv("ATLAS_HUD_INTELLIGENCE_V1", raising=False)
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).post("/api/v1/hud/intelligence", json=_payload())
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "hud_intelligence_v1_disabled"


def test_enabled_route_returns_versioned_envelope(monkeypatch):
    monkeypatch.setenv("ATLAS_HUD_INTELLIGENCE_V1", "true")

    async def fake_execute(req):
        from models.hud_intelligence_models import HudIntelligenceResponse
        return HudIntelligenceResponse(
            request_id=req.request_id, run_id="run-contract-1", status="complete",
            session_id="session-1", message_id="message-1", persona=req.persona,
            learning_level=req.learning_level,
            answer="Resonance is repeated pushing that lines up with natural motion.",
        )

    monkeypatch.setattr(route_module.service, "execute", fake_execute)
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).post("/api/v1/hud/intelligence", json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "req-contract-0001"
    assert body["learning_level"] == "research"
    assert body["confidence"]["label"] == "unknown"
    assert body["memory"]["turn_saved"] is False


def test_audit_document_excludes_raw_prompt():
    from models.hud_intelligence_models import HudIntelligenceResponse
    from services.hud_intelligence import _public_document
    response = HudIntelligenceResponse(
        request_id="req-secret-0001", run_id="run-secret-1", status="queued",
        persona="minerva", learning_level="advanced",
    )
    document = _public_document(response)
    assert "message" not in document
    assert "prompt" not in document

