"""Canonical ATLAS Discovery Engine.

Owns the pre-approval discovery lifecycle. It maps frontier/unknown questions,
records falsifiable hypotheses, prior art, evidence and experiments, and hands
mature candidates to the existing Discovery Approval Pipeline. It never treats
a hypothesis, simulation, analogy, or novelty score as established truth.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services import discovery_approval_pipeline as approval
from services import evidence_scoring

LAYERS = {"FOUNDATION", "FRONTIER", "UNKNOWN"}
STATUSES = {
    "CONCEPT", "HYPOTHESIS", "PRIOR_ART_CHECKED", "TEST_DESIGNED", "SIMULATED",
    "EXPERIMENTALLY_SUPPORTED", "REPLICATED", "INDEPENDENTLY_VERIFIED", "INVALIDATED",
    "INCONCLUSIVE", "BLOCKED_BY_EVIDENCE", "BLOCKED_BY_SAFETY", "BLOCKED_BY_CAPABILITY", "NOT_NOVEL",
}
PROMOTABLE_STATUSES = {
    "PRIOR_ART_CHECKED", "TEST_DESIGNED", "SIMULATED", "EXPERIMENTALLY_SUPPORTED",
    "REPLICATED", "INDEPENDENTLY_VERIFIED",
}

_RECORDS: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class DiscoveryEngineError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_investigation(*, title: str, question: str, knowledge_layer: str = "FRONTIER", owner_ai: str = "Council", subjects: Optional[List[str]] = None, related_projects: Optional[List[str]] = None, mission_id: Optional[str] = None) -> Dict[str, Any]:
    layer = knowledge_layer.upper()
    if layer not in LAYERS:
        raise DiscoveryEngineError(f"invalid knowledge_layer: {knowledge_layer}")
    if owner_ai not in approval.VALID_OWNER_AI:
        raise DiscoveryEngineError(f"invalid owner_ai: {owner_ai}")
    if not title.strip() or not question.strip():
        raise DiscoveryEngineError("title and question are required")
    investigation_id = f"DX-{str(uuid4())[:8]}"
    record = {
        "investigation_id": investigation_id, "title": title.strip(), "question": question.strip(),
        "knowledge_layer": layer, "owner_ai": owner_ai, "status": "CONCEPT", "subjects": subjects or [],
        "related_projects": related_projects or [], "mission_id": mission_id, "known_facts": [], "unknowns": [],
        "assumptions": [], "analogies": [], "candidate_hypotheses": [], "hypotheses": [], "prior_art": [], "evidence": [],
        "evidence_score": evidence_scoring.score_evidence([]), "experiment_plan": None, "results": [],
        "approval_discovery_id": None, "created_at": _now(), "updated_at": _now(),
    }
    _RECORDS[investigation_id] = record
    return record


def get_investigation(investigation_id: str) -> Optional[Dict[str, Any]]:
    return _RECORDS.get(investigation_id)


def list_investigations(*, status: Optional[str] = None, knowledge_layer: Optional[str] = None) -> List[Dict[str, Any]]:
    items = list(_RECORDS.values())
    if status:
        items = [item for item in items if item["status"] == status.upper()]
    if knowledge_layer:
        items = [item for item in items if item["knowledge_layer"] == knowledge_layer.upper()]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)


def map_frontier(*, subjects: Optional[List[str]] = None) -> Dict[str, Any]:
    wanted = {s.casefold() for s in (subjects or [])}
    records = list(_RECORDS.values())
    if wanted:
        records = [r for r in records if wanted.intersection({s.casefold() for s in r.get("subjects", [])})]
    layers = {layer: [] for layer in sorted(LAYERS)}
    for record in records:
        layers[record["knowledge_layer"]].append({
            "investigation_id": record["investigation_id"], "title": record["title"], "question": record["question"],
            "status": record["status"], "subjects": record.get("subjects", []),
            "evidence_score": record.get("evidence_score", {}).get("score", 0),
        })
    return {"generated_at": _now(), "scope_subjects": subjects or [], "layers": layers,
            "counts": {layer: len(items) for layer, items in layers.items()},
            "rule": "FRONTIER and UNKNOWN are ATLAS tracking labels, not claims that the literature contains no answer."}


def detect_gaps(investigation_id: str) -> Dict[str, Any]:
    record = _require(investigation_id); gaps: List[Dict[str, str]] = []
    if not record.get("known_facts"): gaps.append({"kind":"foundation","severity":"medium","message":"No known facts have been recorded."})
    if not record.get("unknowns"): gaps.append({"kind":"question_decomposition","severity":"medium","message":"The main question has not been decomposed into explicit unknowns."})
    if not record.get("hypotheses"): gaps.append({"kind":"hypothesis","severity":"high","message":"No accepted falsifiable hypothesis exists."})
    if not record.get("prior_art"): gaps.append({"kind":"prior_art","severity":"high","message":"No prior-art or literature items are recorded."})
    if record.get("evidence_score", {}).get("score", 0) < 60: gaps.append({"kind":"evidence","severity":"high","message":"Evidence score is below the moderate threshold of 60."})
    if not record.get("experiment_plan"): gaps.append({"kind":"experiment","severity":"high","message":"No measurable experiment or simulation plan exists."})
    if record.get("status") == "SIMULATED": gaps.append({"kind":"physical_validation","severity":"high","message":"Simulation has not established physical or independent verification."})
    if record.get("status") in {"EXPERIMENTALLY_SUPPORTED", "REPLICATED"}: gaps.append({"kind":"independent_verification","severity":"medium","message":"Independent verification has not been recorded."})
    return {"investigation_id":investigation_id,"status":record["status"],"gap_count":len(gaps),"gaps":gaps,
            "ready_for_approval_review":record["status"] in PROMOTABLE_STATUSES and bool(record.get("hypotheses")),
            "ready_for_verified_claim":record["status"] == "INDEPENDENTLY_VERIFIED","generated_at":_now()}


def add_analogy(investigation_id: str, *, source_subject: str, target_subject: str, source_concept: str, mechanism: str, transferable_principle: str, constraints: List[str], source_refs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Record a cross-disciplinary analogy without claiming feasibility."""
    record = _require(investigation_id)
    required = [source_subject, target_subject, source_concept, mechanism, transferable_principle]
    if any(not value.strip() for value in required):
        raise DiscoveryEngineError("analogy requires source/target subjects, source concept, mechanism, and transferable principle")
    if source_subject.casefold() == target_subject.casefold():
        raise DiscoveryEngineError("cross-disciplinary analogy requires different source and target subjects")
    analogy = {"analogy_id":f"ANA-{str(uuid4())[:8]}","source_subject":source_subject.strip(),"target_subject":target_subject.strip(),
               "source_concept":source_concept.strip(),"mechanism":mechanism.strip(),"transferable_principle":transferable_principle.strip(),
               "constraints":constraints,"source_refs":source_refs or [],"status":"candidate","proves_feasibility":False,"created_at":_now()}
    record.setdefault("analogies", []).append(analogy); record["updated_at"] = _now(); return analogy


