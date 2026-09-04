import pytest

from creative_intelligence.vision_provider import VisionProvider, provider_contract, run_art_study_pipeline


class FakeVisionProvider(VisionProvider):
    @property
    def provider_id(self):
        return "fake-vision-v1"

    def analyze(self, source_reference, request):
        return {
            "provider": self.provider_id,
            "evidence": [{
                "locator": "frame:4 region:character",
                "dimension": "gesture",
                "observation": "The action line is established before contour detail",
                "confidence": 0.96,
            }],
        }


class MismatchedProvider(FakeVisionProvider):
    def analyze(self, source_reference, request):
        payload = super().analyze(source_reference, request)
        payload["provider"] = "different-provider"
        return payload


def metadata():
    return {
        "source_id": "study:authorized-001",
        "medium": "pencil animation study",
        "source_kind": "animation frame",
        "rights_basis": "user_provided",
        "transferable_principles": ["Establish motion before detail"],
        "construction_steps": ["Place the gesture line before contour"],
        "limitations": ["Do not imitate or copy distinctive creator expression"],
        "provenance": ["user-authorized source"],
    }


def test_pipeline_converts_provider_evidence_to_traceable_technique_profile():
    result = run_art_study_pipeline(FakeVisionProvider(), "asset://frame-4", metadata(), {"goal": "study gesture"})
    assert result.analysis.provider == "fake-vision-v1"
    assert result.profile.source_ids == ("study:authorized-001",)
    assert "gesture" in result.profile.dimensions
    assert "visual-analysis-provider:fake-vision-v1" in result.profile.provenance
    assert result.profile.direct_imitation_forbidden is True


def test_pipeline_rejects_provider_identity_mismatch():
    with pytest.raises(ValueError, match="identity mismatch"):
        run_art_study_pipeline(MismatchedProvider(), "asset://frame-4", metadata(), {})


def test_pipeline_cannot_bypass_source_rights():
    unsafe = metadata(); unsafe["rights_basis"] = "scraped_unknown"
    with pytest.raises(ValueError, match="rights_basis"):
        run_art_study_pipeline(FakeVisionProvider(), "asset://frame-4", unsafe, {})


def test_pipeline_requires_real_provider_contract_and_source_reference():
    with pytest.raises(ValueError, match="VisionProvider"):
        run_art_study_pipeline(object(), "asset://frame-4", metadata(), {})
    with pytest.raises(ValueError, match="source_reference"):
        run_art_study_pipeline(FakeVisionProvider(), "", metadata(), {})


def test_provider_contract_preserves_atlas_boundaries():
    contract = provider_contract()
    assert contract["provider_independent"] is True
    assert contract["structured_evidence_only"] is True
    assert contract["provider_identity_verified"] is True
    assert contract["rights_and_provenance_validation_required"] is True
    assert contract["direct_imitation_forbidden"] is True
    assert contract["project_identity_authoritative"] is True
