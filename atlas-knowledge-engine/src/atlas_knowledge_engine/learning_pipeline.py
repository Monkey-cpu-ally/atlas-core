"""Universal source-processing pipeline for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable

from .duplicate_detector import DuplicateDetector
from .learning_adapter import AdapterRegistry, ExtractedContent, LearningSource
from .learning_queue import LearningJob, LearningQueue
from .source_registry import SourceRecord, SourceRegistry

PipelineHook = Callable[[ExtractedContent], None]


class DuplicateSourceError(RuntimeError):
    """Raised when a source or its normalized content already exists."""


@dataclass(frozen=True, slots=True)
class LearningResult:
    job_id: str
    source_id: str
    title: str
    content_hash: str
    text_length: int


class LearningPipeline:
    """Queue, validate, extract, normalize, deduplicate, and emit content.

    Storage, graph linking, confidence scoring, and AI review remain injected as
    hooks so these systems stay replaceable and independent.
    """

    def __init__(
        self,
        adapters: AdapterRegistry,
        queue: LearningQueue | None = None,
        *,
        hooks: tuple[PipelineHook, ...] = (),
        source_registry: SourceRegistry | None = None,
        duplicate_detector: DuplicateDetector | None = None,
    ) -> None:
        self.adapters = adapters
        self.queue = queue or LearningQueue()
        self.hooks = hooks
        self.source_registry = source_registry or SourceRegistry()
        self.duplicate_detector = duplicate_detector or DuplicateDetector(self.source_registry)

    def submit(self, source: LearningSource, *, priority: int = 50) -> LearningJob:
        adapter = self.adapters.resolve(source)
        adapter.validate(source)
        return self.queue.submit(source, priority=priority)

    def process_next(self) -> LearningResult | None:
        job = self.queue.claim()
        if job is None:
            return None

        try:
            adapter = self.adapters.resolve(job.source)
            adapter.validate(job.source)
            extracted = adapter.extract(job.source)
            normalized = self._normalize(extracted)
            digest = sha256(normalized.text.encode("utf-8")).hexdigest()

            duplicate = self.duplicate_detector.find(
                source_type=normalized.source_type,
                source_id=normalized.source_id,
                content_hash=digest,
            )
            if duplicate is not None:
                raise DuplicateSourceError(
                    f"duplicate {duplicate.reason}: "
                    f"{duplicate.existing.source_type}:{duplicate.existing.source_id}"
                )

            for hook in self.hooks:
                hook(normalized)

            self.source_registry.register(
                SourceRecord(
                    source_type=normalized.source_type,
                    source_id=normalized.source_id,
                    title=normalized.title,
                    content_hash=digest,
                    canonical_url=normalized.canonical_url,
                    creator=normalized.creator,
                    metadata=dict(normalized.metadata),
                )
            )
            self.queue.complete(job.job_id)
            return LearningResult(
                job_id=job.job_id,
                source_id=normalized.source_id,
                title=normalized.title,
                content_hash=digest,
                text_length=len(normalized.text),
            )
        except Exception as exc:
            self.queue.fail(job.job_id, str(exc))
            raise

    @staticmethod
    def _normalize(content: ExtractedContent) -> ExtractedContent:
        text = "\n".join(
            " ".join(line.split())
            for line in content.text.splitlines()
            if line.strip()
        ).strip()
        if not text:
            raise ValueError("adapter returned no usable content")
        title = " ".join(content.title.split()).strip()
        if not title:
            raise ValueError("adapter returned an empty title")
        source_id = content.source_id.strip()
        if not source_id:
            raise ValueError("adapter returned an empty source_id")
        return ExtractedContent(
            source_type=content.source_type.strip().lower(),
            source_id=source_id,
            title=title,
            text=text,
            canonical_url=content.canonical_url,
            creator=content.creator,
            metadata=dict(content.metadata),
        )

    def health(self) -> dict[str, object]:
        return {
            "status": "healthy",
            "adapters": self.adapters.names(),
            "queue": self.queue.counts(),
            "hooks": len(self.hooks),
            "source_registry": self.source_registry.health(),
            "duplicate_detector": self.duplicate_detector.health(),
        }
