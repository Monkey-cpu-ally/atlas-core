from creative_production.story_quality import StoryQualityDirector


def strong_scores():
    return {dimension: 92 for dimension in StoryQualityDirector.DIMENSIONS}


def test_high_quality_story_passes():
    report = StoryQualityDirector().evaluate(scores=strong_scores())
    assert report.passes
    assert report.issues == []


def test_recycled_or_unmotivated_story_is_blocked():
    report = StoryQualityDirector().evaluate(
        scores=strong_scores(), flags=["recycled_plot", "unmotivated_character"]
    )
    assert not report.passes
    assert {issue.category for issue in report.issues} == {"recycled_plot", "unmotivated_character"}


def test_forced_humor_warns_without_automatically_killing_strong_story():
    report = StoryQualityDirector().evaluate(scores=strong_scores(), flags=["forced_humor"])
    assert report.passes
    assert report.issues[0].severity == "warning"


def test_hard_quality_dimensions_have_minimum_floor():
    scores = strong_scores()
    scores["emotional_authenticity"] = 70
    report = StoryQualityDirector().evaluate(scores=scores)
    assert not report.passes
    assert any(issue.category == "emotional_authenticity" and issue.severity == "blocker" for issue in report.issues)
