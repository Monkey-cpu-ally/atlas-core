from atlas_knowledge_engine.learning_adapter import AdapterRegistry, LearningSource
from atlas_knowledge_engine.learning_pipeline import LearningPipeline
from atlas_knowledge_engine.youtube_adapter import YouTubeLearningAdapter
from atlas_knowledge_engine.youtube_ingestion import TranscriptSegment, VideoMetadata


class FakeTranscriptProvider:
    def get_transcript(self, video_id: str) -> list[TranscriptSegment]:
        assert video_id == "abc_123-XYZ"
        return [
            TranscriptSegment("  Energy   storage ", 0.0, 1.0),
            TranscriptSegment("needs verification.", 1.0, 2.0),
        ]


class FakeMetadataProvider:
    def get_metadata(self, video_id: str, canonical_url: str) -> VideoMetadata:
        return VideoMetadata(
            video_id=video_id,
            url=canonical_url,
            title="  Battery   Lesson ",
            channel_name="Example Engineering",
            channel_url="https://youtube.com/@example",
            language="en",
        )


def build_pipeline() -> LearningPipeline:
    registry = AdapterRegistry()
    registry.register(YouTubeLearningAdapter(FakeTranscriptProvider(), FakeMetadataProvider()))
    return LearningPipeline(registry)


def test_youtube_adapter_runs_through_universal_pipeline() -> None:
    pipeline = build_pipeline()
    job = pipeline.submit(
        LearningSource(
            source_type="youtube",
            locator="https://youtu.be/abc_123-XYZ",
            metadata={"subjects": ["Energy"]},
        )
    )

    result = pipeline.process_next()

    assert result is not None
    assert result.job_id == job.job_id
    assert result.source_id == "abc_123-XYZ"
    assert result.title == "Battery Lesson"
    assert result.text_length == len("Energy storage\nneeds verification.")
    assert len(result.content_hash) == 64
    assert pipeline.queue.counts()["completed"] == 1


def test_registry_resolves_youtube_by_url_when_type_is_generic() -> None:
    registry = AdapterRegistry()
    adapter = YouTubeLearningAdapter(FakeTranscriptProvider(), FakeMetadataProvider())
    registry.register(adapter)

    resolved = registry.resolve(
        LearningSource(source_type="url", locator="https://youtube.com/shorts/abc_123-XYZ")
    )

    assert resolved is adapter
