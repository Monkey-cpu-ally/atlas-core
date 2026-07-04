"""Tests for the ATLAS Research Lab Engine."""
import pytest

from services import research_lab_engine as labs


@pytest.fixture(autouse=True)
def clean_state():
    labs.reset_in_memory_state()
    yield
    labs.reset_in_memory_state()


def test_labs_roster_contains_all_ai_roles():
    roster = labs.labs()["labs"]
    roles = {item["ai"]: item["role"] for item in roster}
    assert roles["Ajani"] == "Chief Engineer"
    assert roles["Hermes"] == "Chief Robotics & Design"
    assert roles["Minerva"] == "Chief Scientist"
    assert roles["Council"] == "Executive Board"


def test_create_mission_for_ajani():
    mission = labs.create_mission(
        title="Hydrogen storage review",
        owner_ai="Ajani",
        goal="Compare high-trust hydrogen storage sources for ATLAS engineering.",
        source_ids=["doe", "nrel", "aist_japan"],
        subject_tags=["energy", "hydrogen"],
        related_projects=["Power Cell"],
        priority="high",
        council_review_required=True,
    )
    assert mission["owner_ai"] == "Ajani"
    assert mission["owner_role"] == "Chief Engineer"
    assert mission["status"] == "queued"
    assert mission["priority"] == "high"
    assert mission["council_review_required"] is True


def test_mission_status_lifecycle():
    mission = labs.create_mission(
        title="Robot joint study",
        owner_ai="Hermes",
        goal="Research compliant robot joints for Weaver.",
    )
    running = labs.update_mission_status(mission["mission_id"], "running", progress_percent=25)
    assert running["status"] == "running"
    assert running["progress_percent"] == 25
    assert running["started_at"] is not None

    completed = labs.update_mission_status(mission["mission_id"], "completed")
    assert completed["status"] == "completed"
    assert completed["progress_percent"] == 100
    assert completed["completed_at"] is not None


def test_list_missions_filters_by_owner_and_status():
    labs.create_mission(title="A", owner_ai="Ajani", goal="Engineering mission goal text.")
    h = labs.create_mission(title="H", owner_ai="Hermes", goal="Robotics mission goal text.")
    labs.update_mission_status(h["mission_id"], "running")

    hermes_running = labs.list_missions(owner_ai="Hermes", status="running")
    assert len(hermes_running) == 1
    assert hermes_running[0]["owner_ai"] == "Hermes"


def test_create_discovery_from_mission():
    mission = labs.create_mission(
        title="Plant library review",
        owner_ai="Minerva",
        goal="Review approved plant biology sources for medicinal plant knowledge.",
        source_ids=["pubmed", "fao"],
        related_projects=["Plant Library"],
        council_review_required=True,
    )
    discovery = labs.create_discovery(
        mission_id=mission["mission_id"],
        title="Medicinal plant evidence pattern",
        summary_in_own_words="Minerva identified a pattern that requires stronger source comparison.",
        why_it_matters="This could guide Plant Library evidence standards.",
        evidence=["Multiple source types required."],
        citations=[{"source_id": "pubmed", "url": "https://pubmed.ncbi.nlm.nih.gov"}],
        confidence_score=72,
        risks_and_limits=["Single test citation only."],
        recommendation="Council should review before Knowledge Bank approval.",
    )
    assert discovery["owner_ai"] == "Minerva"
    assert discovery["verification_status"] == "single_source"
    assert discovery["confidence_score"] == 72
    assert labs.get_mission(mission["mission_id"])["status"] == "council_review"


def test_council_review_approves_discovery():
    mission = labs.create_mission(title="Review", owner_ai="Council", goal="Council validation mission.")
    discovery = labs.create_discovery(
        mission_id=mission["mission_id"],
        title="Validated source rule",
        summary_in_own_words="Council reviewed a source validation rule.",
        why_it_matters="It affects Knowledge Bank trust.",
    )
    reviewed = labs.council_review(discovery["discovery_id"], "approved", notes="Approved for v1.")
    assert reviewed["reviewed_by_council"] is True
    assert reviewed["council_decision"] == "approved"
    assert reviewed["verification_status"] == "council_verified"


def test_invalid_ai_raises_error():
    with pytest.raises(labs.ResearchLabError):
        labs.create_mission(title="Bad", owner_ai="Unknown", goal="Invalid AI should fail.")
