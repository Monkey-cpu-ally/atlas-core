"""Job queue for long-running LLM operations.

The Kubernetes ingress in front of the backend has a hard 60-second
timeout. Several Atlas endpoints (notably tri-council blueprint) routinely
need 120–200 seconds because they chain 4+ LLM calls. To survive the
timeout we offload those calls to an in-process background task and let
the frontend poll for completion.

Design:

  • `submit(coro_factory)` returns a job_id immediately.
  • Result lifecycle is `pending → running → done / failed`.
  • Results are kept for 30 minutes then garbage-collected.
  • The store is in-memory only — fine for v1; persist later.
"""
from __future__ import annotations

import asyncio
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Optional


# How long completed jobs stay around before GC (seconds).
RESULT_TTL = 30 * 60


@dataclass
class Job:
    job_id: str
    status: str = "pending"   # pending | running | done | failed
    result: Any = None
    error: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    label: Optional[str] = None


_jobs: Dict[str, Job] = {}
_lock = threading.Lock()


def _gc_locked() -> None:
    """Drop completed jobs older than RESULT_TTL (caller already holds the lock)."""
    cutoff = time.time() - RESULT_TTL
    stale = [
        jid for jid, j in _jobs.items()
        if j.finished_at is not None and j.finished_at < cutoff
    ]
    for jid in stale:
        del _jobs[jid]


def submit(coro_factory: Callable[[], Awaitable[Any]], label: Optional[str] = None) -> str:
    """Run `coro_factory()` on the event loop and return a job_id immediately."""
    job = Job(job_id=uuid.uuid4().hex, label=label)
    with _lock:
        _gc_locked()
        _jobs[job.job_id] = job

    async def runner():
        with _lock:
            job.status = "running"
        try:
            result = await coro_factory()
            with _lock:
                job.status = "done"
                job.result = result
                job.finished_at = time.time()
        except Exception as exc:        # pragma: no cover  (bubbled to the UI)
            with _lock:
                job.status = "failed"
                job.error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
                job.finished_at = time.time()

    asyncio.create_task(runner())
    return job.job_id


def get(job_id: str) -> Optional[Job]:
    with _lock:
        return _jobs.get(job_id)


def to_dict(job: Job) -> dict:
    out = {
        "job_id": job.job_id,
        "status": job.status,
        "label": job.label,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "result": job.result,
        "error": job.error,
    }
    return out
