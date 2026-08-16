from creative_production.continuity import ContinuityState
from creative_production.orchestrator import CreativeProductionOrchestrator, CreativeProductionRequest
from creative_production.project_store import CreativeProjectStore


def request() -> CreativeProductionRequest:
    return CreativeProductionRequest(
        project="Night Band", idea="return the stolen star horn", emotion="wonder and danger",
        visual_subject="girl and star horn", visual_purpose="protect the horn as focal object",
        beat_goals=["enter forest", "hear the fairies"], scene_number=2,
        character_name="Girl", environment_name="Mystic Forest", prop_name="Star Horn",
    )


def state(*, condition: str, horn: str, owner: str) -> ContinuityState:
    return ContinuityState(
        scene_number=2, character="Girl", location="Mystic Forest", time_of_day="night",
        costume="navy uniform", condition=condition, props={"Star Horn": horn}, facts={"horn_owner": owner},
    )


def test_continuity_is_persisted_and_automatically_blocks_changed_revision(tmp_path):
    store = CreativeProjectStore(str(tmp_path / "projects.sqlite3"))
    orchestrator = CreativeProductionOrchestrator(project_store=store)

    package1, v1 = orchestrator.produce_and_save(
        request(), continuity_state=state(condition="scratched arm", horn="glowing", owner="fairies"), message="approved continuity baseline"
    )
    assert package1.manifest.is_ready_for_production
    assert v1.payload["continuity_state"]["condition"] == "scratched arm"
    assert v1.payload["continuity_issues"] == []

    package2, v2 = orchestrator.produce_and_save(
        request(), continuity_state=state(condition="uninjured", horn="dark", owner="Girl"), message="revised scene"
    )

    categories = {issue.category for issue in package2.continuity_issues}
    assert categories == {"condition", "prop", "story_fact"}
    assert not package2.manifest.is_ready_for_production
    assert package2.manifest.unresolved_continuity()[2]
    assert v2.payload["continuity_state"]["props"]["Star Horn"] == "dark"
    assert len(v2.payload["continuity_issues"]) == 3
    assert v2.payload["manifest"]["ready_for_production"] is False
