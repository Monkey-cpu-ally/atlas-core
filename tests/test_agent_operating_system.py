import pytest

from atlas_core.agents import (
    AgentMessage,
    AgentTask,
    AtlasMemory,
    CouncilBus,
    CouncilVerdict,
    CouncilVote,
    MemoryAccessError,
    MessageKind,
    ProjectOrchestrator,
    WeightedCouncil,
)


def test_orchestrator_assigns_by_specialty_and_tracks_progress():
    system = ProjectOrchestrator()
    project = system.create_project("hof-1", "House of Frazier Collection")
    research = system.add_task("hof-1", AgentTask("t1", "Research heritage", "research"))
    engineering = system.add_task(
        "hof-1",
        AgentTask("t2", "Engineer closure", "engineering", dependencies={"t1"}),
    )
    assert research.assignee == "Minerva"
    assert engineering.assignee == "Hermes"
    assert system.blocked_tasks("hof-1") == [engineering]
    system.complete_task("hof-1", "t1")
    system.complete_task("hof-1", "t2")
    assert project.progress == 100.0


def test_private_memory_isolated():
    memory = AtlasMemory()
    memory.remember_global("collection", "Genesis", "Minerva")
    memory.remember_private("Hermes", "stress-model", {"limit": 220})
    assert memory.recall("collection", "Ajani").value == "Genesis"
    with pytest.raises(MemoryAccessError):
        memory.recall("stress-model", "Ajani", owner="Hermes")


def test_bus_archives_project_messages():
    bus = CouncilBus()
    bus.publish(AgentMessage("Hermes", "Council", MessageKind.REVIEW, "Engineering", "Passed", "hof-1"))
    assert len(bus.project_log("hof-1")) == 1
    assert len(bus.inbox("Minerva", "hof-1")) == 1


def test_weighted_council_prioritizes_domain_expert():
    decision = WeightedCouncil().decide(
        "engineering",
        [
            CouncilVote("Hermes", 55, CouncilVerdict.REJECT),
            CouncilVote("Minerva", 95, CouncilVerdict.APPROVE),
            CouncilVote("Ajani", 95, CouncilVerdict.APPROVE),
        ],
    )
    assert decision.verdict is CouncilVerdict.REJECT
    assert decision.weights["Hermes"] == 0.60
