from creative_intelligence.vision_provider import VisionProvider
from backend.services.art_study_runtime import run_art_study


class FakeVisionProvider(VisionProvider):
    @property
    def provider_id(self):
        return "test-vision"

    def analyze(self, source_reference, request):
        assert source_reference == "asset://frame-001"
        return {
            "provider": self.provider_id,
            "evidence": [{
                "locator": "frame:1 subject",
                "dimension": "shape_and_silhouette",
                "observation": "The subject reads clearly before interior detail",
                "confidence": 0.96,
            }],
        }


def test_callable_runtime_preserves_evidence_identity_and_project_authority():
    result = run_art_study(
        provider=FakeVisionProvider(),
        source_reference="asset://frame-001",
        request={"study": ["silhouette"]},
        source={
            "source_id": "study:runtime-001",
            "medium": "hand-drawn animation",
            "source_kind": "animation frame",
            "rights_basis": "user_provided",
            "transferable_principles": ["Solve silhouette before surface detail"],
            "construction_steps": ["Gesture", "Silhouette", "Detail"],
            "limitations": ["Do not imitate or copy distinctive creator expression"],
            "provenance": ["user-authorized source"],
        },
        project_identity="ATLAS original production",
        project_constraints=["preserve character model", "no generic AI look"],
    )
    assert result["technique_profile"]["source_ids"] == ["study:runtime-001"]
    assert set(result["ai_interpretations"]) == {"ajani", "minerva", "hermes"}
    assert result["visual_direction"]["project_identity"] == "ATLAS original production"
    assert result["visual_direction"]["project_constraints"] == ["preserve character model", "no generic AI look"]
    assert result["runtime_contract"]["direct_imitation_forbidden"] is True
    assert result["runtime_contract"]["project_identity_authoritative"] is True
