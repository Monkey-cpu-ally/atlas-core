"""Factory helpers for assembling ATLAS learning services."""

from __future__ import annotations

import os

from .json_learning_queue import JsonLearningQueue
from .json_source_registry import JsonSourceRegistry
from .learning_adapter import AdapterRegistry
from .learning_pipeline import LearningPipeline, PipelineHook
from .learning_queue import LearningQueue
from .source_registry import SourceRegistry
from .youtube_adapter import YouTubeLearningAdapter
from .youtube_live import YouTubeOEmbedMetadataProvider, YouTubeTranscriptProvider


def build_default_learning_pipeline(
    *,
    hooks: tuple[PipelineHook, ...] = (),
    source_registry_path: str | os.PathLike[str] | None = None,
    learning_queue_path: str | os.PathLike[str] | None = None,
) -> LearningPipeline:
    """Build the default pipeline with currently supported live adapters.

    YouTube is the first production adapter. Future GitHub, PDF, paper, and
    documentation adapters should register here without changing callers.

    Optional JSON paths enable restart-safe source and queue persistence. When
    omitted, lightweight in-memory implementations are used.
    """

    adapters = AdapterRegistry()
    adapters.register(
        YouTubeLearningAdapter(
            transcript_provider=YouTubeTranscriptProvider(),
            metadata_provider=YouTubeOEmbedMetadataProvider(),
        )
    )

    source_registry: SourceRegistry
    if source_registry_path is None:
        source_registry = SourceRegistry()
    else:
        source_registry = JsonSourceRegistry(source_registry_path)

    queue: LearningQueue
    if learning_queue_path is None:
        queue = LearningQueue()
    else:
        queue = JsonLearningQueue(learning_queue_path)

    return LearningPipeline(
        adapters=adapters,
        queue=queue,
        hooks=hooks,
        source_registry=source_registry,
    )
