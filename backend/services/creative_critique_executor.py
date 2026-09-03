"""ATLAS LLM-backed Creative Critic Council executor."""
from __future__ import annotations
import json
from collections.abc import Mapping
from creative_intelligence.craft_rubrics import STORY
from creative_intelligence.critic_council import CreativeCriticCouncil
from creative_intelligence.executor_registry import ExecutionRequest, ExecutionResult, registry
from creative_intelligence.reference_context import ReferenceContext
from services.llm_provider import send
SYSTEM="""You are an ATLAS specialist creative critic. Evaluate the supplied artifact rigorously, not politely. Return JSON only with keys scores, findings, revision_requests and, whenever reference intelligence is supplied, reference_boundary_check. scores must contain every supplied rubric dimension with an integer 0-100. Findings and revision_requests must be arrays of concise strings. reference_boundary_check must contain booleans passed, project_alignment, constraints_respected, anti_imitation and an array findings. Do not reward generic, rushed, derivative, incoherent, juvenile, or technically weak work. When reference intelligence is supplied, judge the artifact itself: verify that it preserves project identity, obeys project constraints, uses only transferable principles, and does not imitate distinctive reference expression. Reference limitations are hard anti-imitation boundaries."""
def _parse_json(text:str)->dict:
    cleaned=text.strip()
    if cleaned.startswith("```"):
        cleaned=cleaned.split("\n",1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"): cleaned=cleaned[:-3]
    data=json.loads(cleaned.strip())
    if not isinstance(data,dict): raise ValueError("critic response must be an object")
    return data
def _boundary_check(review:dict,critic:str)->dict:
    check=review.get("reference_boundary_check")
    if not isinstance(check,Mapping): raise ValueError(f"{critic} must return reference_boundary_check when references participate")
    required=("passed","project_alignment","constraints_respected","anti_imitation")
    if any(type(check.get(k)) is not bool for k in required): raise ValueError(f"{critic} reference_boundary_check requires boolean {', '.join(required)}")
    findings=check.get("findings")
    if not isinstance(findings,list) or any(not isinstance(v,str) or not v.strip() for v in findings): raise ValueError(f"{critic} reference_boundary_check findings must be an array of non-empty strings")
    evidence_fields=("project_alignment","constraints_respected","anti_imitation")
    evidence_verified=all(check[k] for k in evidence_fields)
    if check["passed"] is not evidence_verified: raise ValueError(f"{critic} reference boundary passed flag contradicts its evidence")
    return {"critic":critic,**{k:check[k] for k in required},"findings":findings}
async def _review(critic:str,focus:str,artifact:str,reference_context:ReferenceContext|None=None)->dict:
    dimensions=[{"name":d.name,"question":d.question,"failure_signals":list(d.failure_signals)} for d in STORY.dimensions]; context=None
    if reference_context: context={"project_identity":reference_context.project_identity,"project_constraints":list(reference_context.project_constraints),"reference_ids":list(reference_context.reference_ids),"principles":list(reference_context.principles),"study_targets":list(reference_context.study_targets),"limitations":list(reference_context.limitations),"provenance":list(reference_context.provenance),"instruction":"Use principles as evaluation lenses only. Project identity and constraints override reference influence. Inspect the artifact and return explicit boundary evidence."}
    result=await send(critic,SYSTEM,json.dumps({"critic":critic,"focus":focus,"passing_score":STORY.passing_score,"rubric":dimensions,"reference_context":context,"artifact":artifact},ensure_ascii=False)); text=result.get("text","") if isinstance(result,Mapping) else ""
    if not text.strip(): raise RuntimeError(f"{critic} returned an empty critique")
    return _parse_json(text)
async def execute_critique(request:ExecutionRequest)->ExecutionResult:
    payload=request.payload or {}; artifact=str(payload.get("artifact") or payload.get("text") or "").strip()
    if not artifact: raise ValueError("critique requires artifact text")
    reference_context=ReferenceContext.from_mapping(payload.get("reference_context")); council=CreativeCriticCouncil(); critic_scores={}; findings={}; revisions={}; boundary_checks=[]
    for critic,focus in council.CRITIC_FOCUS.items():
        review=await _review(critic,focus,artifact,reference_context); critic_scores[critic]=review.get("scores",{}); findings[critic]=list(review.get("findings",[])); revisions[critic]=list(review.get("revision_requests",[]))
        if reference_context: boundary_checks.append(_boundary_check(review,critic))
    decision=council.review(rubric=STORY,critic_scores=critic_scores,findings=findings,revision_requests=revisions); blockers=list(decision.blockers); boundaries_verified=bool(reference_context) and all(c["passed"] for c in boundary_checks)
    if reference_context and not boundaries_verified: blockers.append("reference_boundary_verification_failed")
    approved=decision.approved and (not reference_context or boundaries_verified)
    output={"approved":approved,"blockers":blockers,"revision_plan":list(decision.revision_plan),"reference_context_verified":reference_context is not None,"reference_boundaries_verified":boundaries_verified,"reference_boundary_checks":boundary_checks,"reviews":[{"critic":r.critic,"focus":r.focus,"scores":r.scores,"average":r.average,"findings":list(r.findings),"revision_requests":list(r.revision_requests)} for r in decision.reviews]}
    return ExecutionResult(request.artifact_id,output,"creative-critic-council")
def register_critique_executor()->None: registry.register("critique",execute_critique)
