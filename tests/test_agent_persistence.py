from pathlib import Path

from atlas_core.agents import (
    AgentMessage,
    AgentOperatingService,
    AgentStore,
    AgentTask,
    CouncilVerdict,
    CouncilVote,
    MessageKind,
    ProjectOrchestrator,
)


def test_project_round_trip(tmp_path: Path):
    path = tmp_path / "agents.db"
    orchestrator = ProjectOrchestrator()
    project = orchestrator.create_project("hof-2", "House of Frazier")
    orchestrator.add_task("hof-2", AgentTask("t1", "Engineer clasp", "engineering"))

    store = AgentStore(path)
    store.save_project(project)
    restored = store.load_project("hof-2")

    assert restored is not None
    assert restored.name == "House of Frazier"
    assert restored.tasks["t1"].assignee == "Hermes"


def test_service_survives_restart(tmp_path: Path):
    path = tmp_path / "agents.db"
    first = AgentOperatingService(path)
    first.create_project("academy-1", "Luxury Design Academy")
    first.add_task("academy-1", AgentTask("lesson-1", "Research design history", "research"))

    second = AgentOperatingService(path)
    project = second.load_project("academy-1")

    assert project is not None
    assert project.tasks["lesson-1"].assignee == "Minerva"


def test_memory_message_and_decision_round_trip(tmp_path: Path):
    path = tmp_path / "agents.db"
    service = AgentOperatingService(path)
    service.create_project("hof-3", "Genesis Collection")

    memory = service.remember_global("palette", ["ivory", "crimson"], "Minerva")
    assert service.store.load_memory("palette") == memory

    service.publish(
        AgentMessage(
            "Hermes",
            "Council",
            MessageKind.REVIEW,
            "Closure test",
            "Passed",
            "hof-3",
        )
    )
    assert service.store.project_messages("hof-3")[0].body == "Passed"

    decision = service.decide(
        "hof-3",
        "engineering",
        [
            CouncilVote("Hermes", 90, CouncilVerdict.APPROVE),
            CouncilVote("Minerva", 85, CouncilVerdict.APPROVE),
            CouncilVote("Ajani", 80, CouncilVerdict.APPROVE),
        ],
    )
    restored = service.store.latest_decision("hof-3")
    assert restored is not None
    assert restored["score"] == decision.score
    assert restored["verdict"] is CouncilVerdict.APPROVE
