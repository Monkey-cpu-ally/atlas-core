"""Base adapter helpers for ATLAS Tool Bus."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from ..contracts import ToolCapability, ToolJob, ToolJobStatus, ToolResult


class PlaceholderToolAdapter:
    """Safe placeholder adapter for tools that are not connected yet."""

    name = "placeholder"

    def __init__(self, name: str, capabilities: List[ToolCapability] | None = None) -> None:
        self.name = name
        self._capabilities = capabilities or []
        self._initialized = False
        self._connected = False

    def initialize(self) -> None:
        self._initialized = True

    def connect(self) -> None:
        self._connected = False

    def verify(self) -> bool:
        return False

    def get_capabilities(self) -> List[ToolCapability]:
        return self._capabilities

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "initialized": self._initialized,
            "connected": self._connected,
            "enabled": False,
            "capabilities": [capability.name for capability in self._capabilities],
        }

    def execute(self, job: ToolJob) -> ToolResult:
        now = datetime.now(timezone.utc).isoformat()
        return ToolResult(
            success=False,
            status=ToolJobStatus.SKIPPED,
            job_id=job.job_id,
            tool_name=self.name,
            started_at=now,
            finished_at=now,
            warnings=[f"{self.name} adapter is scaffold-only and not enabled."],
            metadata={"requested_capability": job.capability},
        )

    def cancel(self, job_id: str) -> ToolResult:
        now = datetime.now(timezone.utc).isoformat()
        return ToolResult(
            success=False,
            status=ToolJobStatus.CANCELLED,
            job_id=job_id,
            tool_name=self.name,
            started_at=now,
            finished_at=now,
            warnings=[f"No live {self.name} job was running."],
        )

    def disconnect(self) -> None:
        self._connected = False
