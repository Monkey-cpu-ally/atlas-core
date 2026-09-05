import pytest

from creative_intelligence.art_study import ArtStudy
from creative_intelligence.technique_profile import synthesize_technique_profile


def study(source_id, principle, provenance):
    return ArtStudy.from_mapping({"source_id":source_id,"medium":"hand-drawn animation","source_kind":"animation frame","rights_basis":"user_provided","observations":["The focal pose reads clearly in silhouette"],"transferable_principles":[principle],"construction_steps":["Establish gesture and silhouette before surface detail"],"limitations":["Do not imitate or copy distinctive creator expression"],"provenance":[provenance],"dimensions":["gesture","shape_and_silhouette","composition"]})

def test_profile_combines_validated_studies_and_preserves_provenance():
    profile=synthesize_technique_profile([study("study:a","Prioritize readable silhouettes","user source A"),study("study:b","Use focal contrast deliberately","user source B")])
    assert profile.source_ids==("study:a","study:b")
    assert "Prioritize readable silhouettes" in profile.principles and "Use focal contrast deliberately" in profile.principles
    assert profile.provenance==("user source A","user source B")

def test_profile_is_principles_only_and_project_identity_remains_authoritative():
    profile=synthesize_technique_profile([study("study:a","Prioritize readable silhouettes","user source A")])
    assert profile.principles_only is True and profile.direct_imitation_forbidden is True and profile.project_identity_authoritative is True

def test_profile_deduplicates_shared_craft_without_losing_sources():
    profile=synthesize_technique_profile([study("study:a","Prioritize readable silhouettes","user source A"),study("study:b","Prioritize readable silhouettes","user source B")])
    assert profile.principles==("Prioritize readable silhouettes",) and profile.source_ids==("study:a","study:b") and len(profile.provenance)==2

def test_profile_rejects_duplicate_source_identity_case_insensitively():
    with pytest.raises(ValueError,match="duplicate ArtStudy source_id"):
        synthesize_technique_profile([study("study:A","Readable silhouettes","source A"),study("STUDY:a","Focal contrast","source duplicate")])

def test_profile_rejects_empty_or_unvalidated_inputs():
    with pytest.raises(ValueError,match="at least one"): synthesize_technique_profile([])
    with pytest.raises(ValueError,match="validated ArtStudy"): synthesize_technique_profile([{"source_id":"unsafe"}])
