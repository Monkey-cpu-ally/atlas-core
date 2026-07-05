"""ATLAS Discovery Approval routes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import chronicle_engine, discovery_approval_pipeline as dap, knowledge_record_writer

router = APIRouter(prefix="/api/discovery-approval", tags=["ATLAS Discovery Approval"])


class DraftRequest(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    summary: str = Field(min_length=10, max_length=5000)
    owner_ai: str = "Council"
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    source_refs: List[Dict[str, Any]] = Field(default_factory=list)
    related_subjects: List[str] = Field(default_factory=list)
    related_projects: List[str] = Field(default_factory=list)
    mission_id: Optional[str] = None


class ReviewRequest(BaseModel):
    reviewer_ai: str
    recommendation: str
    rationale: str = Field(min_length=3, max_length=5000)
    confidence_score: int = Field(default=50, ge=0, le=100)


class CouncilDecisionRequest(BaseModel):
    decision: str
    rationale: str = Field(min_length=3, max_length=5000)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "discovery_approval_pipeline",
        "persistence_enabled": dap.persistence_enabled(),
        "drafts": len(dap.list_drafts()),
    }


@router.post("/drafts")
async def create_draft(req: DraftRequest):
    try:
        draft = dap.create_draft(**req.model_dump())
        await dap.persist_draft(draft)
        return draft
    except dap.DiscoveryApprovalError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/drafts")
async def list_drafts(status: Optional[str] = None, owner_ai: Optional[str] = None):
    items = dap.list_drafts(status=status, owner_ai=owner_ai)
    return {"count": len(items), "items": items}


@router.get("/drafts/{discovery_id}")
async def get_draft(discovery_id: str):
    draft = dap.get_draft(discovery_id)
    if not draft:
        raise HTTPException(404, f"discovery not found: {discovery_id}")
    return draft


@router.post("/drafts/{discovery_id}/reviews")
async def add_review(discovery_id: str, req: ReviewRequest):
    try:
        review = dap.add_review(discovery_id=discovery_id, **req.model_dump())
        draft = dap.get_draft(discovery_id)
        await dap.persist_review(review)
        if draft:
            await dap.persist_draft(draft)
        return review
    except dap.DiscoveryApprovalError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/drafts/{discovery_id}/council-decision")
async def council_decision(discovery_id: str, req: CouncilDecisionRequest):
    try:
        decision = dap.council_decide(discovery_id=discovery_id, **req.model_dump())
        draft = dap.get_draft(discovery_id)
        await dap.persist_decision(decision)
        if draft:
            await dap.persist_draft(draft)
        if decision.get("knowledge_record"):
            await knowledge_record_writer.persist_record(decision["knowledge_record"])
        if decision.get("chronicle_entry"):
            await chronicle_engine.persist_entry(decision["chronicle_entry"])
        return decision
    except dap.DiscoveryApprovalError as exc:
        raise HTTPException(422, str(exc)) from exc
