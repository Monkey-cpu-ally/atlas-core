from atlas_knowledge_engine.youtube_ingestion import (
    IngestionError,
    TranscriptSegment,
    VideoMetadata,
    YouTubeIngestionService,
    extract_youtube_video_id,
)


class FakeTranscriptProvider:
    def get_transcript(self, video_id: str) -> list[TranscriptSegment]:
        assert video_id == "abc_123-XYZ"
        return [
            TranscriptSegment("  Energy   is conserved. ", 0.0, 2.0),
            TranscriptSegment("Claims still need verification.", 2.0, 3.0),
        ]


class FakeMetadataProvider:
    def get_metadata(self, video_id: str, canonical_url: str) -> VideoMetadata:
        return VideoMetadata(
            video_id=video_id,
            url=canonical_url,
            title="Example Physics Lesson",
            channel_name="Example Channel",
        )


def test_extracts_common_youtube_urls() -> None:
    expected = "abc_123-XYZ"
    assert extract_youtube_video_id(f"https://youtu.be/{expected}") == expected
    assert extract_youtube_video_id(f"https://www.youtube.com/watch?v={expected}") == expected
    assert extract_youtube_video_id(f"https://youtube.com/shorts/{expected}") == expected


def test_rejects_non_youtube_urls() -> None:
    try:
        extract_youtube_video_id("https://example.com/watch?v=abc")
    except IngestionError:
        pass
    else:
        raise AssertionError("Expected invalid host to be rejected")


def test_builds_source_grounded_record() -> None:
    service = YouTubeIngestionService(FakeTranscriptProvider(), FakeMetadataProvider())
    record = service.ingest(
        "https://youtu.be/abc_123-XYZ",
        subjects=["Physics", "Physics"],
        assigned_agents=["Minerva", "Hermes"],
    )

    assert record.source_id == "abc_123-XYZ"
    assert record.transcript == "Energy is conserved.\nClaims still need verification."
    assert record.subjects == ["Physics"]
    assert record.assigned_agents == ["Hermes", "Minerva"]
    assert record.review_status == "pending"
    assert len(record.transcript_hash) == 64
