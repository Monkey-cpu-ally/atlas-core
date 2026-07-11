"""KiCad CLI adapter for safe schematic and PCB validation."""
from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from ..contracts import ToolArtifact, ToolCapability, ToolJob, ToolJobStatus, ToolResult, ToolSafetyLevel


class KiCadAdapter:
    name = "kicad"

    def __init__(self) -> None:
        self._initialized = False
        self._connected = False
        self._cli: str | None = None
        self._error: str | None = None

    def initialize(self) -> None:
        self._initialized = True

    def connect(self) -> None:
        self._cli = shutil.which("kicad-cli")
        self._connected = self._cli is not None
        self._error = None if self._connected else "kicad-cli not found on PATH"

    def verify(self) -> bool:
        if not self._initialized:
            self.initialize()
        if not self._connected:
            self.connect()
        return self._connected

    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability(name="version", description="Report the installed KiCad CLI version.", safety_level=ToolSafetyLevel.READ_ONLY, enabled_by_default=False),
            ToolCapability(name="validate_schematic", description="Run KiCad electrical-rules checking on a .kicad_sch file.", safety_level=ToolSafetyLevel.READ_ONLY, enabled_by_default=False),
            ToolCapability(name="validate_pcb", description="Run KiCad design-rules checking on a .kicad_pcb file.", safety_level=ToolSafetyLevel.READ_ONLY, enabled_by_default=False),
        ]

    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "initialized": self._initialized, "connected": self._connected, "enabled": self._connected, "cli": self._cli, "error": self._error, "capabilities": [c.name for c in self.get_capabilities()]}

    def execute(self, job: ToolJob) -> ToolResult:
        started = datetime.now(timezone.utc)
        if not self.verify():
            return self._failed(job, started, self._error or "KiCad unavailable")
        try:
            if job.capability == "version":
                command = [self._cli or "kicad-cli", "--version"]
                artifact = None
            else:
                source = Path(str(job.payload.get("path", ""))).expanduser().resolve()
                if not source.is_file():
                    raise FileNotFoundError(f"KiCad file not found: {source}")
                report_dir = Path(str(job.payload.get("output_dir", "artifacts/kicad"))).resolve()
                report_dir.mkdir(parents=True, exist_ok=True)
                report = report_dir / f"{source.stem}-{job.capability}.json"
                if job.capability == "validate_schematic":
                    command = [self._cli or "kicad-cli", "sch", "erc", "--format", "json", "--output", str(report), str(source)]
                elif job.capability == "validate_pcb":
                    command = [self._cli or "kicad-cli", "pcb", "drc", "--format", "json", "--output", str(report), str(source)]
                else:
                    raise ValueError(f"Unsupported capability: {job.capability}")
                artifact = ToolArtifact(name=report.name, artifact_type="kicad_report", path=str(report))
            completed = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
            finished = datetime.now(timezone.utc)
            success = completed.returncode == 0
            return ToolResult(success=success, status=ToolJobStatus.SUCCEEDED if success else ToolJobStatus.FAILED, job_id=job.job_id, tool_name=self.name, started_at=started.isoformat(), finished_at=finished.isoformat(), logs=[completed.stdout[-4000:]] if completed.stdout else [], errors=[completed.stderr[-4000:]] if completed.stderr and not success else [], artifacts=[artifact] if artifact and artifact.path and Path(artifact.path).exists() else [], metadata={"returncode": completed.returncode, "command": command})
        except Exception as exc:
            return self._failed(job, started, str(exc))

    def _failed(self, job: ToolJob, started: datetime, error: str) -> ToolResult:
        return ToolResult(success=False, status=ToolJobStatus.FAILED, job_id=job.job_id, tool_name=self.name, started_at=started.isoformat(), finished_at=datetime.now(timezone.utc).isoformat(), errors=[error])

    def cancel(self, job_id: str) -> ToolResult:
        now = datetime.now(timezone.utc).isoformat()
        return ToolResult(success=False, status=ToolJobStatus.CANCELLED, job_id=job_id, tool_name=self.name, started_at=now, finished_at=now, warnings=["KiCad jobs are synchronous."])

    def disconnect(self) -> None:
        self._connected = False
