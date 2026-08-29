import asyncio

import pytest

from creative_intelligence.executor_registry import ExecutionRequest
from backend.services import creative_revision_executor as revision


def request(payload, artifact_id="artifact-v1"):
    return ExecutionRequest(job_id="job-1", project_id="project-1", stage="revision", payload=payload, artifact_id=artifact_id)


def test_revision_requires_existing_artifact():
    with pytest.raises(ValueError, match="current artifact"):
        asyncio.run(revision.execute_revision(request({"revision_plan": ["Fix pacing."]})))


def test_revision_requires_explicit_council_requests():
    with pytest.raises(ValueError, match="explicit Critic Council"):
        asyncio.run(revision.execute_revision(request({"artifact": "Draft text."})))


def test_revision_preserves_parent_and_requires_recritique(monkeypatch):
    async def fake_send(persona, system, prompt):
        assert persona == "minerva"
        assert "Fix pacing." in prompt
        return {"text": "Revised draft text."}

    monkeypatch.setattr(revision, "send", fake_send)
    result = asyncio.run(revision.execute_revision(request({"artifact": "Draft text.", "revision_plan": ["Fix pacing."]})))
    assert result.output["text"] == "Revised draft text."
    assert result.output["parent_artifact_id"] == "artifact-v1"
    assert result.output["resolved_revision_requests"] == ["Fix pacing."]
    assert result.output["requires_recritique"] is True


def test_revision_fails_closed_on_empty_provider_output(monkeypatch):
    async def fake_send(persona, system, prompt):
        return {"text": ""}

    monkeypatch.setattr(revision, "send", fake_send)
    with pytest.raises(RuntimeError, match="empty revision output"):
        asyncio.run(revision.execute_revision(request({"artifact": "Draft text.", "revision_plan": ["Fix pacing."]})))
