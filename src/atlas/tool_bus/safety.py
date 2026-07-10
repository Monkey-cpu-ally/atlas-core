"""Safety policy engine for the ATLAS Tool Bus."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Set

from .contracts import ToolJob, ToolSafetyLevel


class SafetyDecision(str, Enum):
    """Possible outcomes from a Tool Bus safety review."""

    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


@dataclass(frozen=True)
class SafetyReview:
    """Result of evaluating one Tool Bus job."""

    decision: SafetyDecision
    reasons: List[str] = field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.decision == SafetyDecision.ALLOW


@dataclass
class SafetyPolicy:
    """Configurable Tool Bus safety policy.

    The default policy only allows low-risk, explicitly enabled capabilities.
    Higher-risk actions require approval or are denied.
    """

    enabled_tools: Set[str] = field(default_factory=set)
    enabled_capabilities: Dict[str, Set[str]] = field(default_factory=dict)
    approved_job_ids: Set[str] = field(default_factory=set)
    denied_requesters: Set[str] = field(default_factory=set)
    allow_read_only: bool = True
    allow_generate_only: bool = True
    allow_simulation_only: bool = True
    allow_local_writes: bool = False
    allow_remote_writes: bool = False
    allow_destructive: bool = False

    def enable_tool(self, tool_name: str, capabilities: Iterable[str] | None = None) -> None:
        """Enable a tool and optionally restrict it to named capabilities."""
        self.enabled_tools.add(tool_name)
        if capabilities is not None:
            self.enabled_capabilities[tool_name] = set(capabilities)

    def approve_job(self, job_id: str) -> None:
        """Record explicit approval for a specific job."""
        self.approved_job_ids.add(job_id)

    def review(self, job: ToolJob) -> SafetyReview:
        """Evaluate whether a Tool Bus job may proceed."""
        reasons: List[str] = []

        if job.requested_by in self.denied_requesters:
            return SafetyReview(
                SafetyDecision.DENY,
                [f"Requester is blocked: {job.requested_by}"],
            )

        if job.tool_name not in self.enabled_tools:
            return SafetyReview(
                SafetyDecision.DENY,
                [f"Tool is not enabled: {job.tool_name}"],
            )

        allowed_capabilities = self.enabled_capabilities.get(job.tool_name)
        if allowed_capabilities is not None and job.capability not in allowed_capabilities:
            return SafetyReview(
                SafetyDecision.DENY,
                [f"Capability is not enabled: {job.tool_name}.{job.capability}"],
            )

        if job.safety_level == ToolSafetyLevel.READ_ONLY and self.allow_read_only:
            return SafetyReview(SafetyDecision.ALLOW, ["Read-only job allowed by policy."])

        if job.safety_level == ToolSafetyLevel.GENERATE_ONLY and self.allow_generate_only:
            return SafetyReview(SafetyDecision.ALLOW, ["Generate-only job allowed by policy."])

        if job.safety_level == ToolSafetyLevel.SIMULATION_ONLY and self.allow_simulation_only:
            return SafetyReview(SafetyDecision.ALLOW, ["Simulation-only job allowed by policy."])

        if job.job_id in self.approved_job_ids:
            return SafetyReview(
                SafetyDecision.ALLOW,
                ["Job has explicit approval."],
            )

        if job.safety_level == ToolSafetyLevel.WRITE_LOCAL:
            if self.allow_local_writes:
                return SafetyReview(SafetyDecision.ALLOW, ["Local write allowed by policy."])
            reasons.append("Local write requires explicit approval.")

        elif job.safety_level == ToolSafetyLevel.WRITE_REMOTE:
            if self.allow_remote_writes:
                return SafetyReview(SafetyDecision.ALLOW, ["Remote write allowed by policy."])
            reasons.append("Remote write requires explicit approval.")

        elif job.safety_level == ToolSafetyLevel.DESTRUCTIVE:
            if self.allow_destructive:
                return SafetyReview(SafetyDecision.ALLOW, ["Destructive action allowed by policy."])
            return SafetyReview(
                SafetyDecision.DENY,
                ["Destructive actions are disabled by policy."],
            )

        else:
            reasons.append(f"Safety level is not allowed: {job.safety_level.value}")

        return SafetyReview(SafetyDecision.REQUIRE_APPROVAL, reasons)
