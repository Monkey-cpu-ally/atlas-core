from creative_production.orchestrator import CreativeProductionOrchestrator, CreativeProductionRequest
from creative_production.project_store import CreativeProjectStore


def request(*, emotion: str, seconds: float) -> CreativeProductionRequest:
    return CreativeProductionRequest(
        project="Night Band", idea="a child returns a stolen star horn", emotion=emotion,
        visual_subject="girl and horn", visual_purpose="protect the horn as focal object",
        beat_goals=["hear the horn", "choose to return it"], character_name="Girl",
        environment_name="Mystic Forest", prop_name="Star Horn", fps=24, seconds_per_beat=seconds,
    )


def test_produce_revise_compare_restore_end_to_end(tmp_path):
    store = CreativeProjectStore(str(tmp_path / "projects.sqlite3"))
    orchestrator = CreativeProductionOrchestrator(project_store=store)

    package1, v1 = orchestrator.produce_and_save(request(emotion="wonder", seconds=2.0), message="initial cut")
    package2, v2 = orchestrator.produce_and_save(request(emotion="wonder and danger", seconds=2.5), message="increase tension")

    assert v1.version == 1
    assert v2.version == 2
    assert package1.timing.total_frames == 96
    assert package2.timing.total_frames == 120

    changes = store.compare(project="Night Band", from_version=1, to_version=2)
    assert "request" in changes
    assert "timing" in changes
    assert changes["timing"]["before"]["total_frames"] == 96
    assert changes["timing"]["after"]["total_frames"] == 120

    v3 = store.restore(project="Night Band", version=1, message="restore initial approved cut")
    assert v3.version == 3
    assert v3.parent_version == 2
    assert v3.payload == v1.payload
    assert [revision.version for revision in store.history("Night Band")] == [1, 2, 3]
