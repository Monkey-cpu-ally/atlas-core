from services import knowledge_reasoning as kr


def setup_function():
    kr.reset_in_memory_state()


def test_seed_creates_auditable_council_decision():
    result = kr.seed_foundation_mission()
    detail = kr.mission_detail(result["mission"]["mission_id"])
    assert len(detail["assessments"]) == 3
    assert len(detail["evidence"]) == 1
    assert len(detail["risks"]) == 1
    assert detail["decisions"][0]["state"] == "decided"
    assert detail["decisions"][0]["confidence_score"] > 0


def test_blocking_gap_blocks_decision():
    mission = kr.create_mission(objective="Test missing evidence behavior", domains=["Robotics"])
    kr.add_gap(mission_id=mission["mission_id"], question="What test evidence exists?", reason="Validation data is missing.", blocking=True)
    decision = kr.council_decision(mission_id=mission["mission_id"], recommendation="Do not advance yet.", rationale_summary="A blocking evidence gap remains unresolved.")
    assert decision["state"] == "blocked"
    assert len(decision["blocking_gap_ids"]) == 1


def test_conflicting_evidence_reduces_confidence():
    mission = kr.create_mission(objective="Compare evidence confidence", domains=["Materials"])
    good = kr.add_evidence(mission_id=mission["mission_id"], source_id="source:a", claim="Supported claim", status="supported", quality_score=90)
    assessment = kr.add_assessment(mission_id=mission["mission_id"], specialist="Hermes", conclusion="Initial conclusion", recommendation="Initial recommendation", confidence_score=90, evidence_ids=[good["evidence_id"]])
    first = kr.council_decision(mission_id=mission["mission_id"], recommendation="First", rationale_summary="Supported evidence.", selected_assessment_ids=[assessment["assessment_id"]])
    kr.add_evidence(mission_id=mission["mission_id"], source_id="source:b", claim="Conflicting claim", status="conflicting", quality_score=90)
    second = kr.council_decision(mission_id=mission["mission_id"], recommendation="Second", rationale_summary="Conflict now exists.", selected_assessment_ids=[assessment["assessment_id"]])
    assert second["confidence_score"] < first["confidence_score"]


def test_invalid_specialist_is_rejected():
    mission = kr.create_mission(objective="Validate specialist controls", domains=["AI"])
    try:
        kr.add_assessment(mission_id=mission["mission_id"], specialist="Unknown", conclusion="x", recommendation="y", confidence_score=50)
    except ValueError as exc:
        assert "invalid specialist" in str(exc)
    else:
        raise AssertionError("Expected invalid specialist to fail")
