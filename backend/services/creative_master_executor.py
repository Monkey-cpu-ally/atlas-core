"""Fail-closed Creative Studio master approval executor."""
from __future__ import annotations
import uuid
from collections.abc import Mapping
from creative_intelligence.critic_council import CreativeCriticCouncil
from creative_intelligence.executor_registry import ExecutionRequest, ExecutionResult, registry
from creative_intelligence.reference_context import ReferenceContext
REQUIRED_GATES=("creative_approval","story_quality","art_style","visual_quality","continuity","originality")
def _passed(value)->bool:
    if isinstance(value,bool): return value
    if isinstance(value,dict): return bool(value.get("passed"))
    return False
def _verified_reference_checks(council:dict)->bool:
    checks=council.get("reference_boundary_checks")
    if not isinstance(checks,list) or len(checks)!=len(CreativeCriticCouncil.CRITIC_FOCUS): return False
    expected=set(CreativeCriticCouncil.CRITIC_FOCUS); seen=set()
    for check in checks:
        if not isinstance(check,Mapping): return False
        critic=check.get("critic")
        if critic not in expected or critic in seen: return False
        seen.add(critic)
        fields=("project_alignment","constraints_respected","anti_imitation")
        if any(type(check.get(field)) is not bool for field in fields) or type(check.get("passed")) is not bool: return False
        evidence=all(check[field] for field in fields)
        if check["passed"] is not evidence or not evidence: return False
    return seen==expected
async def execute_master(request:ExecutionRequest)->ExecutionResult:
    payload=request.payload or {}; artifact=str(payload.get("artifact") or payload.get("text") or "").strip()
    if not artifact: raise ValueError("master gate requires the final artifact")
    council=payload.get("critic_council") or {}
    if not isinstance(council,dict) or council.get("approved") is not True: raise ValueError("master gate requires an approved post-revision Critic Council decision")
    if council.get("blockers"): raise ValueError("master gate cannot approve an artifact with Critic Council blockers")
    reference_context=ReferenceContext.from_mapping(payload.get("reference_context"))
    if reference_context and (council.get("reference_boundaries_verified") is not True or not _verified_reference_checks(council)): raise ValueError("master gate requires semantic Critic Council proof from every critic that reference boundaries passed")
    evidence=payload.get("quality_evidence") or {}
    if not isinstance(evidence,dict): raise ValueError("quality_evidence must be an object")
    applicable=[str(g) for g in (payload.get("applicable_gates") or list(REQUIRED_GATES))]; unknown=[g for g in applicable if g not in REQUIRED_GATES]
    if unknown: raise ValueError(f"unknown master gates: {', '.join(unknown)}")
    missing=[g for g in applicable if g not in evidence]; failed=[g for g in applicable if g in evidence and not _passed(evidence[g])]
    if reference_context and "originality" not in applicable: missing.append("originality (required when reference intelligence is attached)")
    if missing or failed:
        reasons=[]
        if missing: reasons.append("missing evidence: "+", ".join(missing))
        if failed: reasons.append("failed gates: "+", ".join(failed))
        raise ValueError("; ".join(reasons))
    master_id=str(uuid.uuid4()); return ExecutionResult(request.artifact_id,{"master_id":master_id,"artifact_id":request.artifact_id,"approved":True,"status":"master","critic_council":council,"reference_boundaries_verified":reference_context is not None and _verified_reference_checks(council),"quality_evidence":{g:evidence[g] for g in applicable},"passed_gates":applicable},"creative-master-gate")
def register_master_executor()->None: registry.register("master",execute_master)
