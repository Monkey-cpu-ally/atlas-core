"""Factory helpers for assembling ATLAS learning services."""

from __future__ import annotations

from .learning_adapter import AdapterRegistry
from .learning_pipeline import LearningPipeline, PipelineHook
from .youtube_adapter import YouTubeLearningAdapter
from .youtube_live import YouTubeOEmbedMetadataProvider, YouTubeTranscriptProvider


def build_default_learning_pipeline(
    *,
    hooks: tuple[PipelineHook, ...] = (),
) -> LearningPipeline:
    """Build the default pipeline with currently supported live adapters.

    YouTube is the first production adapter. Future GitHub, PDF, paper, and
    documentation adapters should register here without changing callers.
    """

    adapters = AdapterRegistry()
    adapters.register(
        YouTubeLearningAdapter(
            transcript_provider=YouTubeTranscriptProvider(),
            metadata_provider=YouTubeOEmbedMetadataProvider(),
        )
    )
    return LearningPipeline(adapters=adapters, hooks=hooks)
