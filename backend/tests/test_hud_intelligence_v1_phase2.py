"""Focused tests for HUD Intelligence V1 Phase 2 learning/resource migration."""
from models.hud_intelligence_models import HudIntelligenceRequest
from services.hud_intelligence import _message_for_intent, _resource_evidence, _resource_rows


def _request(intent: str, **overrides) -> HudIntelligenceRequest:
    data = {
        "request_id": "req-phase2-0001",
        "intent": intent,
        "persona": "minerva",
        "message": "Help me understand this.",
        "learning_level": "foundation",
        "resource_ids": [],
        "client_context": {"surface": "teaching", "reduced_motion": False},
    }
    data.update(overrides)
    return HudIntelligenceRequest(**data)


def test_verified_catalog_resource_maps_to_verified_evidence():
    rows, missing = _resource_rows(["nasa-aero-educator-guide"])
    assert missing == []
    assert len(rows) == 1
    evidence = _resource_evidence(rows)
    assert evidence[0].record_id == "nasa-aero-educator-guide"
    assert evidence[0].verification_status == "verified"
    assert evidence[0].kind == "resource"


def test_missing_resource_is_reported_without_fabrication():
    rows, missing = _resource_rows(["not-a-real-atlas-resource"])
    assert rows == []
    assert missing == ["not-a-real-atlas-resource"]


def test_teach_intent_includes_learning_contract_and_original_request():
    req = _request("teach", message="Teach me structural resonance.", learning_level="beginner")
    prompt = _message_for_intent(req, [])
    assert "Teach me structural resonance." in prompt
    assert "beginner" in prompt.lower()
    assert "Do not claim evidence that was not retrieved." in prompt


def test_resource_explanation_is_explicit_about_catalog_only_metadata():
    rows, missing = _resource_rows(["nasa-uas-educator-guide"])
    assert missing == []
    req = _request(
        "explain_resource",
        message="Explain why this is useful for robotics.",
        resource_ids=["nasa-uas-educator-guide"],
        client_context={"surface": "bookshelf", "reduced_motion": False},
    )
    prompt = _message_for_intent(req, rows)
    assert "nasa-uas-educator-guide" in prompt
    assert "Unmanned Aircraft Systems Educator Guide" in prompt
    assert "does NOT prove that full resource text was ingested" in prompt
    assert "Explain why this is useful for robotics." in prompt
