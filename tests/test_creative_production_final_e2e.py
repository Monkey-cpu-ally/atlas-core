from creative_production.continuity import ContinuityState
from creative_production.orchestrator import CreativeProductionOrchestrator, CreativeProductionRequest
from creative_production.project_store import CreativeProjectStore


def request(*, emotion: str = "wonder and danger", seconds: float = 2.5) -> CreativeProductionRequest:
    return CreativeProductionRequest(
        project="Night Band",
        idea="a child returns a stolen star horn before eternal night falls",
        emotion=emotion,
        visual_subject="girl, star horn, and mystic forest",
        visual_purpose="keep the horn as the emotional focal object while the forest grows threatening",
        beat_goals=["enter the forbidden forest", "hear the horn answer", "choose to continue"],
        scene_number=2,
        character_name="Girl",
        character_role="emotional center",
        environment_name="Mystic Forest",
        environment_function="threshold between safety and the unknown",
        prop_name="Star Horn",
        prop_function="stolen magical object and story catalyst",
        fps=24,
        seconds_per_beat=seconds,
    )


def state(*, condition: str, horn: str, owner: str) -> ContinuityState:
    return ContinuityState(
        scene_number=2,
        character="Girl",
        location="Mystic Forest",
        time_of_day="night",
        costume="navy school uniform",
        condition=condition,
        props={"Star Horn": horn},
        facts={"horn_owner": owner, "queen_alive": True},
    )


def test_final_creative_production_regression_lifecycle(tmp_path):
    store = CreativeProjectStore(str(tmp_path / "creative-production.sqlite3"))
    orchestrator = CreativeProductionOrchestrator(project_store=store)

    # V1: complete approved baseline production package.
    package1, v1 = orchestrator.produce_and_save(
        request(seconds=2.0),
        continuity_state=state(condition="scratched arm", horn="glowing", owner="fairies"),
        message="approved baseline production",
    )
    assert package1.manifest.is_ready_for_production
    assert package1.manifest.validate_dependencies() == []
    assert package1.timing.total_frames == 144
    assert len(package1.storyboard.frames) == 3
    assert package1.character_sheet.name == "Girl"
    assert package1.environment_sheet.name == "Mystic Forest"
    assert package1.prop_sheet.name == "Star Horn"
    assert v1.version == 1
    assert v1.payload["manifest"]["ready_for_production"] is True

    # V2: revision changes timing and breaks established continuity.
    package2, v2 = orchestrator.produce_and_save(
        request(emotion="wonder, fear, and resolve", seconds=2.5),
        continuity_state=state(condition="uninjured", horn="dark", owner="Girl"),
        message="revised dramatic cut",
    )
    assert v2.version == 2
    assert package2.timing.total_frames == 180
    assert {issue.category for issue in package2.continuity_issues} == {"condition", "prop", "story_fact"}
    assert not package2.manifest.is_ready_for_production
    assert package2.manifest.unresolved_continuity()[2]

    # Revision comparison must expose both creative/timing and continuity changes.
    changes = store.compare(project="Night Band", from_version=1, to_version=2)
    assert "request" in changes
    assert "timing" in changes
    assert "continuity_state" in changes
    assert changes["timing"]["before"]["total_frames"] == 144
    assert changes["timing"]["after"]["total_frames"] == 180

    # Intentional changes can be approved without erasing the audit trail.
    scene = package2.manifest.scenes[2]
    original_issue_ids = list(scene.continuity_issue_ids)
    for issue_id in original_issue_ids:
        scene.approve_continuity_change(issue_id)
    assert package2.manifest.is_ready_for_production
    assert scene.continuity_issue_ids == original_issue_ids
    assert sorted(scene.approved_continuity_issue_ids) == sorted(original_issue_ids)

    # V3 records the approved intentional change as a new immutable revision.
    v3 = store.save_revision(
        project="Night Band",
        payload=package2.snapshot(),
        message="approve intentional continuity changes",
    )
    assert v3.version == 3
    assert v3.parent_version == 2
    assert v3.payload["manifest"]["ready_for_production"] is True
    assert v3.payload["continuity_issues"] == v2.payload["continuity_issues"]
    assert [revision.version for revision in store.history("Night Band")] == [1, 2, 3]

    # Restoring V1 creates V4 rather than deleting V2/V3.
    v4 = store.restore(project="Night Band", version=1, message="restore approved baseline")
    assert v4.version == 4
    assert v4.parent_version == 3
    assert v4.payload == v1.payload
    assert [revision.version for revision in store.history("Night Band")] == [1, 2, 3, 4]
