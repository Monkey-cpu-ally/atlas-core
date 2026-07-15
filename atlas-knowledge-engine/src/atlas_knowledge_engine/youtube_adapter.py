"""YouTube adapter for the universal ATLAS learning pipeline."""

from __future__ import annotations

from urllib.parse import urlparse

from .learning_adapter import ExtractedContent, LearningSource
from .youtube_ingestion import (
    IngestionError,
    MetadataProvider,
    TranscriptProvider,
    canonical_youtube_url,
    extract_youtube_video_id,
    normalize_transcript,
)


class YouTubeLearningAdapter:
    """Extract caption text and metadata from a YouTube source.

    Network access remains injected through transcript and metadata providers so
    the adapter is testable and can later use local, official, or alternative
    provider implementations without changing the learning pipeline.
    """

    source_type = "youtube"

    def __init__(
        self,
        transcript_provider: TranscriptProvider,
        metadata_provider: MetadataProvider,
    ) -> None:
        self._transcripts = transcript_provider
        self._metadata = metadata_provider

    def can_handle(self, source: LearningSource) -> bool:
        if source.source_type.strip().lower() == self.source_type:
            return True
        try:
            host = urlparse(source.locator.strip()).netloc.lower().removeprefix("www.")
            return host in {
                "youtube.com",
                "m.youtube.com",
                "music.youtube.com",
                "youtu.be",
            }
        except ValueError:
            return False

    def validate(self, source: LearningSource) -> None:
        if not source.locator.strip():
            raise IngestionError("YouTube source URL cannot be empty.")
        extract_youtube_video_id(source.locator)

    def extract(self, source: LearningSource) -> ExtractedContent:
        self.validate(source)
        video_id = extract_youtube_video_id(source.locator)
        canonical_url = canonical_youtube_url(video_id)
        metadata = self._metadata.get_metadata(video_id, canonical_url)
        transcript = normalize_transcript(self._transcripts.get_transcript(video_id))

        merged_metadata = dict(source.metadata)
        merged_metadata.update(
            {
                "video_id": video_id,
                "channel_url": metadata.channel_url,
                "published_at": metadata.published_at,
                "language": metadata.language,
                "review_status": "pending",
                "verification_required": True,
            }
        )

        return ExtractedContent(
            source_type=self.source_type,
            source_id=video_id,
            title=metadata.title,
            text=transcript,
            canonical_url=canonical_url,
            creator=metadata.channel_name,
            metadata=merged_metadata,
        )
