from services import technology_atlas


def setup_function():
    technology_atlas.reset_in_memory_state()


def test_seed_foundation_technologies_creates_registry():
    result = technology_atlas.seed_foundation_technologies()
    summary = technology_atlas.technology_summary()

    assert result["created_or_updated"] >= 6
    assert summary["technology_count"] >= 6
    assert summary["categories"]["Energy"] >= 1
    assert summary["ai_owners"]["Hermes"] >= 1
    assert summary["maturity_levels"]["industrial"] >= 1


def test_technology_filters_by_project_and_discipline():
    technology_atlas.seed_foundation_technologies()

    power_cell = technology_atlas.list_technologies(project="project:power_cell")
    robotics = technology_atlas.list_technologies(discipline="Robotics")

    assert any(item["name"] == "Hydrogen Energy Systems" for item in power_cell)
    assert any("Robotics" in item["disciplines"] for item in robotics)


def test_relationship_requires_known_technology():
    try:
        technology_atlas.link_institution_to_technology(
            institution_id="GKN-test",
            technology_id="missing",
            relationship_type="researches",
            evidence_note="test",
        )
    except ValueError as exc:
        assert "unknown technology_id" in str(exc)
    else:
        raise AssertionError("Expected unknown technology to fail")


def test_relationship_links_institution_to_technology():
    technology = technology_atlas.create_technology(
        name="Test Robotics",
        category="Robotics",
        description="A test robotics technology entry.",
        disciplines=["Robotics"],
        primary_ai_owner="Hermes",
    )
    relationship = technology_atlas.link_institution_to_technology(
        institution_id="GKN-test-institution",
        technology_id=technology["technology_id"],
        relationship_type="researches",
        evidence_note="Institution has robotics research programs.",
        confidence_score=81,
    )

    assert relationship["relationship_id"].startswith("GKN-REL-")
    assert relationship["technology_id"] == technology["technology_id"]
    assert technology_atlas.technology_summary()["relationship_count"] == 1
