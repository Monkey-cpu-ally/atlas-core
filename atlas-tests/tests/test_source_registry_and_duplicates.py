import pytest

from atlas_knowledge_engine.duplicate_detector import DuplicateDetector
from atlas_knowledge_engine.learning_adapter import (
    AdapterRegistry,
    ExtractedContent,
    LearningSource,
)
from atlas_knowledge_engine.learning_pipeline import DuplicateSourceError, LearningPipeline
from atlas_knowledge_engine.source_registry import SourceRecord, SourceRegistry


class StaticAdapter:
    source_type = "test"

    def can_handle(self, source: LearningSource) -> bool:
        return source.source_type == self.source_type

    def validate(self, source: LearningSource) -> None:
        if not source.locator:
            raise ValueError("locator required")

    def extract(self, source: LearningSource) -> ExtractedContent:
        return ExtractedContent(
            source_type="test",
            source_id=source.locator,
            title=f"Title {source.locator}",
            text=str(source.metadata.get("text", "same normalized content")),
            canonical_url=f"https://example.test/{source.locator}",
        )


def build_pipeline() -> LearningPipeline:
    adapters = AdapterRegistry()
    adapters.register(StaticAdapter())
    return LearningPipeline(adapters)


def test_source_registry_tracks_identity_and_hash() -> None:
    registry = SourceRegistry()
    record = SourceRecord("youtube", "abc", "Lesson", "hash-1")
    registry.register(record)

    assert registry.get("YouTube", "abc") == record
    assert registry.find_by_hash("hash-1") == record
    assert registry.health()["sources"] == 1


def test_duplicate_detector_matches_identity_before_hash() -> None:
    registry = SourceRegistry()
    record = SourceRecord("youtube", "abc", "Lesson", "hash-1")
    registry.register(record)
    detector = DuplicateDetector(registry)

    match = detector.find(source_type="youtube", source_id="abc", content_hash="other")
    assert match is not None
    assert match.reason == "source_identity"


def test_pipeline_registers_first_source() -> None:
    pipeline = build_pipeline()
    pipeline.submit(LearningSource("test", "one"))

    result = pipeline.process_next()

    assert result is not None
    assert pipeline.source_registry.get("test", "one").content_hash == result.content_hash
    assert pipeline.queue.counts()["completed"] == 1


def test_pipeline_rejects_same_source_twice() -> None:
    pipeline = build_pipeline()
    source = LearningSource("test", "one")
    pipeline.submit(source)
    pipeline.process_next()
    pipeline.submit(source)

    with pytest.raises(DuplicateSourceError, match="source_identity"):
        pipeline.process_next()

    assert pipeline.queue.counts()["failed"] == 1


def test_pipeline_rejects_same_content_from_different_source() -> None:
    pipeline = build_pipeline()
    pipeline.submit(LearningSource("test", "one", {"text": "identical"}))
    pipeline.process_next()
    pipeline.submit(LearningSource("test", "two", {"text": "identical"}))

    with pytest.raises(DuplicateSourceError, match="content_hash"):
        pipeline.process_next()

    assert len(pipeline.source_registry.records()) == 1


def test_duplicate_does_not_run_downstream_hooks() -> None:
    adapters = AdapterRegistry()
    adapters.register(StaticAdapter())
    seen: list[str] = []
    pipeline = LearningPipeline(adapters, hooks=(lambda content: seen.append(content.source_id),))

    pipeline.submit(LearningSource("test", "one"))
    pipeline.process_next()
    pipeline.submit(LearningSource("test", "one"))

    with pytest.raises(DuplicateSourceError):
        pipeline.process_next()

    assert seen == ["one"]
