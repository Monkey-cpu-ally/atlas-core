import pytest

from creative_intelligence.executor_registry import (
    CreativeExecutorRegistry,
    ExecutionRequest,
    ExecutionResult,
    ExecutorUnavailable,
)


def request(stage="create"):
    return ExecutionRequest(job_id="j1", project_id="p1", stage=stage)


def test_registry_fails_closed_without_real_executor():
    registry = CreativeExecutorRegistry()
    with pytest.raises(ExecutorUnavailable):
        registry.execute(request())


def test_registered_executor_returns_real_result_contract():
    registry = CreativeExecutorRegistry()
    registry.register("create", lambda req: ExecutionResult("a1", {"text": "draft"}, "story-service"))
    result = registry.execute(request())
    assert result.artifact_id == "a1"
    assert result.executor == "story-service"


def test_executor_cannot_return_untyped_placeholder():
    registry = CreativeExecutorRegistry()
    registry.register("create", lambda req: {"fake": "done"})
    with pytest.raises(TypeError):
        registry.execute(request())


def test_capabilities_reflect_only_registered_services():
    registry = CreativeExecutorRegistry()
    registry.register("critique", lambda req: ExecutionResult(req.artifact_id, {}, "critic"))
    assert registry.capabilities() == {
        "create": False,
        "critique": True,
        "revision": False,
        "master": False,
    }
