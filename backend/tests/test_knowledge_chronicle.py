from services import knowledge_chronicle


def setup_function():
    knowledge_chronicle.reset_in_memory_state()


def test_seed_foundation_records_creates_chronicle():
    result = knowledge_chronicle.seed_foundation_records()
    summary = knowledge_chronicle.chronicle_summary()

    assert result["created_or_updated"] >= 3
    assert summary["record_count"] >= 3
    assert summary["event_count"] >= 3
    assert summary["ai_owners"]["Council"] >= 1


def test_create_record_and_filter_by_project():
    record = knowledge_chronicle.create_record(
        title="Test robotics note",
        claim="Robotics records should be traceable to projects and evidence metadata.",
        source_name="test",
        source_type="unit_test",
        evidence_level="official",
        confidence_score=77,
        ai_owner="Hermes",
        project_ids=["project:weaver"],
        tags=["robotics"],
    )

    records = knowledge_chronicle.list_records(project_id="project:weaver")
    assert records[0]["record_id"] == record["record_id"]
    assert record["version"] == 1


def test_review_status_and_revision_increment_history():
    record = knowledge_chronicle.create_record(
        title="Test knowledge",
        claim="Original claim for testing.",
        source_name="test",
        source_type="unit_test",
        evidence_level="academic",
        confidence_score=50,
        ai_owner="Minerva",
    )
    reviewed = knowledge_chronicle.update_review_status(
        record_id=record["record_id"],
        review_status="evidence_review",
        reviewer="Minerva",
        note="Move to evidence review.",
    )
    revised = knowledge_chronicle.revise_record(
        record_id=record["record_id"],
        claim="Revised claim for testing.",
        note="Clarified claim.",
        reviewer="Minerva",
        confidence_score=70,
    )

    assert reviewed["review_status"] == "evidence_review"
    assert revised["version"] == 2
    assert revised["confidence_score"] == 70
    assert len(knowledge_chronicle.list_events(record_id=record["record_id"])) >= 3
