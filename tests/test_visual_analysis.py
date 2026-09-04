import pytest

from creative_intelligence.visual_analysis import VisualAnalysis, analyzer_contract


def source():
    return {
        "source_id": "study:frame-001",
        "medium": "hand-drawn animation",
        "source_kind": "animation frame",
        "rights_basis": "user_provided",
        "transferable_principles": ["Build readable poses before surface detail"],
        "construction_steps": ["Block gesture, then silhouette, then contour"],
        "limitations": ["Do not imitate or copy distinctive creator expression"],
        "provenance": ["user-authorized source"],
    }


def analysis(confidence=0.95):
    return VisualAnalysis.from_mapping({
        "provider": "test-vision-provider",
        "evidence": [{
            "locator": "frame:12 region:subject",
            "dimension": "shape_and_silhouette",
            "observation": "The subject remains readable as a single dark mass",
            "confidence": confidence,
        }],
    })


def test_analysis_turns_traceable_visual_evidence_into_validated_study():
    study = analysis().to_art_study(source())
    assert study.observations == ("The subject remains readable as a single dark mass",)
    assert study.dimensions == ("shape_and_silhouette",)
    assert "visual-analysis-provider:test-vision-provider" in study.provenance


def test_analysis_rejects_evidence_without_locator_or_known_dimension():
    payload = {
        "provider": "test-provider",
        "evidence": [{"locator": "", "dimension": "composition", "observation": "x", "confidence": .9}],
    }
    with pytest.raises(ValueError, match="locator"):
        VisualAnalysis.from_mapping(payload)
    payload["evidence"][0]["locator"] = "frame:1"
    payload["evidence"][0]["dimension"] = "magic_style"
    with pytest.raises(ValueError, match="known Art Study dimension"):
        VisualAnalysis.from_mapping(payload)


def test_analysis_rejects_invalid_or_low_confidence_evidence():
    payload = {
        "provider": "test-provider",
        "evidence": [{"locator": "frame:1", "dimension": "composition", "observation": "x", "confidence": 1.2}],
    }
    with pytest.raises(ValueError, match="between 0 and 1"):
        VisualAnalysis.from_mapping(payload)
    with pytest.raises(ValueError, match="confidence threshold"):
        analysis(.40).to_art_study(source(), minimum_confidence=.60)


def test_analyzer_contract_does_not_claim_pixel_vision_without_provider():
    contract = analyzer_contract()
    assert contract["pixel_analysis_implemented_here"] is False
    assert contract["external_vision_evidence_required"] is True
    assert contract["evidence_locator_required"] is True
    assert contract["rights_checked_by_art_study"] is True
    assert contract["direct_imitation_forbidden"] is True
