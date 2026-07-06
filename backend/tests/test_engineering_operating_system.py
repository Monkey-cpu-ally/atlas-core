from services import engineering_operating_system as aeos


def setup_function():
    aeos.reset_in_memory_state()


def test_seed_foundation_missions_creates_dashboard():
    result = aeos.seed_foundation_missions()
    dashboard = aeos.dashboard_summary()

    assert result["created_or_updated"] >= 3
    assert dashboard["mission_count"] >= 3
    assert dashboard["task_count"] >= 6
    assert dashboard["missions_by_ai"]["Hermes"] >= 1
    assert dashboard["average_erl"] >= 1


def test_create_and_advance_mission_updates_erl():
    mission = aeos.create_mission(
        title="Test Mission",
        project_id="project:test",
        objective="Create a test mission for AEOS.",
        lead_ai="Ajani",
    )
    advanced = aeos.advance_mission(
        mission_id=mission["mission_id"],
        workflow_phase="simulation",
        note="Ready for simulation planning.",
        actor="Ajani",
    )

    assert mission["engineering_readiness_level"] == 1
    assert advanced["workflow_phase"] == "simulation"
    assert advanced["engineering_readiness_level"] == 4
    assert advanced["engineering_readiness_label"] == "Simulation"


def test_task_completion_recalculates_mission():
    mission = aeos.create_mission(
        title="Task Mission",
        project_id="project:task",
        objective="Track task completion.",
        lead_ai="Hermes",
    )
    task = aeos.create_task(
        mission_id=mission["mission_id"],
        title="Complete first task",
        owner_ai="Hermes",
        phase="research",
    )
    aeos.update_task_status(
        task_id=task["task_id"],
        status="done",
        note="Task completed.",
        actor="Hermes",
    )
    updated = aeos.get_mission(mission["mission_id"])

    assert updated["completion_percent"] == 100
    assert len(aeos.list_events(mission_id=mission["mission_id"])) >= 3


def test_high_risk_blocks_mission():
    mission = aeos.create_mission(
        title="Risk Mission",
        project_id="project:risk",
        objective="Track risk blocking.",
        lead_ai="Council",
    )
    aeos.create_risk(
        mission_id=mission["mission_id"],
        title="Critical test risk",
        severity="critical",
        mitigation="Resolve before prototype work.",
        owner_ai="Council",
    )
    updated = aeos.get_mission(mission["mission_id"])

    assert updated["status"] == "blocked"
    assert "Critical test risk" in updated["current_blockers"]
