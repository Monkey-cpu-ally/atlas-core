"""Priority queue for hidden ATLAS learning jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from heapq import heappop, heappush
from itertools import count
from threading import RLock
from typing import Literal
from uuid import uuid4

from .learning_adapter import LearningSource

JobStatus = Literal["queued", "running", "completed", "failed"]


@dataclass(slots=True)
class LearningJob:
    source: LearningSource
    priority: int = 50
    job_id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = "queued"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None


class LearningQueue:
    """Thread-safe, stable priority queue. Lower numbers run first."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, str]] = []
        self._jobs: dict[str, LearningJob] = {}
        self._sequence = count()
        self._lock = RLock()

    def submit(self, source: LearningSource, *, priority: int = 50) -> LearningJob:
        if not 0 <= priority <= 100:
            raise ValueError("priority must be between 0 and 100")
        job = LearningJob(source=source, priority=priority)
        with self._lock:
            self._jobs[job.job_id] = job
            heappush(self._heap, (priority, next(self._sequence), job.job_id))
        return job

    def claim(self) -> LearningJob | None:
        with self._lock:
            while self._heap:
                _, _, job_id = heappop(self._heap)
                job = self._jobs[job_id]
                if job.status != "queued":
                    continue
                job.status = "running"
                job.started_at = datetime.now(UTC).isoformat()
                return job
        return None

    def complete(self, job_id: str) -> LearningJob:
        return self._finish(job_id, "completed")

    def fail(self, job_id: str, error: str) -> LearningJob:
        job = self._finish(job_id, "failed")
        job.error = error
        return job

    def _finish(self, job_id: str, status: Literal["completed", "failed"]) -> LearningJob:
        with self._lock:
            try:
                job = self._jobs[job_id]
            except KeyError as exc:
                raise KeyError(f"learning job not found: {job_id}") from exc
            if job.status != "running":
                raise RuntimeError(f"job must be running before it can be {status}")
            job.status = status
            job.finished_at = datetime.now(UTC).isoformat()
            return job

    def get(self, job_id: str) -> LearningJob:
        with self._lock:
            try:
                return self._jobs[job_id]
            except KeyError as exc:
                raise KeyError(f"learning job not found: {job_id}") from exc

    def counts(self) -> dict[str, int]:
        with self._lock:
            counts = {"queued": 0, "running": 0, "completed": 0, "failed": 0}
            for job in self._jobs.values():
                counts[job.status] += 1
            return counts

    def health(self) -> dict[str, object]:
        counts = self.counts()
        return {
            "status": "healthy" if counts["failed"] == 0 else "degraded",
            "jobs": counts,
        }
