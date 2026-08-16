from creative_intelligence.critic_council import CouncilDecision
from creative_intelligence.master_quality_pipeline import MasterCreativeQualityPipeline
from creative_production.art_style import ArtStyleAssessment
from creative_production.story_quality import StoryQualityReport
from creative_production.visual_quality import VisualQualityAssessment
from creative_production.reference_provenance import OriginalityAssessment


def originality():
    return OriginalityAssessment(influences=[], similarity_scores={"ref": .2}, violations=[])


def council(approved=True, plan=()):
    return CouncilDecision(reviews=(), blockers=() if approved else ("quality",), revision_plan=tuple(plan))


def story(passing=True):
    value = 96 if passing else 60
    keys = ("originality","character_depth","dialogue","emotional_authenticity","theme","structure","pacing","worldbuilding","conflict","setup_payoff","tone","humor_restraint","audience_maturity","ending_quality","internal_logic","character_motivation")
    return StoryQualityReport({k:value for k in keys}, [])


def art(passing=True):
    value = 96 if passing else 70
    keys = ("style_identity","originality","shape_language","silhouette_readability","character_consistency","palette_coherence","lighting_coherence","material_coherence","environment_coherence","composition","perspective","detail_control","visual_coherence")
    return ArtStyleAssessment({k:value for k in keys}, [] if passing else ["weak_project_visual_identity"], [])


def visual(passing=True):
    value = 98 if passing else 70
    keys = ("anatomy","face_integrity","hand_integrity","identity_consistency","pose_physics","perspective_geometry","lighting_consistency","shadow_consistency","material_fidelity","edge_integrity","artifact_free","background_geometry","costume_accuracy","prop_accuracy","composition","focal_hierarchy","resolution_fidelity","texture_fidelity","style_fidelity","production_polish")
    return VisualQualityAssessment({k:value for k in keys}, [] if passing else ["hard_quality_failure:anatomy"], [])


def assessments(*, story_ok=True, art_ok=True, visual_ok=True, continuity=True):
    return lambda artifact: (story(story_ok), art(art_ok), visual(visual_ok), continuity)


def test_master_pipeline_requires_both_creative_and_production_approval():
    result = MasterCreativeQualityPipeline[str]().run(
        artifact="draft",
        reference_queries=("Primal",),
        originality=originality(),
        evaluate=lambda _: council(True),
        revise=lambda text, plan: text,
        production_assessments=assessments(),
    )
    assert result.production_ready
    assert result.blockers == ()


def test_critic_approval_does_not_override_failed_visual_production_gate():
    result = MasterCreativeQualityPipeline[str]().run(
        artifact="draft",
        reference_queries=("Primal",),
        originality=originality(),
        evaluate=lambda _: council(True),
        revise=lambda text, plan: text,
        production_assessments=assessments(visual_ok=False),
    )
    assert not result.production_ready
    assert "production:visual_quality" in result.blockers


def test_failed_creative_quality_never_reaches_production_gate():
    result = MasterCreativeQualityPipeline[str]().run(
        artifact="draft",
        reference_queries=("Primal",),
        originality=originality(),
        evaluate=lambda _: council(False),
        revise=lambda text, plan: text,
        production_assessments=assessments(),
    )
    assert not result.production_ready
    assert result.production is None
    assert "creative_quality_not_approved" in result.blockers


def test_continuity_failure_blocks_master_asset():
    result = MasterCreativeQualityPipeline[str]().run(
        artifact="draft",
        reference_queries=("Primal",),
        originality=originality(),
        evaluate=lambda _: council(True),
        revise=lambda text, plan: text,
        production_assessments=assessments(continuity=False),
    )
    assert not result.production_ready
    assert "production:continuity" in result.blockers
