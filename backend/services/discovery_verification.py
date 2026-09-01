"""Experiment design, evidence evaluation, and replication controls for Discovery Intelligence."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from uuid import uuid4
from services import evidence_scoring

class DiscoveryVerificationError(RuntimeError): pass

def design_experiment(*, hypothesis: str, independent_variables: List[str], dependent_variables: List[str], controls: List[str], procedure: List[str], pass_fail_criteria: List[str], safety_constraints: Optional[List[str]]=None, replication_target: int=2) -> Dict[str, Any]:
    if not hypothesis.strip(): raise DiscoveryVerificationError("hypothesis is required")
    if not independent_variables or not dependent_variables or not controls or not procedure or not pass_fail_criteria: raise DiscoveryVerificationError("experiment requires variables, controls, procedure, and pass/fail criteria")
    if replication_target < 1: raise DiscoveryVerificationError("replication_target must be at least 1")
    return {"experiment_id":f"EXP-{str(uuid4())[:8]}","hypothesis":hypothesis.strip(),"independent_variables":independent_variables,"dependent_variables":dependent_variables,"controls":controls,"procedure":procedure,"pass_fail_criteria":pass_fail_criteria,"safety_constraints":safety_constraints or [],"replication_target":replication_target,"status":"TEST_DESIGNED","claim_rule":"A test design is not a result."}

def evaluate_evidence(*, evidence: List[Dict[str, Any]], conflicts: Optional[List[Dict[str, Any]]]=None) -> Dict[str, Any]:
    scored=evidence_scoring.score_evidence(evidence); conflicts=conflicts or []
    if conflicts: disposition="CONFLICT_REVIEW_REQUIRED"
    elif scored["score"]>=80: disposition="STRONG_EVIDENCE_FOR_REVIEW"
    elif scored["score"]>=60: disposition="MODERATE_EVIDENCE_FOR_REVIEW"
    else: disposition="INSUFFICIENT_EVIDENCE"
    return {"evaluation_id":f"EV-{str(uuid4())[:8]}","evidence_score":scored,"conflicts":conflicts,"disposition":disposition,"claim_rule":"Evidence strength supports review; it does not independently establish truth."}

def evaluate_replication(*, original_result: Dict[str, Any], replication_runs: List[Dict[str, Any]], required_successes: int=2, independent_required: bool=True) -> Dict[str, Any]:
    if required_successes < 1: raise DiscoveryVerificationError("required_successes must be at least 1")
    successes=[r for r in replication_runs if r.get("outcome")=="supports"]
    independent=[r for r in successes if r.get("independent") is True]
    replicated=len(successes)>=required_successes
    independently_verified=replicated and (not independent_required or len(independent)>=1)
    if independently_verified: status="INDEPENDENTLY_VERIFIED"
    elif replicated: status="REPLICATED"
    elif replication_runs: status="INCONCLUSIVE"
    else: status="AWAITING_REPLICATION"
    return {"replication_id":f"REP-{str(uuid4())[:8]}","original_result":original_result,"run_count":len(replication_runs),"support_count":len(successes),"independent_support_count":len(independent),"required_successes":required_successes,"status":status,"claim_rule":"Replication status is based only on recorded runs; simulation-only runs must not be labeled physical verification."}
