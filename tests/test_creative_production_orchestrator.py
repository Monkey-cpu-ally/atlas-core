from creative_intelligence.agent_context import AgentCreativeContextService
from creative_intelligence.creative_memory import CreativeLesson, CreativeMemory
from story_foundry.creative_memory_bridge import StoryFoundryCreativeBridge
from creative_production.orchestrator import CreativeProductionOrchestrator, CreativeProductionRequest


def test_production_pipeline_carries_creative_intelligence_end_to_end():
    memory = CreativeMemory()
    memory.remember(CreativeLesson(
        project="Night Band", task="creative production", references=["approved-study"],
        principle_attempted="shape hierarchy before detail", outcome="clearer visual storytelling",
        critique="secondary forms competed with focal point", revision="simplify secondary shapes",
        lesson="protect the dominant read across screenplay, design, and shots", confidence=0.95,
    ))
    bridge = StoryFoundryCreativeBridge(AgentCreativeContextService(memory))
    package = CreativeProductionOrchestrator(creative_bridge=bridge).produce(CreativeProductionRequest(
        project="Night Band", idea="a child returns a stolen star horn", emotion="wonder and danger",
        visual_subject="the child and star horn", visual_purpose="make the horn the emotional focal object",
        beat_goals=["discover the horn is alive", "choose to return it"],
        character_name="Girl", environment_name="Mystic Forest", prop_name="Star Horn",
        fps=24, seconds_per_beat=2.5,
    ))

    assert package.has_creative_intelligence
    assert "AJANI" in package.screenplay.creative_context
    assert "MINERVA" in package.character_sheet.creative_context
    assert "HERMES" in package.prop_sheet.creative_context
    assert package.timing.total_frames == 120
    assert package.manifest.summary()["asset_count"] == 3
    assert package.manifest.summary()["scene_count"] == 1
    assert package.manifest.summary()["total_frames"] == 120
    assert package.manifest.validate_dependencies() == []
    assert package.manifest.is_ready_for_production
    assert "shape hierarchy before detail" in package.to_markdown()
    assert "Production Manifest" in package.to_markdown()


def test_production_pipeline_runs_without_creative_memory():
    package = CreativeProductionOrchestrator().produce(CreativeProductionRequest(
        project="Original", idea="a machine finds a seed", emotion="hope",
        visual_subject="machine and seed", visual_purpose="contrast hard and organic forms",
        beat_goals=["find the seed", "protect it"],
    ))
    assert not package.has_creative_intelligence
    assert len(package.storyboard.frames) == 2
    assert len(package.timing.shots) == 2
    assert package.manifest.validate_dependencies() == []
    assert package.manifest.is_ready_for_production
