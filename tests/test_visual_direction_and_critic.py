import pytest
from creative_intelligence.art_study import ArtStudy
from creative_intelligence.craft_rubrics import VISUAL_ART
from creative_intelligence.technique_profile import synthesize_technique_profile
from creative_intelligence.visual_critic import PRODUCTION_GATES,STATIC_GATES,review_visual_production
from creative_intelligence.visual_direction import build_visual_direction,generation_context

def profile():
    return synthesize_technique_profile([ArtStudy.from_mapping({"source_id":"study:visual-1","medium":"hand-drawn animation","source_kind":"animation frame","rights_basis":"user_provided","observations":["Pose reads before internal detail"],"transferable_principles":["Prioritize readable silhouettes"],"construction_steps":["Gesture","Silhouette","Detail"],"limitations":["Do not imitate or copy distinctive creator expression"],"provenance":["user-authorized source"],"dimensions":["gesture","shape_and_silhouette","camera_and_staging"]})])
def spec(work_kind="static"): return build_visual_direction(profile(),project_identity="ATLAS original production",project_constraints=["preserve character model","no generic AI look"],work_kind=work_kind)
def critic_scores(score=95):
    dims={d.name:score for d in VISUAL_ART.dimensions}; return {name:dict(dims) for name in ("ajani","minerva","hermes")}
def production_scores(score=95): return {gate:score for gate in PRODUCTION_GATES}
def static_scores(score=95): return {gate:score for gate in STATIC_GATES}

def test_generation_context_keeps_project_identity_above_studied_craft():
    context=generation_context(spec()); assert context["project_identity"]=="ATLAS original production"; assert context["work_kind"]=="static"; assert context["project_constraints"]==["preserve character model","no generic AI look"]; assert context["transferable_craft_principles"]==["Prioritize readable silhouettes"]; assert context["project_identity_authoritative"] is True; assert context["direct_imitation_forbidden"] is True; assert "style_target" not in context and "creator" not in context

def test_static_visual_gate_does_not_require_animation_quality():
    decision=review_visual_production(spec("static"),critic_scores=critic_scores(),production_scores=static_scores()); assert decision.approved is True; assert "animation_quality" not in decision.production_scores

def test_motion_visual_gate_requires_animation_quality():
    scores=static_scores()
    with pytest.raises(ValueError,match="animation_quality"): review_visual_production(spec("animation"),critic_scores=critic_scores(),production_scores=scores)

def test_visual_gate_approves_only_when_council_and_production_gates_pass():
    assert review_visual_production(spec("animation"),critic_scores=critic_scores(),production_scores=production_scores()).approved is True

def test_visual_gate_blocks_generic_or_inconsistent_output():
    scores=static_scores(); scores["character_consistency"]=70; scores["originality"]=65; decision=review_visual_production(spec(),critic_scores=critic_scores(),production_scores=scores); assert decision.approved is False; assert "visual:character_consistency" in decision.blockers and "visual:originality" in decision.blockers

def test_visual_gate_fails_closed_when_any_required_production_dimension_is_missing():
    scores=static_scores(); scores.pop("camera_language")
    with pytest.raises(ValueError,match="missing visual production gates"): review_visual_production(spec(),critic_scores=critic_scores(),production_scores=scores)

def test_council_failure_also_blocks_visual_production():
    scores=critic_scores(); scores["hermes"]["composition"]=50; decision=review_visual_production(spec(),critic_scores=scores,production_scores=static_scores()); assert decision.approved is False; assert "hermes:composition" in decision.council.blockers

def test_visual_direction_rejects_unknown_work_kind():
    with pytest.raises(ValueError,match="work_kind"): spec("hologram")
