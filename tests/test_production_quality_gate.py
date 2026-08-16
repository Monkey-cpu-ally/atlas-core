from creative_production.art_style import ArtStyleAssessment
from creative_production.quality_gate import ProductionQualityGate
from creative_production.story_quality import StoryQualityReport
from creative_production.visual_quality import VisualQualityAssessment


def story(passing=True):
    value = 96 if passing else 60
    return StoryQualityReport(
        scores={
            "originality": value, "character_depth": value, "dialogue": value,
            "emotional_authenticity": value, "theme": value, "structure": value,
            "pacing": value, "worldbuilding": value, "conflict": value,
            "setup_payoff": value, "tone": value, "humor_restraint": value,
            "audience_maturity": value, "ending_quality": value,
            "internal_logic": value, "character_motivation": value,
        },
        issues=[],
    )


def art(passing=True):
    value = 96 if passing else 70
    return ArtStyleAssessment(
        scores={
            "style_identity": value, "originality": value, "shape_language": value,
            "silhouette_readability": value, "character_consistency": value,
            "palette_coherence": value, "lighting_coherence": value,
            "material_coherence": value, "environment_coherence": value,
            "composition": value, "perspective": value, "detail_control": value,
            "visual_coherence": value,
        },
        violations=[] if passing else ["weak_project_visual_identity"], warnings=[],
    )


def visual(passing=True):
    value = 98 if passing else 70
    dimensions = (
        "anatomy", "face_integrity", "hand_integrity", "identity_consistency", "pose_physics",
        "perspective_geometry", "lighting_consistency", "shadow_consistency", "material_fidelity",
        "edge_integrity", "artifact_free", "background_geometry", "costume_accuracy", "prop_accuracy",
        "composition", "focal_hierarchy", "resolution_fidelity", "texture_fidelity", "style_fidelity",
        "production_polish",
    )
    return VisualQualityAssessment(
        scores={key: value for key in dimensions},
        violations=[] if passing else ["hard_quality_failure:anatomy"], warnings=[],
    )


def test_all_directors_must_approve():
    decision = ProductionQualityGate().evaluate(
        story_assessment=story(), art_style_assessment=art(), visual_assessment=visual(), continuity_ready=True
    )
    assert decision.production_ready
    assert decision.blockers == []


def test_single_failed_director_blocks_entire_production():
    decision = ProductionQualityGate().evaluate(
        story_assessment=story(), art_style_assessment=art(), visual_assessment=visual(False), continuity_ready=True
    )
    assert not decision.production_ready
    assert decision.blockers == ["visual_quality"]


def test_multiple_failures_are_reported_together():
    decision = ProductionQualityGate().evaluate(
        story_assessment=story(False), art_style_assessment=art(False), visual_assessment=visual(), continuity_ready=False
    )
    assert not decision.production_ready
    assert decision.blockers == ["story_quality", "art_style_quality", "continuity"]
