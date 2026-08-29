import pytest

from creative_intelligence.executor_registry import ExecutionRequest
from creative_intelligence.story_production import StoryBrief, StoryProductionService, story_create_executor


def test_story_brief_requires_core_fields():
    with pytest.raises(ValueError):
        StoryBrief.from_mapping({"premise": "A haunted mill."})


def test_story_spec_contains_originality_and_quality_directives():
    service = StoryProductionService(lambda spec: "draft")
    spec = service.build_spec(StoryBrief("Two siblings return to a cursed forest.", "adult", "short film", "folk horror"))
    directives = " ".join(spec["directives"]).lower()
    assert "original" in directives
    assert "generic" in directives
    assert "internal logic" in directives
    assert "living creator" in directives


def test_service_rejects_empty_generator_output():
    service = StoryProductionService(lambda spec: "")
    with pytest.raises(RuntimeError):
        service.create(StoryBrief("Premise", "adult", "short story", "horror"))


def test_story_executor_returns_typed_real_artifact():
    service = StoryProductionService(lambda spec: "The finished original draft.")
    executor = story_create_executor(service)
    result = executor(ExecutionRequest(
        job_id="j1", project_id="p1", stage="create",
        payload={"premise": "A witch bargains with two siblings.", "audience": "adult", "medium": "short film", "tone": "horror"},
    ))
    assert result.executor == "story-production-service"
    assert result.artifact_id
    assert result.output["text"] == "The finished original draft."