def generate_candidate_hypothesis(investigation_id: str, *, analogy_id: str, statement: str, rationale: str, assumptions: List[str], falsification_criteria: List[str], expected_observations: List[str], target_measurements: List[str]) -> Dict[str, Any]:
    """Create a reviewable candidate. It is not an active hypothesis until accepted."""
    record = _require(investigation_id)
    analogy = next((item for item in record.get("analogies", []) if item["analogy_id"] == analogy_id), None)
    if not analogy: raise DiscoveryEngineError(f"unknown analogy_id: {analogy_id}")
    if not statement.strip() or not rationale.strip() or not falsification_criteria or not target_measurements:
        raise DiscoveryEngineError("candidate hypothesis requires statement, rationale, falsification criteria, and target measurements")
    candidate = {"candidate_id":f"CHY-{str(uuid4())[:8]}","analogy_id":analogy_id,"statement":statement.strip(),"rationale":rationale.strip(),
                 "assumptions":assumptions,"falsification_criteria":falsification_criteria,"expected_observations":expected_observations,
                 "target_measurements":target_measurements,"status":"pending_review","origin":"structured_candidate","created_at":_now()}
    record.setdefault("candidate_hypotheses", []).append(candidate); record["updated_at"] = _now(); return candidate


def accept_candidate_hypothesis(investigation_id: str, candidate_id: str) -> Dict[str, Any]:
    record = _require(investigation_id)
    candidate = next((item for item in record.get("candidate_hypotheses", []) if item["candidate_id"] == candidate_id), None)
    if not candidate: raise DiscoveryEngineError(f"unknown candidate_id: {candidate_id}")
    if candidate["status"] != "pending_review": raise DiscoveryEngineError(f"candidate is already {candidate['status']}")
    hypothesis = add_hypothesis(investigation_id, statement=candidate["statement"], rationale=candidate["rationale"],
                                falsification_criteria=candidate["falsification_criteria"], assumptions=candidate["assumptions"])
    hypothesis["origin_candidate_id"] = candidate_id; hypothesis["analogy_id"] = candidate["analogy_id"]
    candidate["status"] = "accepted"; candidate["accepted_hypothesis_id"] = hypothesis["hypothesis_id"]; candidate["reviewed_at"] = _now()
    return hypothesis


