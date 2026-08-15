from creative_intelligence.agent_context import AgentCreativeContextService
from creative_intelligence.creative_memory import CreativeLesson, CreativeMemory
from story_foundry.creative_memory_bridge import StoryFoundryCreativeBridge
from creative_production.shot_planning import ShotPlanningEngine


def test_shot_planning_carries_context_and_calculates_timing():
    memory = CreativeMemory()
    memory.remember(CreativeLesson(
        project="Night Band", task="shot planning", references=["approved-study"],
        principle_attempted="hold before reveal", outcome="stronger tension",
        critique="cut arrived too early", revision="add anticipation frames",
        lesson="timing should let the audience form a question before the answer", confidence=0.95,
    ))
    bridge = StoryFoundryCreativeBridge(AgentCreativeContextService(memory))
    plan = ShotPlanningEngine(bridge, fps=24).plan_scene(
        project="Night Band", scene_number=1,
        beat_goals=["girl hears the horn", "horn answers"], seconds_per_beat=2.5,
    )
    assert len(plan.shots) == 2
    assert plan.total_seconds == 5.0
    assert plan.total_frames == 120
    assert plan.shots[0].frame_count == 60
    assert plan.shots[0].key_poses == [1, 30, 60]
    assert "AJANI" in plan.shots[0].creative_context
    assert "hold before reveal" in plan.shots[0].creative_context


def test_shot_planning_without_memory_and_validation():
    plan = ShotPlanningEngine(fps=12).plan_scene(
        project="X", scene_number=2, beat_goals=["turn"], seconds_per_beat=1.0
    )
    assert plan.total_frames == 12
    assert plan.shots[0].creative_context == ""
