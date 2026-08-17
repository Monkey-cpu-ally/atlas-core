"""ATLAS targeted story revision executor.

Revises an existing artifact against explicit Critic Council objections. It preserves
working material instead of blindly regenerating the entire story.
"""
from __future__ import annotations

import json
import uuid
from collections.abc import Mapping

from creative_intelligence.executor_registry import ExecutionRequest, ExecutionResult, registry
from services.llm_provider import send

SYSTEM = """You are ATLAS Story Revision. Revise professional narrative work surgically. Preserve effective character voice, imagery, structure, continuity, and scenes unless a supplied criticism requires change. Resolve every revision request. Do not flatten distinctive material into generic prose, add forced jokes, become juvenile, imitate a living creator's distinctive style, or explain the editing process. Return only the complete revised artifact."""


async def execute_revision(request: ExecutionRequest) -> ExecutionResult:
    payload = request.payload or {}
    artifact = str(payload.get("artifact") or payload.get("text") or "").strip()
    if not artifact:
        raise ValueError("revision requires the current artifact text")

    plan = payload.get("revision_plan") or payload.get("revision_requests") or []
    if isinstance(plan, str):
        plan = [plan]
    plan = [str(item).strip() for item in plan if str(item).strip()]
    if not plan:
        raise ValueError("revision requires explicit Critic Council revision requests")

    context = {
        "artifact": artifact,
        "revision_plan": plan,
        "blockers": list(payload.get("blockers") or []),
        "brief": payload.get("brief") or {},
        "instruction": "Return the full revised artifact. Change only what is needed to resolve the identified weaknesses while preserving what already works.",
    }
    result = await send("minerva", SYSTEM, json.dumps(context, ensure_ascii=False, indent=2))
    text = result.get("text", "") if isinstance(result, Mapping) else ""
    if not text.strip():
        raise RuntimeError("ATLAS LLM provider returned empty revision output")

    artifact_id = str(uuid.uuid4())
    return ExecutionResult(artifact_id, {
        "artifact_id": artifact_id,
        "kind": "story_revision",
        "text": text.strip(),
        "parent_artifact_id": request.artifact_id,
        "resolved_revision_requests": plan,
        "requires_recritique": True,
    }, "story-revision-service")


def register_revision_executor() -> None:
    registry.register("revision", execute_revision)
