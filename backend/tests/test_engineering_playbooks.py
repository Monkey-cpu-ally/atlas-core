from services import engineering_playbooks


def setup_function():
    engineering_playbooks.reset_in_memory_state()


def test_seed_foundation_playbooks_creates_engineering_manuals():
    result = engineering_playbooks.seed_foundation_playbooks()
    summary = engineering_playbooks.playbook_summary()

    assert result["created_or_updated"] >= 3
    assert summary["playbook_count"] >= 3
    assert summary["section_count"] >= 3
    assert summary["component_count"] >= 1
    assert summary["material_count"] >= 1
    assert summary["failure_count"] >= 1
    assert summary["pattern_count"] >= 1


def test_create_playbook_and_add_section_counts():
    playbook = engineering_playbooks.create_playbook(
        title="Test Engineering Playbook",
        playbook_type="technology",
        owner_ai="Hermes",
        domains=["Testing", "Robotics"],
        summary="A test playbook for engineering playbook validation.",
    )
    section = engineering_playbooks.add_section(
        playbook_id=playbook["playbook_id"],
        section_type="overview",
        title="Overview",
        content="This section explains the test playbook overview.",
        confidence_score=75,
    )
    updated = engineering_playbooks.get_playbook(playbook["playbook_id"])

    assert section["playbook_id"] == playbook["playbook_id"]
    assert updated["section_count"] == 1
    assert updated["version"] == 1


def test_detail_includes_components_materials_failures_patterns():
    playbook = engineering_playbooks.create_playbook(
        title="Robot Arm Playbook",
        playbook_type="project",
        owner_ai="Hermes",
        domains=["Robotics"],
        summary="Robot arm engineering test playbook.",
    )
    engineering_playbooks.add_component(
        playbook_id=playbook["playbook_id"],
        name="Joint actuator",
        component_type="motion",
        function="Moves a robot joint.",
    )
    engineering_playbooks.add_material(
        playbook_id=playbook["playbook_id"],
        name="Aluminum",
        material_family="metal",
    )
    engineering_playbooks.add_failure(
        playbook_id=playbook["playbook_id"],
        title="Joint overheating",
        root_cause="Excessive load.",
        severity="high",
        corrective_action="Reduce load and inspect actuator.",
        preventive_action="Add thermal monitoring.",
    )
    engineering_playbooks.add_design_pattern(
        playbook_id=playbook["playbook_id"],
        name="Modular joint",
        pattern_type="mechanical",
        intent="Make joints replaceable.",
        structure=["joint", "connector", "harness"],
    )
    detail = engineering_playbooks.playbook_detail(playbook["playbook_id"])

    assert len(detail["components"]) == 1
    assert len(detail["materials"]) == 1
    assert len(detail["failures"]) == 1
    assert len(detail["patterns"]) == 1
    assert len(detail["revisions"]) >= 5


def test_rejects_invalid_playbook_type():
    try:
        engineering_playbooks.create_playbook(
            title="Bad Playbook",
            playbook_type="bad",
            owner_ai="Hermes",
            domains=["Testing"],
            summary="Invalid type should fail.",
        )
    except ValueError as exc:
        assert "invalid playbook_type" in str(exc)
    else:
        raise AssertionError("Expected invalid playbook type to fail")
