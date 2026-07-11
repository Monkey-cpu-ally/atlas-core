"""CadQuery adapter for safe parametric geometry generation."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from ..contracts import ToolArtifact, ToolCapability, ToolJob, ToolJobStatus, ToolResult, ToolSafetyLevel


class CadQueryAdapter:
    name = "cadquery"

    def __init__(self) -> None:
        self._initialized = False
        self._connected = False
        self._error: str | None = None

    def initialize(self) -> None:
        self._initialized = True

    def connect(self) -> None:
        try:
            import cadquery as cq  # noqa: F401
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
        return [ToolCapability(name="generate_box", description="Generate a basic parametric box and export STEP/STL files.", safety_level=ToolSafetyLevel.WRITE_LOCAL, enabled_by_default=False)]

    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "initialized": self._initialized, "connected": self._connected, "enabled": self._connected, "error": self._error, "capabilities": [c.name for c in self.get_capabilities()]}

    def execute(self, job: ToolJob) -> ToolResult:
        started = datetime.now(timezone.utc)
        if job.capability != "generate_box":
            return self._failed(job, started, f"Unsupported capability: {job.capability}")
        if not self.verify():
            return self._failed(job, started, self._error or "CadQuery unavailable")
        try:
            import cadquery as cq
            width = float(job.payload.get("width", 20))
            depth = float(job.payload.get("depth", 20))
            height = float(job.payload.get("height", 20))
            if min(width, depth, height) <= 0 or max(width, depth, height) > 10000:
                raise ValueError("Dimensions must be greater than 0 and no more than 10000 mm")
            name = str(job.payload.get("name", "atlas_part")).strip().replace(" ", "_")
            out_dir = Path(str(job.payload.get("output_dir", "artifacts/cad"))).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            part = cq.Workplane("XY").box(width, depth, height)
            step_path = out_dir / f"{name}.step"
            stl_path = out_dir / f"{name}.stl"
            cq.exporters.export(part, str(step_path))
            cq.exporters.export(part, str(stl_path))
            finished = datetime.now(timezone.utc)
            return ToolResult(success=True, status=ToolJobStatus.SUCCEEDED, job_id=job.job_id, tool_name=self.name, started_at=started.isoformat(), finished_at=finished.isoformat(), artifacts=[ToolArtifact(name=step_path.name, artifact_type="step", path=str(step_path)), ToolArtifact(name=stl_path.name, artifact_type="stl", path=str(stl_path))], metadata={"dimensions_mm": {"width": width, "depth": depth, "height": height}})
        except Exception as exc:
            return self._failed(job, started, str(exc))

    def _failed(self, job: ToolJob, started: datetime, error: str) -> ToolResult:
        return ToolResult(success=False, status=ToolJobStatus.FAILED, job_id=job.job_id, tool_name=self.name, started_at=started.isoformat(), finished_at=datetime.now(timezone.utc).isoformat(), errors=[error])

    def cancel(self, job_id: str) -> ToolResult:
        now = datetime.now(timezone.utc).isoformat()
        return ToolResult(success=False, status=ToolJobStatus.CANCELLED, job_id=job_id, tool_name=self.name, started_at=now, finished_at=now, warnings=["CadQuery jobs are synchronous."])

    def disconnect(self) -> None:
        self._connected = False
