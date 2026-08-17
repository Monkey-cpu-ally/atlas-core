"""Persistent Creative Studio job records.

The store models workflow state only. A job is never marked complete merely because
it was created; production services must explicitly advance it after real work.
"""
from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Dict, List, Optional

VALID_STAGES = ("create", "critique", "revision", "master")
VALID_STATUSES = ("queued", "running", "blocked", "failed", "completed")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CreativeJob:
    id: str
    project_id: str
    stage: str
    status: str = "queued"
    artifact_id: Optional[str] = None
    parent_job_id: Optional[str] = None
    blockers: List[str] = field(default_factory=list)
    result: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)


class CreativeJobStore:
    def __init__(self, path: str | Path | None = None):
        configured = path or os.getenv("ATLAS_CREATIVE_JOB_STORE")
        self.path = Path(configured) if configured else Path(tempfile.gettempdir()) / "atlas_creative_jobs.json"
        self._lock = RLock()

    def create(self, *, project_id: str, stage: str, artifact_id: str | None = None,
               parent_job_id: str | None = None) -> CreativeJob:
        if stage not in VALID_STAGES:
            raise ValueError(f"invalid creative stage: {stage}")
        job = CreativeJob(
            id=str(uuid.uuid4()), project_id=project_id, stage=stage,
            artifact_id=artifact_id, parent_job_id=parent_job_id,
        )
        with self._lock:
            data = self._read()
            data[job.id] = asdict(job)
            self._write(data)
        return job

    def get(self, job_id: str) -> CreativeJob | None:
        with self._lock:
            raw = self._read().get(job_id)
        return CreativeJob(**raw) if raw else None

    def list(self, project_id: str | None = None) -> List[CreativeJob]:
        with self._lock:
            values = list(self._read().values())
        jobs = [CreativeJob(**item) for item in values]
        if project_id:
            jobs = [job for job in jobs if job.project_id == project_id]
        return sorted(jobs, key=lambda job: job.created_at, reverse=True)

    def transition(self, job_id: str, *, status: str, blockers: List[str] | None = None,
                   result: Dict | None = None) -> CreativeJob:
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid creative status: {status}")
        with self._lock:
            data = self._read()
            raw = data.get(job_id)
            if not raw:
                raise KeyError(job_id)
            current = raw["status"]
            allowed = {
                "queued": {"running", "blocked", "failed"},
                "running": {"blocked", "failed", "completed"},
                "blocked": {"queued", "failed"},
                "failed": set(),
                "completed": set(),
            }
            if status != current and status not in allowed[current]:
                raise ValueError(f"invalid creative job transition: {current} -> {status}")
            raw["status"] = status
            raw["blockers"] = list(blockers or [])
            if result is not None:
                raw["result"] = result
            raw["updated_at"] = _now()
            data[job_id] = raw
            self._write(data)
            return CreativeJob(**raw)

    def _read(self) -> Dict[str, Dict]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, data: Dict[str, Dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)
