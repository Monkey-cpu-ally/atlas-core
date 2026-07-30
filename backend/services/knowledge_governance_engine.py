"""Governed Knowledge Bank records for AtlasOS.

This module implements the rules in the ATLAS Knowledge Bank Constitution:
explicit knowledge classes, validation states, provenance, correction history,
supersession, and links to projects and Digital Twins.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


class KnowledgeClass(str, Enum):
    OBSERVATION = "observation"
    QUESTION = "question"
    HYPOTHESIS = "hypothesis"
    EXPLORATORY_SOURCE = "exploratory_source"
    RESEARCH_FINDING = "research_finding"
    ENGINEERING_DECISION = "engineering_decision"
    SPECIFICATION = "specification"
    TEST_EVIDENCE = "test_evidence"
    FAILURE_RECORD = "failure_record"
    VALIDATED_KNOWLEDGE = "validated_knowledge"
    ENGINEERING_STANDARD = "engineering_standard"
    HISTORICAL_ARCHIVE = "historical_archive"


class ValidationStatus(str, Enum):
    DRAFT = "draft"
    EXPLORATORY = "exploratory"
    UNDER_REVIEW = "under_review"
    TESTED = "tested"
    VALIDATED = "validated"
    APPROVED_STANDARD = "approved_standard"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class SourceQuality(str, Enum):
    HIGH_CONFIDENCE = "high_confidence"
    SUPPORTING = "supporting"
    EXPLORATORY = "exploratory"


class KnowledgeSource(BaseModel):
    source_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(min_length=1, max_length=300)
    uri: HttpUrl | None = None
    quality: SourceQuality
    publisher: str | None = Field(default=None, max_length=200)
    published_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=2000)


class ReviewEvent(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid4()))
    reviewer: str = Field(min_length=1, max_length=120)
    action: str = Field(min_length=1, max_length=80)
    notes: str | None = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CorrectionEvent(BaseModel):
    correction_id: str = Field(default_factory=lambda: str(uuid4()))
    original_claim: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    corrected_claim: str = Field(min_length=1)
    evidence_source_ids: list[str] = Field(default_factory=list)
    impacted_project_ids: list[str] = Field(default_factory=list)
    impacted_twin_ids: list[str] = Field(default_factory=list)
    approved_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeRecordCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(min_length=1)
    content: str = Field(min_length=1)
    owning_institute: str = Field(min_length=1, max_length=160)
    owning_ai: str = Field(min_length=1, max_length=80)
    knowledge_class: KnowledgeClass
    validation_status: ValidationStatus = ValidationStatus.DRAFT
    assumptions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    sources: list[KnowledgeSource] = Field(default_factory=list)
    project_ids: list[str] = Field(default_factory=list)
    twin_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    access_classification: str = Field(default="internal", max_length=80)

    @field_validator("validation_status")
    @classmethod
    def prevent_unreviewed_standard(cls, value: ValidationStatus) -> ValidationStatus:
        if value == ValidationStatus.APPROVED_STANDARD:
            raise ValueError("New records cannot begin as an approved standard")
        return value


class KnowledgeRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid4()))
    version: int = 1
    title: str
    summary: str
    content: str
    owning_institute: str
    owning_ai: str
    knowledge_class: KnowledgeClass
    validation_status: ValidationStatus
    assumptions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[KnowledgeSource] = Field(default_factory=list)
    project_ids: list[str] = Field(default_factory=list)
    twin_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    access_classification: str = "internal"
    reviews: list[ReviewEvent] = Field(default_factory=list)
    corrections: list[CorrectionEvent] = Field(default_factory=list)
    supersedes_record_id: str | None = None
    superseded_by_record_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


_db: Any | None = None
_memory: dict[str, KnowledgeRecord] = {}
_COLLECTION = "governed_knowledge_records"


def attach_mongo(db: Any) -> None:
    global _db
    _db = db


async def create_indexes() -> None:
    if _db is None:
        return
    collection = _db[_COLLECTION]
    await collection.create_index("record_id", unique=True)
    await collection.create_index("validation_status")
    await collection.create_index("knowledge_class")
    await collection.create_index("project_ids")
    await collection.create_index("twin_ids")
    await collection.create_index([("title", "text"), ("summary", "text"), ("content", "text")])


def _document(record: KnowledgeRecord) -> dict[str, Any]:
    return record.model_dump(mode="json")


async def _persist(record: KnowledgeRecord) -> None:
    _memory[record.record_id] = record
    if _db is not None:
        await _db[_COLLECTION].replace_one(
            {"record_id": record.record_id}, _document(record), upsert=True
        )


async def hydrate_from_mongo() -> int:
    if _db is None:
        return len(_memory)
    _memory.clear()
    docs = await _db[_COLLECTION].find({}, {"_id": 0}).to_list(10000)
    for doc in docs:
        record = KnowledgeRecord.model_validate(doc)
        _memory[record.record_id] = record
    return len(_memory)


async def create_record(payload: KnowledgeRecordCreate) -> KnowledgeRecord:
    record = KnowledgeRecord(**payload.model_dump())
    await _persist(record)
    return record


async def get_record(record_id: str) -> KnowledgeRecord | None:
    record = _memory.get(record_id)
    if record is not None:
        return record
    if _db is None:
        return None
    doc = await _db[_COLLECTION].find_one({"record_id": record_id}, {"_id": 0})
    if doc is None:
        return None
    record = KnowledgeRecord.model_validate(doc)
    _memory[record_id] = record
    return record


async def list_records(
    *,
    status: ValidationStatus | None = None,
    knowledge_class: KnowledgeClass | None = None,
    project_id: str | None = None,
    twin_id: str | None = None,
    owner: str | None = None,
) -> list[KnowledgeRecord]:
    records = list(_memory.values())
    if _db is not None and not records:
        await hydrate_from_mongo()
        records = list(_memory.values())
    if status:
        records = [r for r in records if r.validation_status == status]
    if knowledge_class:
        records = [r for r in records if r.knowledge_class == knowledge_class]
    if project_id:
        records = [r for r in records if project_id in r.project_ids]
    if twin_id:
        records = [r for r in records if twin_id in r.twin_ids]
    if owner:
        needle = owner.casefold()
        records = [r for r in records if needle in r.owning_ai.casefold() or needle in r.owning_institute.casefold()]
    return sorted(records, key=lambda r: r.updated_at, reverse=True)


async def search_records(query: str) -> list[KnowledgeRecord]:
    needle = query.strip().casefold()
    if not needle:
        return await list_records()
    records = await list_records()
    return [
        record
        for record in records
        if needle in " ".join(
            [record.title, record.summary, record.content, *record.tags]
        ).casefold()
    ]


_ALLOWED_TRANSITIONS: dict[ValidationStatus, set[ValidationStatus]] = {
    ValidationStatus.DRAFT: {ValidationStatus.EXPLORATORY, ValidationStatus.UNDER_REVIEW, ValidationStatus.REJECTED, ValidationStatus.ARCHIVED},
    ValidationStatus.EXPLORATORY: {ValidationStatus.UNDER_REVIEW, ValidationStatus.REJECTED, ValidationStatus.ARCHIVED},
    ValidationStatus.UNDER_REVIEW: {ValidationStatus.TESTED, ValidationStatus.VALIDATED, ValidationStatus.REJECTED, ValidationStatus.DRAFT},
    ValidationStatus.TESTED: {ValidationStatus.VALIDATED, ValidationStatus.UNDER_REVIEW, ValidationStatus.REJECTED},
    ValidationStatus.VALIDATED: {ValidationStatus.APPROVED_STANDARD, ValidationStatus.UNDER_REVIEW, ValidationStatus.SUPERSEDED, ValidationStatus.ARCHIVED},
    ValidationStatus.APPROVED_STANDARD: {ValidationStatus.UNDER_REVIEW, ValidationStatus.SUPERSEDED, ValidationStatus.ARCHIVED},
    ValidationStatus.REJECTED: {ValidationStatus.DRAFT, ValidationStatus.ARCHIVED},
    ValidationStatus.SUPERSEDED: {ValidationStatus.ARCHIVED},
    ValidationStatus.ARCHIVED: set(),
}


async def transition_status(
    record_id: str,
    target: ValidationStatus,
    reviewer: str,
    notes: str | None = None,
) -> KnowledgeRecord:
    record = await get_record(record_id)
    if record is None:
        raise KeyError(record_id)
    if target not in _ALLOWED_TRANSITIONS[record.validation_status]:
        raise ValueError(f"Invalid transition: {record.validation_status.value} -> {target.value}")
    if target in {ValidationStatus.VALIDATED, ValidationStatus.APPROVED_STANDARD} and not record.sources:
        raise ValueError("Validated knowledge and standards require at least one source")
    if target == ValidationStatus.APPROVED_STANDARD and record.confidence < 0.8:
        raise ValueError("Approved standards require confidence of at least 0.80")
    record.validation_status = target
    record.version += 1
    record.updated_at = datetime.now(timezone.utc)
    record.reviews.append(ReviewEvent(reviewer=reviewer, action=f"status:{target.value}", notes=notes))
    await _persist(record)
    return record


async def add_correction(record_id: str, correction: CorrectionEvent) -> KnowledgeRecord:
    record = await get_record(record_id)
    if record is None:
        raise KeyError(record_id)
    record.corrections.append(correction)
    record.version += 1
    record.updated_at = datetime.now(timezone.utc)
    if record.validation_status in {ValidationStatus.VALIDATED, ValidationStatus.APPROVED_STANDARD}:
        record.validation_status = ValidationStatus.UNDER_REVIEW
    await _persist(record)
    return record


async def supersede_record(
    record_id: str,
    replacement: KnowledgeRecordCreate,
    reviewer: str,
    notes: str | None = None,
) -> tuple[KnowledgeRecord, KnowledgeRecord]:
    old = await get_record(record_id)
    if old is None:
        raise KeyError(record_id)
    if old.validation_status not in {ValidationStatus.VALIDATED, ValidationStatus.APPROVED_STANDARD}:
        raise ValueError("Only validated knowledge or approved standards can be superseded")
    new = KnowledgeRecord(**replacement.model_dump(), supersedes_record_id=old.record_id)
    new.reviews.append(ReviewEvent(reviewer=reviewer, action="created_as_replacement", notes=notes))
    old.validation_status = ValidationStatus.SUPERSEDED
    old.superseded_by_record_id = new.record_id
    old.version += 1
    old.updated_at = datetime.now(timezone.utc)
    old.reviews.append(ReviewEvent(reviewer=reviewer, action="superseded", notes=notes))
    await _persist(old)
    await _persist(new)
    return old, new


def governance_health() -> dict[str, Any]:
    records = list(_memory.values())
    return {
        "service": "knowledge-governance",
        "status": "healthy",
        "record_count": len(records),
        "validated_count": sum(r.validation_status in {ValidationStatus.VALIDATED, ValidationStatus.APPROVED_STANDARD} for r in records),
        "unsourced_count": sum(not r.sources for r in records),
        "under_review_count": sum(r.validation_status == ValidationStatus.UNDER_REVIEW for r in records),
        "persistence": "mongodb" if _db is not None else "memory",
    }
