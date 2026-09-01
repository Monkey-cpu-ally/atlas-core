"""ATLAS targeted story revision executor.

Revises an existing artifact against explicit Critic Council objections while
preserving project identity, hard constraints, and anti-imitation boundaries.
"""
from __future__ import annotations

import json
import uuid
from collections.abc import Mapping
from dataclasses import asdict

from creative_intelligence.executor_registry import ExecutionRequest, ExecutionResult, registry
from creative_intelligence.story_production import ReferenceContext
from services.llm_provider import send

SYSTEM = """You are ATLAS Story Revision. Revise professional narrative work surgically. Preserve effective character voice, imagery, structure, continuity, and scenes unless a supplied criticism requires change. Resolve every revision request. Project identity and project constraints are authoritative. Reference intelligence may supply transferable craft principles only; reference limitations are hard anti-imitation boundaries. Do not flatten distinctive material into generic prose, add forced jokes, become juvenile, imitate a living creator's distinctive style, or explain the editing process. Return only the complete revised artifact."""


async def execute_revision(request: ExecutionRequest) -> ExecutionResult:
    payload = request.payload or {}; artifact = str(payload.get("artifact") or payload.get("text") or "").strip()
    if not artifact: raise ValueError("revision requires the current artifact text")
    plan = payload.get("revision_plan") or payload.get("revision_requests") or []
    if isinstance(plan, str): plan = [plan]
    plan = [str(item).strip() for item in plan if str(item).strip()]
    if not plan: raise ValueError("revision requires explicit Critic Council revision requests")
    reference_context = ReferenceContext.from_mapping(payload.get("reference_context"))
    context = {"artifact": artifact, "revision_plan": plan, "blockers": list(payload.get("blockers") or []), "brief": payload.get("brief") or {}, "reference_context": asdict(reference_context) if reference_context else None, "instruction": "Return the full revised artifact. Resolve identified weaknesses while preserving what works, project identity, hard constraints, originality, and anti-imitation boundaries."}
    result = await send("minerva", SYSTEM, json.dumps(context, ensure_ascii=False, indent=2)); text = result.get("text", "") if isinstance(result, Mapping) else ""
    if not text.strip(): raise RuntimeError("ATLAS LLM provider returned empty revision output")
    artifact_id = str(uuid.uuid4())
    return ExecutionResult(artifact_id, {"artifact_id": artifact_id, "kind": "story_revision", "text": text.strip(), "parent_artifact_id": request.artifact_id, "resolved_revision_requests": plan, "reference_context_preserved": reference_context is not None, "requires_recritique": True}, "story-revision-service")


def register_revision_executor() -> None:
    registry.register("revision", execute_revision)
