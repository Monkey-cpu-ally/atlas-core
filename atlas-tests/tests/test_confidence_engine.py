from __future__ import annotations

from atlas_knowledge_engine.confidence_engine import ConfidenceEngine
from atlas_knowledge_engine.learning_adapter import (
    AdapterRegistry,
    ExtractedContent,
    LearningSource,
)
from atlas_knowledge_engine.learning_pipeline import LearningPipeline


class StaticAdapter:
    source_type = "youtube"

    def can_handle(self, source: LearningSource) -> bool:
        return source.source_type == "youtube"

    def validate(self, source: LearningSource) -> None:
        if not source.locator:
            raise ValueError("missing locator")

    def extract(self, source: LearningSource) -> ExtractedContent:
        return ExtractedContent(
            source_type="youtube",
            source_id="video-123",
            title="Engineering lesson",
            text="A useful transcript about energy systems.",
            canonical_url="https://www.youtube.com/watch?v=video-123",
            creator="Example Engineering",
            metadata={"requires_verification": True},
        )


def test_official_peer_reviewed_source_scores_high() -> None:
    engine = ConfidenceEngine()
    content = ExtractedContent(
        source_type="paper",
        source_id="doi:10/example",
        title="Study",
        text="Results",
        canonical_url="https://doi.org/10/example",
        creator="University Lab",
        metadata={
            "peer_reviewed": True,
            "official_source": True,
            "citations": ["a", "b"],
        },
    )

    result = engine.assess(content)

    assert result.score >= 0.90
    assert result.label == "verified"
    assert result.requires_verification is False


def test_youtube_source_stays_marked_for_verification() -> None:
    engine = ConfidenceEngine()
    content = StaticAdapter().extract(LearningSource("youtube", "url"))

    result = engine.assess(content)

    assert result.source_class == "educational_video"
    assert result.score < 0.80
    assert result.requires_verification is True


def test_pipeline_persists_confidence_metadata() -> None:
    adapters = AdapterRegistry()
    adapters.register(StaticAdapter())
    observed: list[ExtractedContent] = []
    pipeline = LearningPipeline(adapters, hooks=(observed.append,))

    pipeline.submit(LearningSource("youtube", "https://youtu.be/video-123"))
    result = pipeline.process_next()

    assert result is not None
    assert result.confidence_label == "limited"
    assert result.requires_verification is True
    assert observed[0].metadata["confidence_score"] == result.confidence_score
    assert observed[0].metadata["requires_verification"] is True

    stored = pipeline.source_registry.get("youtube", "video-123")
    assert stored.metadata["confidence_label"] == result.confidence_label
    assert stored.metadata["source_class"] == "educational_video"
