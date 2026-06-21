"""Subjects REST API — Knowledge Bank Phase A.

Mounted at `/api/subjects/*`. Idempotent seeding on startup.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import subjects as subj_svc
from services.subjects import Subject

router = APIRouter(prefix="/api/subjects", tags=["Knowledge Bank · Subjects"])


@router.get("")
async def list_subjects(
    family: Optional[str] = None,
    enabled_only: bool = True,
):
    items = await subj_svc.list_subjects(family=family, enabled_only=enabled_only)
    return {"count": len(items), "items": items}


@router.get("/stats")
async def stats():
    return await subj_svc.stats()


@router.get("/{slug_or_id}")
async def get_subject(slug_or_id: str):
    doc = await subj_svc.get_subject(slug_or_id)
    if not doc:
        raise HTTPException(404, f"subject not found: {slug_or_id}")
    return doc


class UpsertReq(BaseModel):
    slug: str
    name: str
    description: str
    primary_agent: str
    family: str
    accent_color: str = "#00FFC8"
    parent_tags: List[str] = Field(default_factory=list)
    enabled: bool = True


@router.post("")
async def upsert(req: UpsertReq):
    return await subj_svc.upsert(Subject(**req.model_dump()))


@router.post("/seed")
async def seed():
    n = await subj_svc.seed_if_needed()
    all_items = await subj_svc.list_subjects()
    return {"inserted": n, "total": len(all_items)}
