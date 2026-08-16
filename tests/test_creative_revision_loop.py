from creative_intelligence.critic_council import CouncilDecision
from creative_intelligence.revision_loop import CreativeRevisionLoop


def decision(approved, plan=()):
    return CouncilDecision(reviews=(), blockers=() if approved else ("quality",), revision_plan=tuple(plan))


def test_rejected_work_can_be_revised_and_reapproved():
    def evaluate(text):
        return decision("fixed" in text, () if "fixed" in text else ("Fix the weak midpoint.",))

    result = CreativeRevisionLoop[str](max_revisions=2).run(
        artifact="draft", evaluate=evaluate, revise=lambda text, plan: text + " fixed"
    )
    assert result.approved
    assert result.stop_reason == "approved"
    assert len(result.cycles) == 2


def test_loop_stops_when_critics_offer_no_actionable_revision():
    result = CreativeRevisionLoop[str](max_revisions=3).run(
        artifact="draft", evaluate=lambda _: decision(False), revise=lambda text, plan: text + " changed"
    )
    assert not result.approved
    assert result.stop_reason == "no_actionable_revision_plan"


def test_loop_detects_revision_that_changes_nothing():
    result = CreativeRevisionLoop[str](max_revisions=3).run(
        artifact="draft",
        evaluate=lambda _: decision(False, ("Improve it.",)),
        revise=lambda text, plan: text,
    )
    assert not result.approved
    assert result.stop_reason == "revision_made_no_change"


def test_loop_never_revises_forever():
    result = CreativeRevisionLoop[str](max_revisions=2).run(
        artifact="v0",
        evaluate=lambda _: decision(False, ("Keep improving.",)),
        revise=lambda text, plan: text + "x",
    )
    assert not result.approved
    assert result.stop_reason == "revision_limit"
    assert len(result.cycles) == 3
