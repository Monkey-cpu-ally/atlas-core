"""ATLAS Tool Bus registry, safety gate, event log, and dispatcher."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Dict, List, Optional

from .contracts import ToolAdapter, ToolJob, ToolJobStatus, ToolResult
from .events import InMemoryEventLog, ToolEvent, ToolEventType
from .safety import SafetyDecision, SafetyPolicy


class ToolBusError(RuntimeError):
    """Raised when Tool Bus routing fails."""


class ToolBus:
    """Registry and dispatcher for ATLAS tool adapters."""

    def __init__(
        self,
        safety_policy: SafetyPolicy | None = None,
        event_log: InMemoryEventLog | None = None,
    ) -> None:
        self._adapters: Dict[str, ToolAdapter] = {}
        self._job_history: Dict[str, ToolResult] = {}
        self.safety_policy = safety_policy or SafetyPolicy()
        self.event_log = event_log or InMemoryEventLog()

    def _record(
        self,
        event_type: ToolEventType,
        job: ToolJob,
        *,
        message: str | None = None,
        metadata: Dict[str, object] | None = None,
    ) -> None:
        self.event_log.append(
            ToolEvent(
                event_type=event_type,
                job_id=job.job_id,
                tool_name=job.tool_name,
                source=job.requested_by,
                message=message,
                metadata=dict(metadata or {}),
            )
        )

    def register(self, adapter: ToolAdapter) -> None:
        if adapter.name in self._adapters:
            raise ToolBusError(f"Adapter already registered: {adapter.name}")
        adapter.initialize()
        self._adapters[adapter.name] = adapter

    def list_tools(self) -> List[str]:
        return sorted(self._adapters.keys())

    def get_adapter(self, tool_name: str) -> ToolAdapter:
        try:
            return self._adapters[tool_name]
        except KeyError as exc:
            raise ToolBusError(f"No adapter registered for tool: {tool_name}") from exc

    def get_status(self) -> Dict[str, object]:
        return {
            "tool_count": len(self._adapters),
            "tools": {name: adapter.get_status() for name, adapter in self._adapters.items()},
            "job_count": len(self._job_history),
            "event_count": len(self.event_log),
            "safety": {
                "enabled_tools": sorted(self.safety_policy.enabled_tools),
                "approved_job_count": len(self.safety_policy.approved_job_ids),
                "allow_local_writes": self.safety_policy.allow_local_writes,
                "allow_remote_writes": self.safety_policy.allow_remote_writes,
                "allow_destructive": self.safety_policy.allow_destructive,
            },
        }

    def execute(self, job: ToolJob) -> ToolResult:
        adapter = self.get_adapter(job.tool_name)
        started = datetime.now(timezone.utc).isoformat()
        start_timer = perf_counter()
        self._record(
            ToolEventType.JOB_RECEIVED,
            job,
            message=f"Job received for {job.tool_name}.{job.capability}",
            metadata={"capability": job.capability, "safety_level": job.safety_level.value},
        )

        review = self.safety_policy.review(job)
        if review.decision != SafetyDecision.ALLOW:
            status = ToolJobStatus.SKIPPED if review.decision == SafetyDecision.REQUIRE_APPROVAL else ToolJobStatus.FAILED
            event_type = ToolEventType.SAFETY_APPROVAL_REQUIRED if review.decision == SafetyDecision.REQUIRE_APPROVAL else ToolEventType.SAFETY_DENIED
            self._record(event_type, job, message="; ".join(review.reasons), metadata={"safety_decision": review.decision.value})
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

        self._record(ToolEventType.SAFETY_ALLOWED, job, message="Safety policy allowed the job.", metadata={"safety_decision": review.decision.value})
        if not adapter.verify():
            self._record(ToolEventType.ADAPTER_VERIFICATION_FAILED, job, message=f"Adapter verification failed: {job.tool_name}")
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

        self._record(ToolEventType.JOB_STARTED, job, message="Adapter execution started.")
        result = adapter.execute(job)
        result.started_at = result.started_at or started
        result.finished_at = result.finished_at or datetime.now(timezone.utc).isoformat()
        result.execution_time_ms = result.execution_time_ms or int((perf_counter() - start_timer) * 1000)
        result.metadata.setdefault("safety_decision", review.decision.value)
        self._job_history[job.job_id] = result
        self._record(
            ToolEventType.JOB_SUCCEEDED if result.success else ToolEventType.JOB_FAILED,
            job,
            message="Tool job completed successfully." if result.success else "Tool job failed.",
            metadata={"status": result.status.value, "execution_time_ms": result.execution_time_ms},
        )
        return result

    def approve_job(self, job_id: str) -> None:
        self.safety_policy.approve_job(job_id)

    def get_job_result(self, job_id: str) -> Optional[ToolResult]:
        return self._job_history.get(job_id)

    def get_job_events(self, job_id: str) -> List[ToolEvent]:
        return self.event_log.for_job(job_id)

    def cancel(self, tool_name: str, job_id: str) -> ToolResult:
        adapter = self.get_adapter(tool_name)
        result = adapter.cancel(job_id)
        self._job_history[job_id] = result
        self.event_log.append(
            ToolEvent(
                event_type=ToolEventType.JOB_CANCELLED,
                job_id=job_id,
                tool_name=tool_name,
                message="Cancellation requested through Tool Bus.",
                metadata={"status": result.status.value},
            )
        )
        return result
