from services import global_knowledge_network as gkn
from services import project_knowledge_linker as pkl
from services import technology_atlas


def setup_function():
    gkn.reset_in_memory_state()
    technology_atlas.reset_in_memory_state()
    pkl.reset_in_memory_state()


def test_seed_project_profiles_creates_atlas_projects():
    result = pkl.seed_project_profiles()
    summary = pkl.project_knowledge_summary()

    assert result["created_or_updated"] >= 5
    assert summary["project_count"] >= 5
    assert summary["lead_ai"]["Hermes"] >= 1
    assert summary["lead_ai"]["Minerva"] >= 1


def test_project_brief_recommends_technologies_and_institutions():
    gkn.seed_foundation_registry()
    technology_atlas.seed_foundation_technologies()
    pkl.seed_project_profiles()

    brief = pkl.build_project_brief("project:weaver")

    assert brief["title"] == "ATLAS Project Knowledge Brief"
    assert brief["project"]["project_id"] == "project:weaver"
    assert any(item["name"] == "Advanced Robotics" for item in brief["recommended_technologies"])
    assert len(brief["recommended_institutions"]) > 0
    assert "ISO" in brief["standards_to_review"]


def test_project_brief_rejects_unknown_project():
    try:
        pkl.build_project_brief("project:missing")
    except ValueError as exc:
        assert "unknown project_id" in str(exc)
    else:
        raise AssertionError("Expected unknown project to fail")


def test_project_link_requires_known_project():
    try:
        pkl.link_project_to_target(
            project_id="project:missing",
            target_type="technology",
            target_id="TECH-test",
            relationship_type="uses",
            rationale="test",
        )
    except ValueError as exc:
        assert "unknown project_id" in str(exc)
    else:
        raise AssertionError("Expected unknown project to fail")


def test_project_link_creation():
    pkl.seed_project_profiles()
    link = pkl.link_project_to_target(
        project_id="project:weaver",
        target_type="technology",
        target_id="TECH-advanced-robotics-test",
        relationship_type="uses",
        rationale="Weaver requires robotics research references.",
        confidence_score=88,
    )

    assert link["link_id"].startswith("PKL-")
    assert link["project_id"] == "project:weaver"
    assert pkl.project_knowledge_summary()["link_count"] == 1
