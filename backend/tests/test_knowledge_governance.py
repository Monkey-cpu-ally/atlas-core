"""Unit tests for the governed Knowledge Bank engine."""
from __future__ import annotations

import asyncio

import pytest

from services import knowledge_governance_engine as engine


def run(coro):
    return asyncio.run(coro)


def make_payload(**overrides):
    data = {
        "title": "Weaver actuator test",
        "summary": "Bench test evidence for a Weaver actuator.",
        "content": "The actuator completed the defined duty cycle.",
        "owning_institute": "Hermes Engineering Complex",
        "owning_ai": "Hermes",
        "knowledge_class": engine.KnowledgeClass.TEST_EVIDENCE,
        "validation_status": engine.ValidationStatus.DRAFT,
        "confidence": 0.9,
        "sources": [
            engine.KnowledgeSource(
                title="ATLAS bench test log",
                quality=engine.SourceQuality.HIGH_CONFIDENCE,
            )
        ],
        "project_ids": ["project-weaver"],
        "twin_ids": ["twin-weaver-actuator"],
        "tags": ["weaver", "actuator"],
    }
    data.update(overrides)
    return engine.KnowledgeRecordCreate(**data)


def setup_function():
    engine._memory.clear()
    engine._db = None


def test_new_record_cannot_start_as_approved_standard():
    with pytest.raises(ValueError):
        make_payload(validation_status=engine.ValidationStatus.APPROVED_STANDARD)


def test_record_creation_preserves_project_and_twin_links():
    record = run(engine.create_record(make_payload()))

    assert record.project_ids == ["project-weaver"]
    assert record.twin_ids == ["twin-weaver-actuator"]
    assert record.version == 1


def test_invalid_status_jump_is_rejected():
    record = run(engine.create_record(make_payload()))

    with pytest.raises(ValueError, match="Invalid transition"):
        run(
            engine.transition_status(
                record.record_id,
                engine.ValidationStatus.APPROVED_STANDARD,
                reviewer="Council",
            )
        )


def test_valid_review_path_reaches_validated():
    record = run(engine.create_record(make_payload()))

    record = run(
        engine.transition_status(
            record.record_id,
            engine.ValidationStatus.UNDER_REVIEW,
            reviewer="Hermes",
        )
    )
    record = run(
        engine.transition_status(
            record.record_id,
            engine.ValidationStatus.TESTED,
            reviewer="Hermes",
        )
    )
    record = run(
        engine.transition_status(
            record.record_id,
            engine.ValidationStatus.VALIDATED,
            reviewer="Council",
        )
    )

    assert record.validation_status == engine.ValidationStatus.VALIDATED
    assert len(record.reviews) == 3
    assert record.version == 4


def test_unsourced_record_cannot_be_validated():
    record = run(engine.create_record(make_payload(sources=[])))
    run(
        engine.transition_status(
            record.record_id,
            engine.ValidationStatus.UNDER_REVIEW,
            reviewer="Minerva",
        )
    )

    with pytest.raises(ValueError, match="require at least one source"):
        run(
            engine.transition_status(
                record.record_id,
                engine.ValidationStatus.VALIDATED,
                reviewer="Council",
            )
        )


def test_correction_reopens_validated_record_for_review():
    record = run(engine.create_record(make_payload()))
    record.validation_status = engine.ValidationStatus.VALIDATED
    run(engine._persist(record))

    corrected = run(
        engine.add_correction(
            record.record_id,
            engine.CorrectionEvent(
                original_claim="Cycle count was 1,000.",
                reason="The counter export omitted the final segment.",
                corrected_claim="Cycle count was 1,250.",
            ),
        )
    )

    assert corrected.validation_status == engine.ValidationStatus.UNDER_REVIEW
    assert corrected.corrections[0].corrected_claim == "Cycle count was 1,250."


def test_supersession_preserves_history_and_links_records():
    old = run(engine.create_record(make_payload()))
    old.validation_status = engine.ValidationStatus.VALIDATED
    run(engine._persist(old))

    superseded, replacement = run(
        engine.supersede_record(
            old.record_id,
            make_payload(
                title="Weaver actuator test revision 2",
                content="A revised actuator completed the expanded duty cycle.",
            ),
            reviewer="Council",
            notes="Expanded test protocol replaces the original record.",
        )
    )

    assert superseded.validation_status == engine.ValidationStatus.SUPERSEDED
    assert superseded.superseded_by_record_id == replacement.record_id
    assert replacement.supersedes_record_id == superseded.record_id
