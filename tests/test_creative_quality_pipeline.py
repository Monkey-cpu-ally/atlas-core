from creative_intelligence.critic_council import CouncilDecision
from creative_intelligence.quality_pipeline import CreativeQualityPipeline
from creative_production.reference_provenance import OriginalityAssessment


def originality(passes=True):
    return OriginalityAssessment(
        influences=[],
        similarity_scores={"ref": 0.2},
        violations=[] if passes else ["reference_similarity_too_high:ref"],
    )


def decision(approved, plan=()):
    return CouncilDecision(
        reviews=(),
        blockers=() if approved else ("quality",),
        revision_plan=tuple(plan),
    )


def test_pipeline_resolves_references_and_approves_after_revision():
    pipeline = CreativeQualityPipeline[str](max_revisions=2)

    def evaluate(text):
        return decision("fixed" in text, () if "fixed" in text else ("Fix weak midpoint.",))

    result = pipeline.run(
        artifact="draft",
        reference_queries=("Primal", "silhouette"),
        originality=originality(),
        evaluate=evaluate,
        revise=lambda text, plan: text + " fixed",
    )
    assert result.approved
    assert result.references
    assert result.revision is not None
    assert result.revision.stop_reason == "approved"


def test_originality_failure_blocks_before_revision():
    pipeline = CreativeQualityPipeline[str]()
    result = pipeline.run(
        artifact="draft",
        reference_queries=("Primal",),
        originality=originality(False),
        evaluate=lambda _: decision(True),
        revise=lambda text, plan: text,
    )
    assert not result.approved
    assert result.revision is None
    assert any(item.startswith("originality:") for item in result.blockers)


def test_missing_reference_context_fails_closed():
    pipeline = CreativeQualityPipeline[str]()
    result = pipeline.run(
        artifact="draft",
        reference_queries=("definitely-not-a-reference",),
        originality=originality(),
        evaluate=lambda _: decision(True),
        revise=lambda text, plan: text,
    )
    assert not result.approved
    assert "no_reference_context" in result.blockers


def test_unresolved_critique_remains_blocked():
    pipeline = CreativeQualityPipeline[str](max_revisions=1)
    result = pipeline.run(
        artifact="draft",
        reference_queries=("Primal",),
        originality=originality(),
        evaluate=lambda _: decision(False, ("Improve pacing.",)),
        revise=lambda text, plan: text + "x",
    )
    assert not result.approved
    assert "critique:revision_limit" in result.blockers
