from services import chronicle_engine, discovery_approval_pipeline as dap, knowledge_record_writer


def setup_function():
    dap.reset_in_memory_state()
    chronicle_engine.reset_in_memory_state()
    knowledge_record_writer.reset_in_memory_state()


def test_discovery_draft_scores_evidence():
    draft = dap.create_draft(
        title="Solid state battery safety finding",
        summary="ATLAS summary of a reviewed technical finding.",
        owner_ai="Minerva",
        evidence=[
            {"source_type": "peer_reviewed", "citation": "paper-1", "direct_support": True},
            {"source_type": "government", "url": "https://example.invalid/report", "direct_support": True},
        ],
        related_subjects=["Chemistry", "Engineering"],
        related_projects=["project:power_cell"],
    )

    assert draft["discovery_id"].startswith("DISC-")
    assert draft["status"] == "draft"
    assert draft["evidence_score"]["items_count"] == 2
    assert draft["evidence_score"]["score"] > 0


def test_review_and_council_approval_creates_record_and_chronicle():
    draft = dap.create_draft(
        title="NIR material sorting improvement",
        summary="ATLAS summary of a material sorting improvement.",
        owner_ai="Hermes",
        evidence=[{"source_type": "technical_documentation", "source_id": "doc-1", "direct_support": True}],
        related_projects=["project:nir_scanner"],
    )

    dap.add_review(
        discovery_id=draft["discovery_id"],
        reviewer_ai="Ajani",
        recommendation="approve",
        rationale="Engineering risk is acceptable for prototype review.",
        confidence_score=82,
    )
    dap.add_review(
        discovery_id=draft["discovery_id"],
        reviewer_ai="Minerva",
        recommendation="approve",
        rationale="Evidence is adequate for controlled knowledge storage.",
        confidence_score=78,
    )

    decision = dap.council_decide(
        discovery_id=draft["discovery_id"],
        decision="approved",
        rationale="Approved as summarized ATLAS knowledge with citation metadata only.",
    )

    updated = dap.get_draft(draft["discovery_id"])
    assert decision["decision"] == "approved"
    assert decision["knowledge_record"]["content_stored"] == "atlas_summary_only"
    assert decision["chronicle_entry"]["event_type"] == "knowledge_approved"
    assert updated["knowledge_record_id"] == decision["knowledge_record"]["knowledge_record_id"]
    assert updated["chronicle_id"] == decision["chronicle_entry"]["chronicle_id"]


def test_invalid_review_recommendation_is_rejected():
    draft = dap.create_draft(title="Test", summary="A valid discovery summary.")

    try:
        dap.add_review(
            discovery_id=draft["discovery_id"],
            reviewer_ai="Ajani",
            recommendation="ship_it_fast",
            rationale="bad recommendation",
        )
    except dap.DiscoveryApprovalError as exc:
        assert "invalid recommendation" in str(exc)
    else:
        raise AssertionError("Expected invalid recommendation to fail")
