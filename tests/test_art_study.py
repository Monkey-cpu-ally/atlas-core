import pytest

from creative_intelligence.art_study import ART_STUDY_DIMENSIONS, AI_ROLES, ArtStudy, study_contract


def valid_study():
    return {
        "source_id": "study:hand-drawn-001",
        "medium": "hand-drawn animation",
        "observations": ["Line weight changes around the focal subject"],
        "transferable_principles": ["Use line-weight hierarchy to improve readability"],
        "construction_steps": ["Block gesture before committing to final contour"],
        "limitations": ["Do not imitate or copy distinctive creator expression"],
        "provenance": ["user-authorized visual study source"],
        "dimensions": ["construction", "line_and_mark", "composition"],
    }


def test_art_study_accepts_transferable_hand_drawn_craft():
    study = ArtStudy.from_mapping(valid_study())
    assert study.medium == "hand-drawn animation"
    assert "construction" in study.dimensions
    assert study.transferable_principles


def test_art_study_requires_anti_imitation_boundary():
    payload = valid_study(); payload["limitations"] = ["Keep the image readable"]
    with pytest.raises(ValueError, match="anti-imitation"):
        ArtStudy.from_mapping(payload)


def test_art_study_requires_provenance_and_evidence_fields():
    payload = valid_study(); payload["provenance"] = []
    with pytest.raises(ValueError, match="provenance"):
        ArtStudy.from_mapping(payload)
    payload = valid_study(); payload["observations"] = []
    with pytest.raises(ValueError, match="observations"):
        ArtStudy.from_mapping(payload)


def test_art_study_rejects_unknown_dimensions_and_duplicates():
    payload = valid_study(); payload["dimensions"] = ["construction", "magic_style"]
    with pytest.raises(ValueError, match="unknown art study dimensions"):
        ArtStudy.from_mapping(payload)
    payload = valid_study(); payload["dimensions"] = ["construction", "Construction"]
    with pytest.raises(ValueError, match="duplicate"):
        ArtStudy.from_mapping(payload)


def test_art_study_contract_assigns_all_three_ais_and_forbids_imitation():
    contract = study_contract()
    assert set(contract["dimensions"]) == set(ART_STUDY_DIMENSIONS)
    assert set(contract["ai_roles"]) == set(AI_ROLES)
    assert contract["principles_only"] is True
    assert contract["direct_imitation_forbidden"] is True
    assert contract["project_identity_overrides_study_influence"] is True
    assert contract["provenance_required"] is True
    assert contract["evidence_required_before_generation"] is True
