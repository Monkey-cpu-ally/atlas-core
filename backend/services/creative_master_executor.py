"""Fail-closed Creative Studio master approval executor.

Master status is an evidence gate, not another generation pass. Approval requires a
post-revision Critic Council decision plus every applicable quality gate to pass.
"""
from __future__ import annotations

import uuid

from creative_intelligence.executor_registry import ExecutionRequest, ExecutionResult, registry

REQUIRED_GATES = (
    "creative_approval",
    "story_quality",
    "art_style",
    "visual_quality",
    "continuity",
    "originality",
)


def _passed(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return bool(value.get("passed"))
    return False


async def execute_master(request: ExecutionRequest) -> ExecutionResult:
    payload = request.payload or {}
    artifact = str(payload.get("artifact") or payload.get("text") or "").strip()
    if not artifact:
        raise ValueError("master gate requires the final artifact")

    council = payload.get("critic_council") or {}
    if not isinstance(council, dict) or council.get("approved") is not True:
        raise ValueError("master gate requires an approved post-revision Critic Council decision")
    if council.get("blockers"):
        raise ValueError("master gate cannot approve an artifact with Critic Council blockers")

    evidence = payload.get("quality_evidence") or {}
    if not isinstance(evidence, dict):
        raise ValueError("quality_evidence must be an object")

    applicable = payload.get("applicable_gates") or list(REQUIRED_GATES)
    applicable = [str(gate) for gate in applicable]
    unknown = [gate for gate in applicable if gate not in REQUIRED_GATES]
    if unknown:
        raise ValueError(f"unknown master gates: {', '.join(unknown)}")

    missing = [gate for gate in applicable if gate not in evidence]
    failed = [gate for gate in applicable if gate in evidence and not _passed(evidence[gate])]
    if missing or failed:
        reasons = []
        if missing:
            reasons.append("missing evidence: " + ", ".join(missing))
        if failed:
            reasons.append("failed gates: " + ", ".join(failed))
        raise ValueError("; ".join(reasons))

    master_id = str(uuid.uuid4())
    return ExecutionResult(request.artifact_id, {
        "master_id": master_id,
        "artifact_id": request.artifact_id,
        "approved": True,
        "status": "master",
        "critic_council": council,
        "quality_evidence": {gate: evidence[gate] for gate in applicable},
        "passed_gates": applicable,
    }, "creative-master-gate")


def register_master_executor() -> None:
    registry.register("master", execute_master)
