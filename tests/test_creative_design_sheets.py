from creative_intelligence.agent_context import AgentCreativeContextService
from creative_intelligence.creative_memory import CreativeLesson, CreativeMemory
from story_foundry.creative_memory_bridge import StoryFoundryCreativeBridge
from creative_production.design_sheets import DesignSheetEngine


def test_design_sheets_consume_creative_intelligence():
    memory = CreativeMemory()
    memory.remember(CreativeLesson(
        project="Night Band", task="design sheets", references=["approved-study"],
        principle_attempted="protect silhouette hierarchy", outcome="clear read",
        critique="detail competed with identity", revision="simplify secondary forms",
        lesson="identity must survive before surface detail", confidence=0.96,
    ))
    engine = DesignSheetEngine(StoryFoundryCreativeBridge(AgentCreativeContextService(memory)))
    character = engine.character(project="Night Band", name="Protagonist", role="emotional center")
    environment = engine.environment(project="Night Band", name="Mystic Forest", story_function="threshold into the unknown")
    prop = engine.prop(project="Night Band", name="Star Horn", story_function="stolen magical object")

    for sheet in (character, environment, prop):
        assert sheet.creative_context
        assert "AJANI" in sheet.creative_context
        assert "MINERVA" in sheet.creative_context
        assert "HERMES" in sheet.creative_context
        assert "protect silhouette hierarchy" in sheet.creative_context


def test_design_sheets_work_without_memory():
    engine = DesignSheetEngine()
    assert engine.character(project="X", name="A", role="lead").creative_context == ""
    assert engine.environment(project="X", name="B", story_function="arena").creative_context == ""
    assert engine.prop(project="X", name="C", story_function="key object").creative_context == ""
