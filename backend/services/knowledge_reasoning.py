"""ATLAS Knowledge Reasoning Layer.

Produces auditable engineering decision records from missions, specialist
assessments, evidence references, risks, knowledge gaps and Council consensus.
V1 deliberately stores conclusions and provenance rather than hidden chain of
thought. It can later be connected to retrieval/LLM adapters without changing
the public decision-record contract.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_MISSIONS: Dict[str, Dict[str, Any]] = {}
_ASSESSMENTS: Dict[str, Dict[str, Any]] = {}
_EVIDENCE: Dict[str, Dict[str, Any]] = {}
_RISKS: Dict[str, Dict[str, Any]] = {}
_GAPS: Dict[str, Dict[str, Any]] = {}
_DECISIONS: Dict[str, Dict[str, Any]] = {}

SPECIALISTS = {"Hermes", "Minerva", "Ajani"}
ALL_ACTORS = SPECIALISTS | {"Council", "System"}
MISSION_STATES = {"draft", "researching", "review", "decided", "blocked", "archived"}
EVIDENCE_STATES = {"unverified", "supported", "conflicting", "rejected"}
RISK_LEVELS = {"low", "medium", "high", "critical"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_mission(*, objective: str, domains: List[str], project_id: Optional[str] = None, assumptions: Optional[List[str]] = None) -> Dict[str, Any]:
    mission_id = f"KRM-{str(uuid4())[:8]}"
    now = _now()
    item = {
        "mission_id": mission_id,
        "objective": objective,
        "domains": sorted(set(domains)),
        "project_id": project_id,
        "assumptions": assumptions or [],
        "state": "draft",
        "confidence_score": 0,
        "created_at": now,
        "updated_at": now,
    }
    _MISSIONS[mission_id] = item
    return item


def add_evidence(*, mission_id: str, source_id: str, claim: str, status: str = "unverified", quality_score: int = 50, locator: Optional[str] = None) -> Dict[str, Any]:
    _require_mission(mission_id)
    if status not in EVIDENCE_STATES:
        raise ValueError(f"invalid evidence status: {status}")
    evidence_id = f"KRE-{str(uuid4())[:8]}"
    item = {
        "evidence_id": evidence_id,
        "mission_id": mission_id,
        "source_id": source_id,
        "claim": claim,
        "status": status,
        "quality_score": _score(quality_score),
        "locator": locator,
        "created_at": _now(),
    }
    _EVIDENCE[evidence_id] = item
    _touch(mission_id)
    return item


def add_assessment(*, mission_id: str, specialist: str, conclusion: str, recommendation: str, confidence_score: int, evidence_ids: Optional[List[str]] = None, assumptions: Optional[List[str]] = None) -> Dict[str, Any]:
    _require_mission(mission_id)
    if specialist not in SPECIALISTS:
        raise ValueError(f"invalid specialist: {specialist}")
    evidence_ids = evidence_ids or []
    for eid in evidence_ids:
        evidence = _EVIDENCE.get(eid)
        if not evidence or evidence["mission_id"] != mission_id:
            raise ValueError(f"invalid evidence_id for mission: {eid}")
    assessment_id = f"KRA-{str(uuid4())[:8]}"
    item = {
        "assessment_id": assessment_id,
        "mission_id": mission_id,
        "specialist": specialist,
        "conclusion": conclusion,
        "recommendation": recommendation,
        "confidence_score": _score(confidence_score),
        "evidence_ids": evidence_ids,
        "assumptions": assumptions or [],
        "created_at": _now(),
    }
    _ASSESSMENTS[assessment_id] = item
    _touch(mission_id, state="review")
    return item


def add_risk(*, mission_id: str, title: str, level: str, probability_score: int, impact_score: int, mitigation: str, owner_ai: str = "Council") -> Dict[str, Any]:
    _require_mission(mission_id)
    if level not in RISK_LEVELS:
        raise ValueError(f"invalid risk level: {level}")
    if owner_ai not in ALL_ACTORS:
        raise ValueError(f"invalid owner_ai: {owner_ai}")
    risk_id = f"KRR-{str(uuid4())[:8]}"
    probability = _score(probability_score)
    impact = _score(impact_score)
    item = {
        "risk_id": risk_id,
        "mission_id": mission_id,
        "title": title,
        "level": level,
        "probability_score": probability,
        "impact_score": impact,
        "priority_score": round((probability * impact) / 100),
        "mitigation": mitigation,
        "owner_ai": owner_ai,
        "created_at": _now(),
    }
    _RISKS[risk_id] = item
    _touch(mission_id)
    return item


def add_gap(*, mission_id: str, question: str, reason: str, required_domains: Optional[List[str]] = None, blocking: bool = False) -> Dict[str, Any]:
    _require_mission(mission_id)
    gap_id = f"KRG-{str(uuid4())[:8]}"
    item = {
        "gap_id": gap_id,
        "mission_id": mission_id,
        "question": question,
        "reason": reason,
        "required_domains": sorted(set(required_domains or [])),
        "blocking": bool(blocking),
        "resolved": False,
        "created_at": _now(),
    }
    _GAPS[gap_id] = item
    _touch(mission_id, state="blocked" if blocking else "researching")
    return item


def resolve_gap(gap_id: str) -> Dict[str, Any]:
    item = _GAPS.get(gap_id)
    if not item:
        raise ValueError(f"unknown gap_id: {gap_id}")
    item["resolved"] = True
    item["resolved_at"] = _now()
    _touch(item["mission_id"])
    return item


def council_decision(*, mission_id: str, recommendation: str, rationale_summary: str, selected_assessment_ids: Optional[List[str]] = None, dissent_notes: Optional[List[str]] = None) -> Dict[str, Any]:
    mission = _require_mission(mission_id)
    selected = selected_assessment_ids or [a["assessment_id"] for a in _ASSESSMENTS.values() if a["mission_id"] == mission_id]
    assessments = []
    for aid in selected:
        item = _ASSESSMENTS.get(aid)
        if not item or item["mission_id"] != mission_id:
            raise ValueError(f"invalid assessment_id for mission: {aid}")
        assessments.append(item)
    confidence = _calculate_confidence(mission_id, assessments)
    blocking_gaps = [g for g in _GAPS.values() if g["mission_id"] == mission_id and g["blocking"] and not g["resolved"]]
    state = "blocked" if blocking_gaps else "decided"
    decision_id = f"KRD-{str(uuid4())[:8]}"
    item = {
        "decision_id": decision_id,
        "mission_id": mission_id,
        "recommendation": recommendation,
        "rationale_summary": rationale_summary,
        "selected_assessment_ids": selected,
        "dissent_notes": dissent_notes or [],
        "confidence_score": confidence,
        "blocking_gap_ids": [g["gap_id"] for g in blocking_gaps],
        "state": state,
        "created_at": _now(),
    }
    _DECISIONS[decision_id] = item
    mission["confidence_score"] = confidence
    _touch(mission_id, state=state)
    return item


def mission_detail(mission_id: str) -> Dict[str, Any]:
    mission = _require_mission(mission_id)
    return {
        "mission": mission,
        "evidence": _for_mission(_EVIDENCE, mission_id),
        "assessments": _for_mission(_ASSESSMENTS, mission_id),
        "risks": sorted(_for_mission(_RISKS, mission_id), key=lambda x: x["priority_score"], reverse=True),
        "knowledge_gaps": _for_mission(_GAPS, mission_id),
        "decisions": _for_mission(_DECISIONS, mission_id),
    }


def list_missions(*, state: Optional[str] = None, project_id: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    items = list(_MISSIONS.values())
    if state:
        items = [x for x in items if x["state"] == state]
    if project_id:
        items = [x for x in items if x.get("project_id") == project_id]
    return sorted(items, key=lambda x: x["updated_at"], reverse=True)[:limit]


def summary() -> Dict[str, Any]:
    return {
        "title": "ATLAS Knowledge Reasoning Layer",
        "generated_at": _now(),
        "mission_count": len(_MISSIONS),
        "assessment_count": len(_ASSESSMENTS),
        "evidence_count": len(_EVIDENCE),
        "risk_count": len(_RISKS),
        "knowledge_gap_count": len(_GAPS),
        "decision_count": len(_DECISIONS),
        "blocked_missions": len([x for x in _MISSIONS.values() if x["state"] == "blocked"]),
    }


def seed_foundation_mission() -> Dict[str, Any]:
    mission = create_mission(objective="Demonstrate auditable multi-specialist engineering review.", domains=["Robotics", "Manufacturing", "Safety"], project_id="project:weaver")
    evidence = add_evidence(mission_id=mission["mission_id"], source_id="source:nist", claim="Engineering recommendations should be grounded in traceable standards and test evidence.", status="supported", quality_score=90)
    h = add_assessment(mission_id=mission["mission_id"], specialist="Hermes", conclusion="Architecture should prioritize modularity and testability.", recommendation="Use modular subsystem boundaries and measurable acceptance tests.", confidence_score=85, evidence_ids=[evidence["evidence_id"]])
    m = add_assessment(mission_id=mission["mission_id"], specialist="Minerva", conclusion="Environmental and human context should be included in system review.", recommendation="Add lifecycle and operator-impact checks to design reviews.", confidence_score=75, evidence_ids=[evidence["evidence_id"]])
    a = add_assessment(mission_id=mission["mission_id"], specialist="Ajani", conclusion="Risk ownership and staged validation reduce program uncertainty.", recommendation="Gate progression on explicit risk retirement criteria.", confidence_score=80, evidence_ids=[evidence["evidence_id"]])
    add_risk(mission_id=mission["mission_id"], title="Insufficient validation evidence", level="high", probability_score=55, impact_score=85, mitigation="Require test evidence before advancing maturity gates.")
    decision = council_decision(mission_id=mission["mission_id"], recommendation="Proceed with a modular, evidence-gated engineering workflow.", rationale_summary="All three specialist assessments support staged validation, traceability, and explicit risk management.", selected_assessment_ids=[h["assessment_id"], m["assessment_id"], a["assessment_id"]])
    return {"mission": mission, "decision": decision}


def reset_in_memory_state() -> None:
    _MISSIONS.clear(); _ASSESSMENTS.clear(); _EVIDENCE.clear(); _RISKS.clear(); _GAPS.clear(); _DECISIONS.clear()


async def persist_all() -> None:
    if _DB is None:
        return
    specs = [
        ("reasoning_missions", _MISSIONS, "mission_id"),
        ("reasoning_assessments", _ASSESSMENTS, "assessment_id"),
        ("reasoning_evidence", _EVIDENCE, "evidence_id"),
        ("reasoning_risks", _RISKS, "risk_id"),
        ("reasoning_gaps", _GAPS, "gap_id"),
        ("reasoning_decisions", _DECISIONS, "decision_id"),
    ]
    for collection_name, store, key in specs:
        collection = getattr(_DB, collection_name)
        for item in store.values():
            await collection.update_one({key: item[key]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"reasoning_missions": 0, "reasoning_decisions": 0}
    reset_in_memory_state()
    specs = [
        ("reasoning_missions", _MISSIONS, "mission_id"),
        ("reasoning_assessments", _ASSESSMENTS, "assessment_id"),
        ("reasoning_evidence", _EVIDENCE, "evidence_id"),
        ("reasoning_risks", _RISKS, "risk_id"),
        ("reasoning_gaps", _GAPS, "gap_id"),
        ("reasoning_decisions", _DECISIONS, "decision_id"),
    ]
    for collection_name, store, key in specs:
        collection = getattr(_DB, collection_name)
        for item in await collection.find({}, {"_id": 0}).to_list(100000):
            store[item[key]] = item
    return {"reasoning_missions": len(_MISSIONS), "reasoning_decisions": len(_DECISIONS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.reasoning_missions.create_index("mission_id", unique=True)
    await _DB.reasoning_missions.create_index("project_id")
    await _DB.reasoning_missions.create_index("state")
    for collection_name, key in [("reasoning_assessments", "assessment_id"), ("reasoning_evidence", "evidence_id"), ("reasoning_risks", "risk_id"), ("reasoning_gaps", "gap_id"), ("reasoning_decisions", "decision_id")]:
        collection = getattr(_DB, collection_name)
        await collection.create_index(key, unique=True)
        await collection.create_index("mission_id")


def _require_mission(mission_id: str) -> Dict[str, Any]:
    item = _MISSIONS.get(mission_id)
    if not item:
        raise ValueError(f"unknown mission_id: {mission_id}")
    return item


def _touch(mission_id: str, state: Optional[str] = None) -> None:
    item = _require_mission(mission_id)
    if state:
        if state not in MISSION_STATES:
            raise ValueError(f"invalid mission state: {state}")
        item["state"] = state
    item["updated_at"] = _now()


def _for_mission(store: Dict[str, Dict[str, Any]], mission_id: str) -> List[Dict[str, Any]]:
    return [x for x in store.values() if x["mission_id"] == mission_id]


def _score(value: int) -> int:
    return max(0, min(100, int(value)))


def _calculate_confidence(mission_id: str, assessments: List[Dict[str, Any]]) -> int:
    assessment_score = sum(a["confidence_score"] for a in assessments) / len(assessments) if assessments else 0
    evidence = _for_mission(_EVIDENCE, mission_id)
    supported = [e for e in evidence if e["status"] == "supported"]
    evidence_score = sum(e["quality_score"] for e in supported) / len(supported) if supported else 0
    conflicting = len([e for e in evidence if e["status"] == "conflicting"])
    unresolved_blockers = len([g for g in _GAPS.values() if g["mission_id"] == mission_id and g["blocking"] and not g["resolved"]])
    raw = (assessment_score * 0.55) + (evidence_score * 0.45) - (conflicting * 8) - (unresolved_blockers * 15)
    return _score(round(raw))
