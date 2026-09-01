"""Assumption, contradiction, and prior-art gates for ATLAS Discovery Intelligence."""
from __future__ import annotations
from typing import Any, Dict, List
from uuid import uuid4


class DiscoveryChallengeError(RuntimeError):
    pass


def challenge_hypothesis(*, statement: str, assumptions: List[str], supporting_claims: List[Dict[str, Any]], conflicting_claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not statement.strip():
        raise DiscoveryChallengeError("hypothesis statement is required")
    challenges=[]
    for assumption in assumptions:
        challenges.append({"type":"ASSUMPTION","text":assumption,"question":f"What evidence would show this assumption is false: {assumption}?"})
    for claim in conflicting_claims:
        challenges.append({"type":"CONTRADICTION","text":claim.get("claim") or claim.get("title") or "conflicting evidence","source_ref":claim.get("source_ref") or claim.get("url"),"resolution_required":True})
    return {"challenge_id":f"CH-{str(uuid4())[:8]}","statement":statement.strip(),"support_count":len(supporting_claims),"conflict_count":len(conflicting_claims),"challenges":challenges,"status":"CONTRADICTION_REVIEW_REQUIRED" if conflicting_claims else "ASSUMPTIONS_EXPOSED","claim_rule":"Absence of a recorded contradiction does not prove a hypothesis true."}


def assess_prior_art(*, candidate_statement: str, search_queries: List[str], matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not candidate_statement.strip() or not search_queries:
        raise DiscoveryChallengeError("prior-art assessment requires a candidate statement and search queries")
    normalized=[]
    strongest="NONE_RECORDED"
    rank={"NONE_RECORDED":0,"RELATED":1,"CLOSE":2,"DIRECT":3}
    for match in matches:
        similarity=str(match.get("similarity","RELATED")).upper()
        if similarity not in rank: similarity="RELATED"
        normalized.append({"title":match.get("title","Untitled prior art"),"source_ref":match.get("source_ref") or match.get("url"),"similarity":similarity,"notes":match.get("notes","")})
        if rank[similarity]>rank[strongest]: strongest=similarity
    if strongest=="DIRECT": disposition="NOT_NOVEL_CANDIDATE"
    elif strongest in {"CLOSE","RELATED"}: disposition="NOVELTY_UNRESOLVED"
    else: disposition="NO_MATCH_RECORDED"
    return {"assessment_id":f"PA-{str(uuid4())[:8]}","candidate_statement":candidate_statement.strip(),"queries":search_queries,"matches":normalized,"strongest_match":strongest,"disposition":disposition,"status":"PRIOR_ART_REVIEW","claim_rule":"No recorded match is not proof of novelty; novelty requires adequate external search and review."}
