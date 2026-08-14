from pathlib import Path

from creative_intelligence.agent_context import AgentCreativeContextService
from creative_intelligence.creative_memory import CreativeMemory
from creative_intelligence.media_analysis.ingestion import ReferenceIngestionService
from creative_intelligence.media_analysis.providers import CallableVisionProvider


def test_image_ingestion_becomes_agent_context(tmp_path: Path):
    image = tmp_path / "reference.jpg"
    image.write_bytes(b"fixture")

    def model(_request):
        return {
            "silhouette": ["clear asymmetric silhouette"],
            "color": ["restrained palette with one focal accent"],
            "lighting": ["rim separation around the subject"],
            "composition": ["diagonal hierarchy leads toward the focal point"],
        }

    memory = CreativeMemory()
    ingestion = ReferenceIngestionService(CallableVisionProvider(model), memory)
    result = ingestion.study_image(
        project="Hyper Axel",
        source_name="approved-reference",
        image_path=str(image),
    )

    assert result.learned_lessons > 0
    packet = AgentCreativeContextService(memory).retrieve(
        agent="Hermes",
        project="Hyper Axel",
        query="",
    )
    prompt = packet.to_prompt_context()
    assert packet.lessons
    assert "HERMES" in prompt
    assert "copy a source's distinctive expression" in prompt


def test_agent_context_rejects_unknown_agent():
    memory = CreativeMemory()
    service = AgentCreativeContextService(memory)
    try:
        service.retrieve(agent="unknown", project="x", query="y")
    except ValueError as exc:
        assert "Ajani, Minerva, or Hermes" in str(exc)
    else:
        raise AssertionError("unknown agent should be rejected")
