"""Live adapters for ATLAS YouTube ingestion.

Transcript access uses the optional ``youtube-transcript-api`` dependency. Metadata
uses YouTube's public oEmbed response and does not require an API key.
"""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .youtube_ingestion import IngestionError, TranscriptSegment, VideoMetadata


class YouTubeTranscriptProvider:
    """Retrieve creator-provided or auto-generated captions when available."""

    def __init__(self, languages: tuple[str, ...] = ("en", "en-US", "en-GB")) -> None:
        self.languages = languages

    def get_transcript(self, video_id: str) -> list[TranscriptSegment]:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError as exc:
            raise IngestionError(
                "Live transcript support is not installed. Install ATLAS with the "
                "youtube optional dependency."
            ) from exc

        try:
            # youtube-transcript-api 1.x
            api = YouTubeTranscriptApi()
            fetched = api.fetch(video_id, languages=list(self.languages))
            raw_segments = fetched.to_raw_data()
        except AttributeError:
            # Compatibility with older releases.
            try:
                raw_segments = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=list(self.languages)
                )
            except Exception as exc:  # package exposes several provider-specific errors
                raise IngestionError(f"Transcript unavailable: {exc}") from exc
        except Exception as exc:  # package exposes several provider-specific errors
            raise IngestionError(f"Transcript unavailable: {exc}") from exc

        return [
            TranscriptSegment(
                text=str(item.get("text", "")),
                start_seconds=float(item.get("start", 0.0)),
                duration_seconds=(
                    float(item["duration"]) if item.get("duration") is not None else None
                ),
            )
            for item in raw_segments
        ]


class YouTubeOEmbedMetadataProvider:
    """Fetch basic public video metadata without storing an API key."""

    endpoint = "https://www.youtube.com/oembed"

    def __init__(self, timeout_seconds: float = 15.0) -> None:
        self.timeout_seconds = timeout_seconds

    def get_metadata(self, video_id: str, canonical_url: str) -> VideoMetadata:
        query = urlencode({"url": canonical_url, "format": "json"})
        request = Request(
            f"{self.endpoint}?{query}",
            headers={"User-Agent": "ATLAS-Knowledge-Engine/0.1"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise IngestionError(f"Unable to retrieve YouTube metadata: {exc}") from exc

        title = str(payload.get("title", "")).strip()
        channel_name = str(payload.get("author_name", "")).strip()
        if not title or not channel_name:
            raise IngestionError("YouTube returned incomplete video metadata.")

        return VideoMetadata(
            video_id=video_id,
            url=canonical_url,
            title=title,
            channel_name=channel_name,
            channel_url=str(payload.get("author_url") or "") or None,
        )
