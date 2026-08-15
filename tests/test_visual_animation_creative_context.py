from creative_intelligence.agent_context import AgentCreativeContextService
from creative_intelligence.creative_memory import CreativeLesson, CreativeMemory
from story_foundry.creative_memory_bridge import StoryFoundryCreativeBridge
from academy.school_of_visual_development import VisualDevelopmentEngine
from atlas_animation_studio.storyboard_engine import StoryboardEngine


def _bridge():
    memory = CreativeMemory()
    memory.remember(CreativeLesson(
        project="Hyper Axel",
        task="visual development animation storyboard",
        references=["approved-study"],
        principle_attempted="use silhouette contrast before surface detail",
        outcome="faster visual read",
        critique="secondary shapes competed with the focal mass",
        revision="simplify secondary forms and protect negative space",
        lesson="clarity should survive at thumbnail scale",
        confidence=0.93,
    ))
    return StoryFoundryCreativeBridge(AgentCreativeContextService(memory))


def test_visual_development_consumes_creative_memory():
    plan = VisualDevelopmentEngine(_bridge()).build_plan(
        project="Hyper Axel",
        subject="aircraft mechanic hero",
        purpose="readable silhouette and mechanical identity",
    )
    assert plan.creative_context
    assert "silhouette contrast" in plan.creative_context
    assert "HERMES" in plan.creative_context
    assert "Creative Intelligence Context" in plan.to_markdown()


def test_animation_storyboard_consumes_creative_memory():
    sequence = StoryboardEngine(_bridge()).build_sequence(
        title="Hyper Axel",
        scene_number=1,
        beat_goals=["discover danger", "choose to act"],
    )
    assert len(sequence.frames) == 2
    assert sequence.creative_context
    assert "silhouette contrast" in sequence.creative_context
    assert "AJANI" in sequence.creative_context
    assert "Creative Intelligence Context" in sequence.to_markdown()


def test_consumers_work_without_memory_bridge():
    visual = VisualDevelopmentEngine().build_plan(project="Original", subject="robot", purpose="function")
    animation = StoryboardEngine().build_sequence("Original", 1, ["begin"])
    assert visual.creative_context == ""
    assert animation.creative_context == ""
