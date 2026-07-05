"""ATLAS Discovery Approval Pipeline.

Quality gate that turns discovery drafts into approved knowledge records through
AI reviews, evidence scoring, and Council decision. V1 is deterministic and
safe: it does not claim truth without an approval record.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services import chronicle_engine, evidence_scoring, knowledge_record_writer

VALID_OWNER_AI = {"Ajani", "Hermes", "Minerva", "Council"}
VALID_RECOMMENDATIONS = {"approve", "needs_more_evidence", "reject", "archive_only"}
VALID_DECISIONS = {"approved", "needs_more_research", "rejected", "archive_only", "future_research_candidate"}

_DRAFTS: Dict[str, Dict[str, Any]] = {}
_REVIEWS: Dict[str, Dict[str, Any]] = {}
_DECISIONS: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class DiscoveryApprovalError(RuntimeError):
    """Raised when discovery approval state is invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_draft(
    *,
    title: str,
    summary: str,
    owner_ai: str = "Council",
    evidence: Optional[List[Dict[str, Any]]] = None,
    source_refs: Optional[List[Dict[str, Any]]] = None,
    related_subjects: Optional[List[str]] = None,
    related_projects: Optional[List[str]] = None,
    mission_id: Optional[str] = None,
) -> Dict[str, Any]:
    if owner_ai not in VALID_OWNER_AI:
        raise DiscoveryApprovalError(f"invalid owner_ai: {owner_ai}")
    draft_id = f"DISC-{str(uuid4())[:8]}"
    score = evidence_scoring.score_evidence(evidence or [])
    draft = {
        "discovery_id": draft_id,
        "title": title,
        "summary": summary,
        "owner_ai": owner_ai,
        "status": "draft",
        "mission_id": mission_id,
        "evidence": evidence or [],
        "source_refs": source_refs or [],
        "evidence_score": score,
        "related_subjects": related_subjects or [],
        "related_projects": related_projects or [],
        "reviews": [],
        "council_decision_id": None,
        "knowledge_record_id": None,
        "chronicle_id": None,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _DRAFTS[draft_id] = draft
    return draft


def get_draft(discovery_id: str) -> Optional[Dict[str, Any]]:
    return _DRAFTS.get(discovery_id)


def list_drafts(status: Optional[str] = None, owner_ai: Optional[str] = None) -> List[Dict[str, Any]]:
    items = list(_DRAFTS.values())
    if status:
        items = [item for item in items if item["status"] == status]
    if owner_ai:
        items = [item for item in items if item["owner_ai"].lower() == owner_ai.lower()]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)


def add_review(
    *,
    discovery_id: str,
    reviewer_ai: str,
    recommendation: str,
    rationale: str,
    confidence_score: int = 50,
) -> Dict[str, Any]:
    draft = get_draft(discovery_id)
    if not draft:
        raise DiscoveryApprovalError(f"unknown discovery_id: {discovery_id}")
    if reviewer_ai not in VALID_OWNER_AI:
        raise DiscoveryApprovalError(f"invalid reviewer_ai: {reviewer_ai}")
    if recommendation not in VALID_RECOMMENDATIONS:
        raise DiscoveryApprovalError(f"invalid recommendation: {recommendation}")
    review_id = f"REV-{str(uuid4())[:8]}"
    review = {
        "review_id": review_id,
        "discovery_id": discovery_id,
        "reviewer_ai": reviewer_ai,
        "recommendation": recommendation,
        "rationale": rationale,
        "confidence_score": max(0, min(100, int(confidence_score))),
        "created_at": _utc_now(),
    }
    _REVIEWS[review_id] = review
    draft["reviews"].append(review)
    draft["status"] = "under_review"
    draft["review_score"] = evidence_scoring.score_reviews(draft["reviews"])
    draft["updated_at"] = _utc_now()
    return review


def council_decide(*, discovery_id: str, decision: str, rationale: str) -> Dict[str, Any]:
    draft = get_draft(discovery_id)
    if not draft:
        raise DiscoveryApprovalError(f"unknown discovery_id: {discovery_id}")
    if decision not in VALID_DECISIONS:
        raise DiscoveryApprovalError(f"invalid decision: {decision}")

    decision_id = f"CD-{str(uuid4())[:8]}"
    review_score = evidence_scoring.score_reviews(draft.get("reviews", []))
    council = {
        "council_decision_id": decision_id,
        "discovery_id": discovery_id,
        "decision": decision,
        "rationale": rationale,
        "evidence_score": draft.get("evidence_score", {}),
        "review_score": review_score,
        "created_at": _utc_now(),
    }
    _DECISIONS[decision_id] = council
    draft["council_decision_id"] = decision_id
    draft["status"] = decision
    draft["updated_at"] = _utc_now()

    if decision == "approved":
        record = knowledge_record_writer.create_record(
            title=draft["title"],
            summary=draft["summary"],
            owner_ai=draft["owner_ai"],
            source_refs=draft.get("source_refs", []),
            evidence_score=draft.get("evidence_score", {}),
            related_subjects=draft.get("related_subjects", []),
            related_projects=draft.get("related_projects", []),
            discovery_id=discovery_id,
            council_decision="approved",
        )
        chronicle = chronicle_engine.create_entry(
            title=f"Knowledge approved: {draft['title']}",
            event_type="knowledge_approved",
            summary=rationale,
            actor="Council",
            related_ids={
                "discovery_id": discovery_id,
                "knowledge_record_id": record["knowledge_record_id"],
                "council_decision_id": decision_id,
            },
            affected_systems=["knowledge_bank", "knowledge_graph", "project_intelligence"],
        )
        draft["knowledge_record_id"] = record["knowledge_record_id"]
        draft["chronicle_id"] = chronicle["chronicle_id"]
        council["knowledge_record"] = record
        council["chronicle_entry"] = chronicle

    return council


async def persist_draft(draft: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.discovery_drafts.update_one({"discovery_id": draft["discovery_id"]}, {"$set": draft}, upsert=True)


async def persist_review(review: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.discovery_reviews.update_one({"review_id": review["review_id"]}, {"$set": review}, upsert=True)


async def persist_decision(decision: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.council_reviews.update_one({"council_decision_id": decision["council_decision_id"]}, {"$set": decision}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"discovery_drafts": 0, "discovery_reviews": 0, "council_reviews": 0}
    drafts = await _DB.discovery_drafts.find({}, {"_id": 0}).to_list(10000)
    reviews = await _DB.discovery_reviews.find({}, {"_id": 0}).to_list(10000)
    decisions = await _DB.council_reviews.find({}, {"_id": 0}).to_list(10000)
    _DRAFTS.clear(); _REVIEWS.clear(); _DECISIONS.clear()
    for draft in drafts:
        _DRAFTS[draft["discovery_id"]] = draft
    for review in reviews:
        _REVIEWS[review["review_id"]] = review
    for decision in decisions:
        _DECISIONS[decision["council_decision_id"]] = decision
    return {"discovery_drafts": len(_DRAFTS), "discovery_reviews": len(_REVIEWS), "council_reviews": len(_DECISIONS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.discovery_drafts.create_index("discovery_id", unique=True)
    await _DB.discovery_drafts.create_index([("owner_ai", 1), ("status", 1)])
    await _DB.discovery_reviews.create_index("review_id", unique=True)
    await _DB.discovery_reviews.create_index("discovery_id")
    await _DB.council_reviews.create_index("council_decision_id", unique=True)
    await _DB.council_reviews.create_index("discovery_id")


def reset_in_memory_state() -> None:
    _DRAFTS.clear(); _REVIEWS.clear(); _DECISIONS.clear()
