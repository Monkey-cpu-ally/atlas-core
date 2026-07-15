"""Transcript-first YouTube ingestion for the ATLAS Knowledge Bank.

This module deliberately separates orchestration from network access. A transcript
provider and metadata provider are injected, allowing ATLAS to use authorized
captions, YouTube APIs, local transcripts, or future multimodal services without
locking the knowledge engine to one vendor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol
from urllib.parse import parse_qs, urlparse


class IngestionError(ValueError):
    """Raised when a video cannot be safely prepared for ingestion."""


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    text: str
    start_seconds: float
    duration_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    video_id: str
    url: str
    title: str
    channel_name: str
    channel_url: str | None = None
    published_at: str | None = None
    language: str | None = None


@dataclass(slots=True)
class KnowledgeRecord:
    source_type: str
    source_url: str
    source_id: str
    title: str
    creator: str
    transcript: str
    transcript_hash: str
    ingested_at: str
    subjects: list[str] = field(default_factory=list)
    assigned_agents: list[str] = field(default_factory=list)
    review_status: str = "pending"
    confidence: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class TranscriptProvider(Protocol):
    def get_transcript(self, video_id: str) -> list[TranscriptSegment]: ...


class MetadataProvider(Protocol):
    def get_metadata(self, video_id: str, canonical_url: str) -> VideoMetadata: ...


def extract_youtube_video_id(url: str) -> str:
    """Extract a YouTube video ID from common public URL formats."""
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith(("/shorts/", "/embed/", "/live/")):
            parts = parsed.path.strip("/").split("/")
            video_id = parts[1] if len(parts) > 1 else ""
        else:
            video_id = ""
    else:
        video_id = ""

    if not video_id or len(video_id) > 32 or not all(c.isalnum() or c in "-_" for c in video_id):
        raise IngestionError("Unsupported or invalid YouTube video URL.")
    return video_id


def canonical_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def normalize_transcript(segments: list[TranscriptSegment]) -> str:
    cleaned = [" ".join(segment.text.split()) for segment in segments if segment.text.strip()]
    transcript = "\n".join(cleaned).strip()
    if not transcript:
        raise IngestionError("No usable authorized transcript was available.")
    return transcript


class YouTubeIngestionService:
    """Prepare a source-grounded knowledge record from an authorized transcript."""

    def __init__(
        self,
        transcript_provider: TranscriptProvider,
        metadata_provider: MetadataProvider,
    ) -> None:
        self._transcripts = transcript_provider
        self._metadata = metadata_provider

    def ingest(
        self,
        url: str,
        *,
        subjects: list[str] | None = None,
        assigned_agents: list[str] | None = None,
    ) -> KnowledgeRecord:
        video_id = extract_youtube_video_id(url)
        canonical_url = canonical_youtube_url(video_id)
        metadata = self._metadata.get_metadata(video_id, canonical_url)
        transcript = normalize_transcript(self._transcripts.get_transcript(video_id))
        transcript_hash = sha256(transcript.encode("utf-8")).hexdigest()

        return KnowledgeRecord(
            source_type="youtube_video",
            source_url=canonical_url,
            source_id=video_id,
            title=metadata.title,
            creator=metadata.channel_name,
            transcript=transcript,
            transcript_hash=transcript_hash,
            ingested_at=datetime.now(UTC).isoformat(),
            subjects=sorted(set(subjects or [])),
            assigned_agents=sorted(set(assigned_agents or [])),
            notes=[
                "Transcript content is a source to review, not automatic ground truth.",
                "Important claims require verification against primary or authoritative sources.",
            ],
        )
