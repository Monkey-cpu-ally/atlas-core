"""Knowledge Bank governance API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import knowledge_governance_engine as engine


router = APIRouter(prefix="/api/knowledge-governance", tags=["Knowledge Governance"])


class StatusTransitionRequest(BaseModel):
    target: engine.ValidationStatus
    reviewer: str = Field(min_length=1, max_length=120)
    notes: str | None = Field(default=None, max_length=2000)


class SupersedeRequest(BaseModel):
    replacement: engine.KnowledgeRecordCreate
    reviewer: str = Field(min_length=1, max_length=120)
    notes: str | None = Field(default=None, max_length=2000)


@router.get("/health")
async def health():
    return engine.governance_health()


@router.post("/records", response_model=engine.KnowledgeRecord, status_code=201)
async def create_record(payload: engine.KnowledgeRecordCreate):
    return await engine.create_record(payload)


@router.get("/records", response_model=list[engine.KnowledgeRecord])
async def list_records(
    status: engine.ValidationStatus | None = None,
    knowledge_class: engine.KnowledgeClass | None = None,
    project_id: str | None = None,
    twin_id: str | None = None,
    owner: str | None = None,
):
    return await engine.list_records(
        status=status,
        knowledge_class=knowledge_class,
        project_id=project_id,
        twin_id=twin_id,
        owner=owner,
    )


@router.get("/records/search", response_model=list[engine.KnowledgeRecord])
async def search_records(q: str = Query(min_length=1, max_length=300)):
    return await engine.search_records(q)


@router.get("/records/{record_id}", response_model=engine.KnowledgeRecord)
async def get_record(record_id: str):
    record = await engine.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Knowledge record not found")
    return record


@router.post("/records/{record_id}/status", response_model=engine.KnowledgeRecord)
async def transition_status(record_id: str, payload: StatusTransitionRequest):
    try:
        return await engine.transition_status(
            record_id=record_id,
            target=payload.target,
            reviewer=payload.reviewer,
            notes=payload.notes,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Knowledge record not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/records/{record_id}/corrections", response_model=engine.KnowledgeRecord)
async def add_correction(record_id: str, payload: engine.CorrectionEvent):
    try:
        return await engine.add_correction(record_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Knowledge record not found")


@router.post("/records/{record_id}/supersede")
async def supersede_record(record_id: str, payload: SupersedeRequest):
    try:
        old, new = await engine.supersede_record(
            record_id=record_id,
            replacement=payload.replacement,
            reviewer=payload.reviewer,
            notes=payload.notes,
        )
        return {"superseded": old, "replacement": new}
    except KeyError:
        raise HTTPException(status_code=404, detail="Knowledge record not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
