import pytest

from creative_intelligence.executor_registry import ExecutionRequest
from creative_intelligence.story_production import StoryBrief, StoryProductionService, story_create_executor


def test_story_brief_requires_core_fields():
    with pytest.raises(ValueError): StoryBrief.from_mapping({"premise": "A haunted mill."})


def test_story_spec_contains_originality_and_quality_directives():
    service = StoryProductionService(lambda spec: "draft")
    spec = service.build_spec(StoryBrief("Two siblings return to a cursed forest.", "adult", "short film", "folk horror"))
    directives = " ".join(spec["directives"]).lower()
    assert "original" in directives and "generic" in directives and "internal logic" in directives and "living creator" in directives
    assert "project identity" in directives and "anti-imitation" in directives


def test_story_brief_validates_reference_context_fail_closed():
    base = {"premise": "Premise", "audience": "adult", "medium": "story", "tone": "horror"}
    with pytest.raises(ValueError, match="reference_context must be an object"):
        StoryBrief.from_mapping({**base, "reference_context": "unsafe"})
    with pytest.raises(ValueError, match="principle-only"):
        StoryBrief.from_mapping({**base, "reference_context": {"contract": {"principle_only": False}}})
    with pytest.raises(ValueError, match="project_constraints must be a list"):
        StoryBrief.from_mapping({**base, "reference_context": {"project_constraints": "no copying"}})


@pytest.mark.asyncio
async def test_service_rejects_empty_generator_output():
    service = StoryProductionService(lambda spec: "")
    with pytest.raises(RuntimeError): await service.create(StoryBrief("Premise", "adult", "short story", "horror"))


@pytest.mark.asyncio
async def test_story_executor_returns_typed_real_artifact():
    service = StoryProductionService(lambda spec: "The finished original draft."); executor = story_create_executor(service)
    result = await executor(ExecutionRequest(job_id="j1", project_id="p1", stage="create", payload={"premise": "A witch bargains with two siblings.", "audience": "adult", "medium": "short film", "tone": "horror"}))
    assert result.executor == "story-production-service" and result.artifact_id and result.output["text"] == "The finished original draft."


@pytest.mark.asyncio
async def test_story_executor_delivers_reference_intelligence_to_generator():
    captured = {}
    async def generator(spec):
        captured.update(spec); return "An original project-defined draft."
    service = StoryProductionService(generator); executor = story_create_executor(service)
    context = {
        "query": "minimal dialogue industrial design", "project_identity": "Original machine-world family drama",
        "project_constraints": ["functional machinery", "no copied designs"], "diversity_dimensions": ["creator:animation", "work:film"],
        "reference_ids": ["creator:test", "work:test"], "principles": ["visual storytelling", "functional silhouette"],
        "study_targets": ["pacing", "machine architecture"], "limitations": ["do not imitate signature forms"],
        "provenance": ["curated profile A", "curated profile B"],
        "contract": {"principle_only": True, "project_identity_overrides_reference_influence": True},
    }
    result = await executor(ExecutionRequest(job_id="j2", project_id="p2", stage="create", payload={"premise": "A family repairs a dying machine city.", "audience": "general", "medium": "story", "tone": "project-defined", "reference_context": context}))
    delivered = captured["reference_context"]
    assert delivered["project_identity"] == context["project_identity"]
    assert delivered["project_constraints"] == tuple(context["project_constraints"])
    assert delivered["reference_ids"] == tuple(context["reference_ids"])
    assert delivered["principles"] == tuple(context["principles"])
    assert delivered["limitations"] == tuple(context["limitations"])
    assert delivered["provenance"] == tuple(context["provenance"])
    assert result.output["spec"]["reference_context"] == delivered
