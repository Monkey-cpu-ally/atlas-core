from creative_intelligence.agent_context import AgentCreativeContextService
from creative_intelligence.creative_memory import CreativeLesson, CreativeMemory
from story_foundry.creative_memory_bridge import StoryFoundryCreativeBridge


def test_story_foundry_receives_three_agent_lenses():
    memory = CreativeMemory()
    memory.remember(CreativeLesson(
        project="Night Band",
        task="visual storytelling",
        references=["approved-study"],
        principle_attempted="silhouette before detail",
        outcome="clear read",
        critique="keep focal hierarchy",
        revision="simplify secondary forms",
        lesson="establish readable shape before surface detail",
        confidence=0.91,
    ))
    bridge = StoryFoundryCreativeBridge(AgentCreativeContextService(memory))
    brief = bridge.build_brief(project="Night Band", task="visual storytelling")
    prompt = brief.to_prompt_context()
    assert "AJANI" in prompt
    assert "MINERVA" in prompt
    assert "HERMES" in prompt
    assert "silhouette before detail" in prompt
    assert "Do not reproduce" in prompt
