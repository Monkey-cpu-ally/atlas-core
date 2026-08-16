import pytest

from creative_intelligence.craft_rubrics import MEDIUMS, QUALITY_PRINCIPLES, STORY, VISUAL_ART


def test_story_and_visual_rubrics_cover_artistic_quality_not_only_technical_validity():
    story = {dimension.name for dimension in STORY.dimensions}
    art = {dimension.name for dimension in VISUAL_ART.dimensions}
    assert {"character_motivation", "setup_payoff", "emotional_authenticity", "theme", "ending"} <= story
    assert {"composition", "focal_hierarchy", "value_structure", "gesture", "visual_storytelling", "originality"} <= art


def test_medium_specific_rubrics_exist_for_core_handmade_media():
    assert {"oil_painting", "watercolor", "ink"} <= set(MEDIUMS)
    assert "brush_direction" in {d.name for d in MEDIUMS["oil_painting"].dimensions}
    assert "wash_control" in {d.name for d in MEDIUMS["watercolor"].dimensions}
    assert "line_weight" in {d.name for d in MEDIUMS["ink"].dimensions}


def test_rubric_requires_every_dimension_before_judgment():
    with pytest.raises(ValueError):
        STORY.validate_scores({"character_motivation": 99})


def test_scores_are_bounded():
    scores = {dimension.name: 101 for dimension in VISUAL_ART.dimensions}
    normalized = VISUAL_ART.validate_scores(scores)
    assert all(value == 100 for value in normalized.values())


def test_quality_philosophy_rejects_detail_equals_quality_assumption():
    joined = " ".join(QUALITY_PRINCIPLES).lower()
    assert "detail is not quality" in joined
    assert "high resolution is not artistic quality" in joined
    assert "complexity is not quality" in joined
