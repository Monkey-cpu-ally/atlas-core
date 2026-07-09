"""ATLAS Tool Bus scaffold.

This module provides a safe registry and dispatcher for tool adapters.
It does not connect to live external tools by itself.
"""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Dict, List, Optional

from .contracts import ToolAdapter, ToolJob, ToolJobStatus, ToolResult


class ToolBusError(RuntimeError):
    """Raised when Tool Bus routing fails."""


class ToolBus:
    """Registry and dispatcher for ATLAS tool adapters."""

    def __init__(self) -> None:
        self._adapters: Dict[str, ToolAdapter] = {}
        self._job_history: Dict[str, ToolResult] = {}

    def register(self, adapter: ToolAdapter) -> None:
        """Register a tool adapter by name."""
        if adapter.name in self._adapters:
            raise ToolBusError(f"Adapter already registered: {adapter.name}")
        adapter.initialize()
        self._adapters[adapter.name] = adapter

    def list_tools(self) -> List[str]:
        """Return registered tool names."""
        return sorted(self._adapters.keys())

    def get_adapter(self, tool_name: str) -> ToolAdapter:
        """Return a registered adapter or raise."""
        try:
            return self._adapters[tool_name]
        except KeyError as exc:
            raise ToolBusError(f"No adapter registered for tool: {tool_name}") from exc

    def get_status(self) -> Dict[str, object]:
        """Return status for the Tool Bus and each adapter."""
        return {
            "tool_count": len(self._adapters),
            "tools": {name: adapter.get_status() for name, adapter in self._adapters.items()},
            "job_count": len(self._job_history),
        }

    def execute(self, job: ToolJob) -> ToolResult:
        """Execute a job through the correct adapter."""
        adapter = self.get_adapter(job.tool_name)
        started = datetime.now(timezone.utc).isoformat()
        start_timer = perf_counter()

        if not adapter.verify():
            result = ToolResult(
                success=False,
                status=ToolJobStatus.FAILED,
                job_id=job.job_id,
                tool_name=job.tool_name,
                started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(),
                errors=[f"Adapter verification failed: {job.tool_name}"],
            )
            self._job_history[job.job_id] = result
            return result

        result = adapter.execute(job)
        result.started_at = result.started_at or started
        result.finished_at = result.finished_at or datetime.now(timezone.utc).isoformat()
        result.execution_time_ms = result.execution_time_ms or int((perf_counter() - start_timer) * 1000)
        self._job_history[job.job_id] = result
        return result

    def get_job_result(self, job_id: str) -> Optional[ToolResult]:
        """Return a previous job result if available."""
        return self._job_history.get(job_id)

    def cancel(self, tool_name: str, job_id: str) -> ToolResult:
        """Cancel a job through the correct adapter."""
        adapter = self.get_adapter(tool_name)
        result = adapter.cancel(job_id)
        self._job_history[job_id] = result
        return result
