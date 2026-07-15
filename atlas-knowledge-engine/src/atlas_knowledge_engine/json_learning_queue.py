"""Persistent JSON-backed learning queue for ATLAS."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from threading import RLock
from typing import Any

from .learning_adapter import LearningSource
from .learning_queue import LearningJob, LearningQueue


class JsonLearningQueue(LearningQueue):
    """Learning queue that survives restarts.

    Queued jobs are restored as queued. Jobs that were running when the process
    stopped are treated as interrupted and safely returned to the queue.
    """

    FORMAT_VERSION = 1

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = Path(path)
        self._file_lock = RLock()
        super().__init__()
        self._load()

    def submit(self, source: LearningSource, *, priority: int = 50) -> LearningJob:
        job = super().submit(source, priority=priority)
        self._persist_or_rollback()
        return job

    def claim(self) -> LearningJob | None:
        job = super().claim()
        if job is not None:
            self._persist_or_rollback()
        return job

    def complete(self, job_id: str) -> LearningJob:
        job = super().complete(job_id)
        self._persist_or_rollback()
        return job

    def fail(self, job_id: str, error: str) -> LearningJob:
        job = super().fail(job_id, error)
        self._persist_or_rollback()
        return job

    def _persist_or_rollback(self) -> None:
        try:
            self._persist()
        except Exception:
            self._reset_from_disk()
            raise

    def _reset_from_disk(self) -> None:
        with self._lock:
            self._heap.clear()
            self._jobs.clear()
            from itertools import count
            self._sequence = count()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid learning queue JSON: {self.path}") from exc

        if not isinstance(raw, dict):
            raise ValueError("learning queue root must be an object")
        if raw.get("format_version") != self.FORMAT_VERSION:
            raise ValueError("unsupported learning queue format version")

        jobs = raw.get("jobs", [])
        if not isinstance(jobs, list):
            raise ValueError("learning queue jobs must be a list")

        from heapq import heappush
        for sequence, item in enumerate(jobs):
            job = self._job_from_dict(item)
            if job.status == "running":
                job.status = "queued"
                job.started_at = None
                job.error = "recovered after interrupted processing"
            self._jobs[job.job_id] = job
            if job.status == "queued":
                heappush(self._heap, (job.priority, sequence, job.job_id))

    def _persist(self) -> None:
        with self._lock:
            jobs = [asdict(job) for job in self._jobs.values()]
        payload = {"format_version": self.FORMAT_VERSION, "jobs": jobs}
        serialized = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_lock:
            descriptor, temporary_name = tempfile.mkstemp(
                dir=str(self.path.parent),
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                text=True,
            )
            temporary_path = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(serialized)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary_path, self.path)
            finally:
                if temporary_path.exists():
                    temporary_path.unlink()

    @staticmethod
    def _job_from_dict(item: dict[str, Any]) -> LearningJob:
        if not isinstance(item, dict):
            raise ValueError("learning queue job must be an object")
        source_data = item.get("source")
        if not isinstance(source_data, dict):
            raise ValueError("learning queue job source must be an object")
        source = LearningSource(
            source_type=str(source_data.get("source_type", "")),
            locator=str(source_data.get("locator", "")),
            metadata=dict(source_data.get("metadata", {})),
        )
        return LearningJob(
            source=source,
            priority=int(item.get("priority", 50)),
            job_id=str(item.get("job_id", "")),
            status=str(item.get("status", "queued")),
            created_at=str(item.get("created_at", "")),
            started_at=item.get("started_at"),
            finished_at=item.get("finished_at"),
            error=item.get("error"),
        )

    def health(self) -> dict[str, object]:
        status = super().health()
        status.update(
            {
                "storage": "json",
                "path": str(self.path),
                "persistent": True,
                "file_exists": self.path.exists(),
            }
        )
        return status
