import asyncio
import json
import pytest
from creative_intelligence.executor_registry import ExecutionRequest
from backend.services import creative_revision_executor as revision

def request(payload, artifact_id="artifact-v1"):
    return ExecutionRequest(job_id="job-1", project_id="project-1", stage="revision", payload=payload, artifact_id=artifact_id)

def reference_context():
    return {"project_identity":"Original machine-world family drama","project_constraints":["functional machinery","no copied designs"],"reference_ids":["creator:test"],"principles":["visual storytelling"],"study_targets":["pacing"],"limitations":["do not imitate signature forms"],"provenance":["curated profile"],"contract":{"principle_only":True,"project_identity_overrides_reference_influence":True,"project_constraints_preserved":True,"constraints_are_not_inspiration":True}}

def test_revision_requires_existing_artifact():
    with pytest.raises(ValueError, match="current artifact"): asyncio.run(revision.execute_revision(request({"revision_plan":["Fix pacing."]})))

def test_revision_requires_explicit_council_requests():
    with pytest.raises(ValueError, match="explicit Critic Council"): asyncio.run(revision.execute_revision(request({"artifact":"Draft text."})))

def test_revision_preserves_parent_and_requires_recritique(monkeypatch):
    async def fake_send(persona, system, prompt):
        assert persona == "minerva"; assert "Fix pacing." in prompt; return {"text":"Revised draft text."}
    monkeypatch.setattr(revision,"send",fake_send)
    result=asyncio.run(revision.execute_revision(request({"artifact":"Draft text.","revision_plan":["Fix pacing."]})))
    assert result.output["text"]=="Revised draft text."; assert result.output["parent_artifact_id"]=="artifact-v1"; assert result.output["resolved_revision_requests"]==["Fix pacing."]; assert result.output["requires_recritique"] is True

def test_revision_delivers_reference_boundaries_to_minerva(monkeypatch):
    captured={}
    async def fake_send(persona, system, prompt):
        captured.update(json.loads(prompt)); assert "project identity" in system.lower(); assert "anti-imitation" in system.lower(); return {"text":"Boundary-preserving revision."}
    monkeypatch.setattr(revision,"send",fake_send)
    result=asyncio.run(revision.execute_revision(request({"artifact":"Draft.","revision_plan":["Strengthen causality."],"reference_context":reference_context()})))
    assert captured["reference_context"]["project_identity"]=="Original machine-world family drama"
    assert captured["reference_context"]["project_constraints"]==["functional machinery","no copied designs"]
    assert captured["reference_context"]["limitations"]==["do not imitate signature forms"]
    assert result.output["reference_context_preserved"] is True

def test_revision_rejects_unsafe_reference_contract(monkeypatch):
    context=reference_context(); context["contract"]["principle_only"]=False
    with pytest.raises(ValueError, match="principle-only"): asyncio.run(revision.execute_revision(request({"artifact":"Draft.","revision_plan":["Fix pacing."],"reference_context":context})))

def test_revision_fails_closed_on_empty_provider_output(monkeypatch):
    async def fake_send(persona, system, prompt): return {"text":""}
    monkeypatch.setattr(revision,"send",fake_send)
    with pytest.raises(RuntimeError, match="empty revision output"): asyncio.run(revision.execute_revision(request({"artifact":"Draft text.","revision_plan":["Fix pacing."]})))