def add_hypothesis(investigation_id: str, *, statement: str, rationale: str, falsification_criteria: List[str], assumptions: Optional[List[str]] = None) -> Dict[str, Any]:
    record = _require(investigation_id)
    if not falsification_criteria: raise DiscoveryEngineError("a hypothesis requires falsification criteria")
    hypothesis = {"hypothesis_id":f"HYP-{str(uuid4())[:8]}","statement":statement.strip(),"rationale":rationale.strip(),"falsification_criteria":falsification_criteria,"assumptions":assumptions or [],"status":"active","created_at":_now()}
    record["hypotheses"].append(hypothesis); record["status"]="HYPOTHESIS"; record["updated_at"]=_now(); return hypothesis


def add_prior_art(investigation_id: str, *, items: List[Dict[str, Any]], conclusion: str) -> Dict[str, Any]:
    record=_require(investigation_id); record["prior_art"].extend(items); record["prior_art_conclusion"]=conclusion.strip(); record["status"]="PRIOR_ART_CHECKED"; record["updated_at"]=_now(); return record


def add_evidence(investigation_id: str, *, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    record=_require(investigation_id); record["evidence"].extend(evidence); record["evidence_score"]=evidence_scoring.score_evidence(record["evidence"]); record["updated_at"]=_now(); return record


def set_experiment_plan(investigation_id: str, *, objective: str, method: List[str], measurements: List[str], pass_fail_criteria: List[str], safety_constraints: Optional[List[str]] = None) -> Dict[str, Any]:
    record=_require(investigation_id)
    if not method or not measurements or not pass_fail_criteria: raise DiscoveryEngineError("experiment plan requires method, measurements, and pass/fail criteria")
    record["experiment_plan"]={"objective":objective.strip(),"method":method,"measurements":measurements,"pass_fail_criteria":pass_fail_criteria,"safety_constraints":safety_constraints or [],"created_at":_now()}
    record["status"]="TEST_DESIGNED"; record["updated_at"]=_now(); return record


def record_result(investigation_id: str, *, result_type: str, summary: str, measurements: Optional[Dict[str, Any]] = None, resulting_status: str) -> Dict[str, Any]:
    record=_require(investigation_id); status=resulting_status.upper()
    if status not in STATUSES: raise DiscoveryEngineError(f"invalid resulting_status: {resulting_status}")
    if status in {"SIMULATED","EXPERIMENTALLY_SUPPORTED","REPLICATED","INDEPENDENTLY_VERIFIED"} and not record.get("experiment_plan"): raise DiscoveryEngineError("validated result states require an experiment plan")
    result={"result_id":f"RES-{str(uuid4())[:8]}","result_type":result_type,"summary":summary,"measurements":measurements or {},"status":status,"created_at":_now()}
    record["results"].append(result); record["status"]=status; record["updated_at"]=_now(); return result


def promote_to_approval(investigation_id: str) -> Dict[str, Any]:
    record=_require(investigation_id)
    if record["status"] not in PROMOTABLE_STATUSES: raise DiscoveryEngineError(f"status {record['status']} is not ready for approval review")
    if not record["hypotheses"]: raise DiscoveryEngineError("at least one hypothesis is required before approval review")
    if record.get("approval_discovery_id"):
        existing=approval.get_draft(record["approval_discovery_id"])
        if existing: return existing
    draft=approval.create_draft(title=record["title"],summary=record["question"],owner_ai=record["owner_ai"],evidence=record["evidence"],source_refs=[item for item in record["prior_art"] if isinstance(item,dict)],related_subjects=record["subjects"],related_projects=record["related_projects"],mission_id=record["mission_id"])
    draft["discovery_engine_investigation_id"]=investigation_id; draft["discovery_engine_status"]=record["status"]
    record["approval_discovery_id"]=draft["discovery_id"]; record["updated_at"]=_now(); return draft


def _require(investigation_id: str) -> Dict[str, Any]:
    record=get_investigation(investigation_id)
    if not record: raise DiscoveryEngineError(f"unknown investigation_id: {investigation_id}")
    return record


async def persist(record: Dict[str, Any]) -> None:
    if _DB is not None: await _DB.discovery_investigations.update_one({"investigation_id":record["investigation_id"]},{"$set":record},upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None: return {"investigations":0}
    items=await _DB.discovery_investigations.find({}, {"_id":0}).to_list(10000); _RECORDS.clear()
    for item in items:
        item.setdefault("analogies", []); item.setdefault("candidate_hypotheses", []); _RECORDS[item["investigation_id"]]=item
    return {"investigations":len(_RECORDS)}


async def create_indexes() -> None:
    if _DB is not None:
        await _DB.discovery_investigations.create_index("investigation_id",unique=True)
        await _DB.discovery_investigations.create_index([("knowledge_layer",1),("status",1)])
        await _DB.discovery_investigations.create_index("mission_id")


def reset_in_memory_state() -> None:
    _RECORDS.clear()
