"""ATLAS Tool Bus registry, safety gate, and dispatcher."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Dict, List, Optional

from .contracts import ToolAdapter, ToolJob, ToolJobStatus, ToolResult
from .safety import SafetyDecision, SafetyPolicy


class ToolBusError(RuntimeError):
    """Raised when Tool Bus routing fails."""


class ToolBus:
    """Registry and dispatcher for ATLAS tool adapters."""

    def __init__(self, safety_policy: SafetyPolicy | None = None) -> None:
        self._adapters: Dict[str, ToolAdapter] = {}
        self._job_history: Dict[str, ToolResult] = {}
        self.safety_policy = safety_policy or SafetyPolicy()

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
            "safety": {
                "enabled_tools": sorted(self.safety_policy.enabled_tools),
                "approved_job_count": len(self.safety_policy.approved_job_ids),
                "allow_local_writes": self.safety_policy.allow_local_writes,
                "allow_remote_writes": self.safety_policy.allow_remote_writes,
                "allow_destructive": self.safety_policy.allow_destructive,
            },
        }

    def execute(self, job: ToolJob) -> ToolResult:
        """Review and execute a job through the correct adapter."""
        adapter = self.get_adapter(job.tool_name)
        started = datetime.now(timezone.utc).isoformat()
        start_timer = perf_counter()

        review = self.safety_policy.review(job)
        if review.decision != SafetyDecision.ALLOW:
            status = (
                ToolJobStatus.SKIPPED
                if review.decision == SafetyDecision.REQUIRE_APPROVAL
                else ToolJobStatus.FAILED
            )
            result = ToolResult(
                success=False,
                status=status,
                job_id=job.job_id,
                tool_name=job.tool_name,
                started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(),
                errors=review.reasons if review.decision == SafetyDecision.DENY else [],
                warnings=review.reasons if review.decision == SafetyDecision.REQUIRE_APPROVAL else [],
                metadata={"safety_decision": review.decision.value},
            )
            self._job_history[job.job_id] = result
            return result

        if not adapter.verify():
            result = ToolResult(
                success=False,
                status=ToolJobStatus.FAILED,
                job_id=job.job_id,
                tool_name=job.tool_name,
                started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(),
                errors=[f"Adapter verification failed: {job.tool_name}"],
                metadata={"safety_decision": review.decision.value},
            )
            self._job_history[job.job_id] = result
            return result

        result = adapter.execute(job)
        result.started_at = result.started_at or started
        result.finished_at = result.finished_at or datetime.now(timezone.utc).isoformat()
        result.execution_time_ms = result.execution_time_ms or int((perf_counter() - start_timer) * 1000)
        result.metadata.setdefault("safety_decision", review.decision.value)
        self._job_history[job.job_id] = result
        return result

    def approve_job(self, job_id: str) -> None:
        """Approve a specific higher-risk job."""
        self.safety_policy.approve_job(job_id)

    def get_job_result(self, job_id: str) -> Optional[ToolResult]:
        """Return a previous job result if available."""
        return self._job_history.get(job_id)

    def cancel(self, tool_name: str, job_id: str) -> ToolResult:
        """Cancel a job through the correct adapter."""
        adapter = self.get_adapter(tool_name)
        result = adapter.cancel(job_id)
        self._job_history[job_id] = result
        return result
