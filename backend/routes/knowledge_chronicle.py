"""ATLAS Knowledge Chronicle routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import knowledge_chronicle

router = APIRouter(prefix="/api/knowledge-chronicle", tags=["ATLAS Knowledge Chronicle"])


class KnowledgeRecordRequest(BaseModel):
    title: str = Field(min_length=3, max_length=250)
    claim: str = Field(min_length=10, max_length=5000)
    source_name: str = Field(min_length=2, max_length=250)
    source_type: str = Field(min_length=2, max_length=120)
    evidence_level: str
    confidence_score: int = Field(ge=0, le=100)
    ai_owner: str
    project_ids: List[str] = Field(default_factory=list)
    technology_ids: List[str] = Field(default_factory=list)
    institution_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    review_status: str = "draft"


class ReviewStatusRequest(BaseModel):
    review_status: str
    reviewer: str = Field(min_length=2, max_length=120)
    note: str = Field(min_length=3, max_length=1000)


class ReviseRecordRequest(BaseModel):
    claim: str = Field(min_length=10, max_length=5000)
    note: str = Field(min_length=3, max_length=1000)
    reviewer: str = Field(min_length=2, max_length=120)
    confidence_score: Optional[int] = Field(default=None, ge=0, le=100)


class ContradictionRequest(BaseModel):
    conflicting_record_id: str
    note: str = Field(min_length=3, max_length=1000)
    reviewer: str = Field(min_length=2, max_length=120)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "knowledge_chronicle",
        "persistence_enabled": knowledge_chronicle.persistence_enabled(),
        "registered_records": knowledge_chronicle.chronicle_summary()["record_count"],
    }


@router.post("/seed")
async def seed_foundation_records():
    result = knowledge_chronicle.seed_foundation_records()
    await knowledge_chronicle.persist_records(result["items"])
    await knowledge_chronicle.persist_events(knowledge_chronicle.list_events(limit=10000))
    return {"created_or_updated": result["created_or_updated"], "summary": knowledge_chronicle.chronicle_summary()}


@router.get("/summary")
async def summary():
    return knowledge_chronicle.chronicle_summary()


@router.post("/records")
async def create_record(req: KnowledgeRecordRequest):
    try:
        record = knowledge_chronicle.create_record(**req.model_dump())
        await knowledge_chronicle.persist_records([record])
        await knowledge_chronicle.persist_events(knowledge_chronicle.list_events(record_id=record["record_id"], limit=100))
        return record
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/records")
async def list_records(
    project_id: Optional[str] = None,
    technology_id: Optional[str] = None,
    institution_id: Optional[str] = None,
    ai_owner: Optional[str] = None,
    review_status: Optional[str] = None,
    evidence_level: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 250,
):
    items = knowledge_chronicle.list_records(
        project_id=project_id,
        technology_id=technology_id,
        institution_id=institution_id,
        ai_owner=ai_owner,
        review_status=review_status,
        evidence_level=evidence_level,
        tag=tag,
        limit=limit,
    )
    return {"count": len(items), "items": items}


@router.get("/records/{record_id}")
async def get_record(record_id: str):
    item = knowledge_chronicle.get_record(record_id)
    if not item:
        raise HTTPException(404, f"record not found: {record_id}")
    return item


@router.post("/records/{record_id}/review-status")
async def update_review_status(record_id: str, req: ReviewStatusRequest):
    try:
        record = knowledge_chronicle.update_review_status(record_id=record_id, **req.model_dump())
        await knowledge_chronicle.persist_records([record])
        await knowledge_chronicle.persist_events(knowledge_chronicle.list_events(record_id=record_id, limit=100))
        return record
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/records/{record_id}/revise")
async def revise_record(record_id: str, req: ReviseRecordRequest):
    try:
        record = knowledge_chronicle.revise_record(record_id=record_id, **req.model_dump())
        await knowledge_chronicle.persist_records([record])
        await knowledge_chronicle.persist_events(knowledge_chronicle.list_events(record_id=record_id, limit=100))
        return record
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/records/{record_id}/contradiction")
async def flag_contradiction(record_id: str, req: ContradictionRequest):
    try:
        record = knowledge_chronicle.flag_contradiction(record_id=record_id, **req.model_dump())
        await knowledge_chronicle.persist_records([record])
        await knowledge_chronicle.persist_events(knowledge_chronicle.list_events(record_id=record_id, limit=100))
        return record
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/events")
async def list_events(record_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 250):
    items = knowledge_chronicle.list_events(record_id=record_id, event_type=event_type, limit=limit)
    return {"count": len(items), "items": items}
