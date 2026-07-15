import pytest

from atlas_knowledge_engine.learning_adapter import (
    AdapterRegistry,
    ExtractedContent,
    LearningSource,
)
from atlas_knowledge_engine.learning_pipeline import LearningPipeline
from atlas_knowledge_engine.learning_queue import LearningQueue


class FakeAdapter:
    source_type = "note"

    def can_handle(self, source: LearningSource) -> bool:
        return source.source_type == "note"

    def validate(self, source: LearningSource) -> None:
        if not source.locator.strip():
            raise ValueError("missing note")

    def extract(self, source: LearningSource) -> ExtractedContent:
        return ExtractedContent(
            source_type="note",
            source_id="note-1",
            title="  Example   Note ",
            text="  Energy   is conserved.\n\nClaims need evidence.  ",
        )


def test_priority_queue_claims_lowest_number_first() -> None:
    queue = LearningQueue()
    normal = queue.submit(LearningSource("note", "normal"), priority=50)
    urgent = queue.submit(LearningSource("note", "urgent"), priority=5)

    assert queue.claim().job_id == urgent.job_id
    assert queue.claim().job_id == normal.job_id


def test_adapter_registry_rejects_duplicate_registration() -> None:
    registry = AdapterRegistry()
    registry.register(FakeAdapter())
    with pytest.raises(KeyError, match="already registered"):
        registry.register(FakeAdapter())


def test_pipeline_normalizes_content_and_runs_hooks() -> None:
    seen: list[ExtractedContent] = []
    registry = AdapterRegistry()
    registry.register(FakeAdapter())
    pipeline = LearningPipeline(registry, hooks=(seen.append,))

    job = pipeline.submit(LearningSource("note", "lesson"), priority=10)
    result = pipeline.process_next()

    assert result is not None
    assert result.job_id == job.job_id
    assert result.title == "Example Note"
    assert result.text_length == len("Energy is conserved.\nClaims need evidence.")
    assert len(result.content_hash) == 64
    assert seen[0].text == "Energy is conserved.\nClaims need evidence."
    assert pipeline.queue.get(job.job_id).status == "completed"


def test_pipeline_marks_failed_jobs() -> None:
    class BrokenAdapter(FakeAdapter):
        def extract(self, source: LearningSource) -> ExtractedContent:
            raise RuntimeError("extract failed")

    registry = AdapterRegistry()
    registry.register(BrokenAdapter())
    pipeline = LearningPipeline(registry)
    job = pipeline.submit(LearningSource("note", "lesson"))

    with pytest.raises(RuntimeError, match="extract failed"):
        pipeline.process_next()

    failed = pipeline.queue.get(job.job_id)
    assert failed.status == "failed"
    assert failed.error == "extract failed"
