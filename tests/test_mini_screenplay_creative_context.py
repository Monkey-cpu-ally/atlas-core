from creative_intelligence.agent_context import AgentCreativeContextService
from creative_intelligence.creative_memory import CreativeLesson, CreativeMemory
from story_foundry.creative_memory_bridge import StoryFoundryCreativeBridge
from story_foundry.mini_screenplay_engine import MiniScreenplayEngine


def test_screenplay_plan_consumes_learned_creative_context():
    memory = CreativeMemory()
    memory.remember(CreativeLesson(
        project="Night Band",
        task="mini screenplay",
        references=["approved-study"],
        principle_attempted="repeat a visual motif after an emotional turn",
        outcome="stronger payoff",
        critique="motif must change meaning",
        revision="echo opening object in final image",
        lesson="visual repetition gains power when context changes",
        confidence=0.94,
    ))
    bridge = StoryFoundryCreativeBridge(AgentCreativeContextService(memory))
    engine = MiniScreenplayEngine(creative_bridge=bridge)
    plan = engine.build_plan("Night Band", "a child returning a stolen star horn", "wonder and danger")

    assert plan.creative_context
    assert "repeat a visual motif" in plan.creative_context
    assert "AJANI" in plan.creative_context
    assert "MINERVA" in plan.creative_context
    assert "HERMES" in plan.creative_context
    assert "Creative Intelligence Context" in plan.to_markdown()


def test_screenplay_engine_remains_backward_compatible_without_memory():
    plan = MiniScreenplayEngine().build_plan("Original", "a difficult choice", "hope")
    assert plan.title == "Original"
    assert plan.creative_context == ""
