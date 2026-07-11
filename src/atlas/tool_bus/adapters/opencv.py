"""OpenCV adapter for safe image inspection."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from ..contracts import ToolArtifact, ToolCapability, ToolJob, ToolJobStatus, ToolResult, ToolSafetyLevel


class OpenCVAdapter:
    name = "opencv"

    def __init__(self) -> None:
        self._initialized = False
        self._connected = False
        self._error: str | None = None

    def initialize(self) -> None:
        self._initialized = True

    def connect(self) -> None:
        try:
            import cv2  # noqa: F401
            self._connected = True
            self._error = None
        except Exception as exc:
            self._connected = False
            self._error = str(exc)

    def verify(self) -> bool:
        if not self._initialized:
            self.initialize()
        if not self._connected:
            self.connect()
        return self._connected

    def get_capabilities(self) -> List[ToolCapability]:
        return [ToolCapability(name="inspect_image", description="Read image dimensions and channels without modifying the source.", safety_level=ToolSafetyLevel.READ_ONLY, enabled_by_default=False)]

    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "initialized": self._initialized, "connected": self._connected, "enabled": self._connected, "error": self._error, "capabilities": [c.name for c in self.get_capabilities()]}

    def execute(self, job: ToolJob) -> ToolResult:
        started = datetime.now(timezone.utc)
        if job.capability != "inspect_image":
            return self._failed(job, started, f"Unsupported capability: {job.capability}")
        if not self.verify():
            return self._failed(job, started, self._error or "OpenCV unavailable")
        path = Path(str(job.payload.get("path", ""))).expanduser().resolve()
        if not path.is_file():
            return self._failed(job, started, f"Image not found: {path}")
        try:
            import cv2
            image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            if image is None:
                raise ValueError("OpenCV could not decode the image")
            height, width = image.shape[:2]
            channels = 1 if image.ndim == 2 else image.shape[2]
            finished = datetime.now(timezone.utc)
            return ToolResult(success=True, status=ToolJobStatus.SUCCEEDED, job_id=job.job_id, tool_name=self.name, started_at=started.isoformat(), finished_at=finished.isoformat(), artifacts=[ToolArtifact(name=path.name, artifact_type="image", path=str(path))], metadata={"width": width, "height": height, "channels": channels, "dtype": str(image.dtype)})
        except Exception as exc:
            return self._failed(job, started, str(exc))

    def _failed(self, job: ToolJob, started: datetime, error: str) -> ToolResult:
        return ToolResult(success=False, status=ToolJobStatus.FAILED, job_id=job.job_id, tool_name=self.name, started_at=started.isoformat(), finished_at=datetime.now(timezone.utc).isoformat(), errors=[error])

    def cancel(self, job_id: str) -> ToolResult:
        now = datetime.now(timezone.utc).isoformat()
        return ToolResult(success=False, status=ToolJobStatus.CANCELLED, job_id=job_id, tool_name=self.name, started_at=now, finished_at=now, warnings=["OpenCV jobs are synchronous."])

    def disconnect(self) -> None:
        self._connected = False
