"""Universal source-processing pipeline for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable

from .learning_adapter import AdapterRegistry, ExtractedContent, LearningSource
from .learning_queue import LearningJob, LearningQueue

PipelineHook = Callable[[ExtractedContent], None]


@dataclass(frozen=True, slots=True)
class LearningResult:
    job_id: str
    source_id: str
    title: str
    content_hash: str
    text_length: int


class LearningPipeline:
    """Queue, validate, extract, normalize, and emit learning content.

    Storage, graph linking, confidence scoring, and AI review are injected as
    hooks so these systems stay replaceable and independent.
    """

    def __init__(
        self,
        adapters: AdapterRegistry,
        queue: LearningQueue | None = None,
        *,
        hooks: tuple[PipelineHook, ...] = (),
    ) -> None:
        self.adapters = adapters
        self.queue = queue or LearningQueue()
        self.hooks = hooks

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
            for hook in self.hooks:
                hook(normalized)
            digest = sha256(normalized.text.encode("utf-8")).hexdigest()
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
        return ExtractedContent(
            source_type=content.source_type.strip().lower(),
            source_id=content.source_id.strip(),
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
        }
