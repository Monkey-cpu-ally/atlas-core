from creative_intelligence.craft_rubrics import STORY
from creative_intelligence.critic_council import CreativeCriticCouncil


def complete(value=96):
    return {dimension.name: value for dimension in STORY.dimensions}


def test_three_critics_can_approve_strong_work():
    scores = {name: complete() for name in ("minerva", "hermes", "ajani")}
    decision = CreativeCriticCouncil().review(rubric=STORY, critic_scores=scores)
    assert decision.approved
    assert decision.blockers == ()


def test_one_specialist_objection_blocks_instead_of_being_averaged_away():
    scores = {name: complete() for name in ("minerva", "hermes", "ajani")}
    scores["hermes"]["internal_logic"] = 72
    decision = CreativeCriticCouncil().review(rubric=STORY, critic_scores=scores)
    assert not decision.approved
    assert "hermes:internal_logic" in decision.blockers


def test_missing_critic_fails_closed():
    scores = {"minerva": complete(), "hermes": complete()}
    decision = CreativeCriticCouncil().review(rubric=STORY, critic_scores=scores)
    assert not decision.approved
    assert "missing_critic:ajani" in decision.blockers


def test_revision_requests_are_combined_without_duplicates():
    scores = {name: complete() for name in ("minerva", "hermes", "ajani")}
    scores["ajani"]["pacing"] = 80
    decision = CreativeCriticCouncil().review(
        rubric=STORY,
        critic_scores=scores,
        revision_requests={
            "minerva": ["Strengthen Gretel's emotional reason for returning."],
            "hermes": ["Clarify the supernatural rule before the third act."],
            "ajani": ["Compress the repeated forest pursuit.", "Clarify the supernatural rule before the third act."],
        },
    )
    assert not decision.approved
    assert decision.revision_plan == (
        "Strengthen Gretel's emotional reason for returning.",
        "Clarify the supernatural rule before the third act.",
        "Compress the repeated forest pursuit.",
    )
