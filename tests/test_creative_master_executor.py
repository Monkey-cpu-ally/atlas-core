import asyncio
import pytest
from creative_intelligence.executor_registry import ExecutionRequest
from backend.services.creative_master_executor import REQUIRED_GATES, execute_master

def request(payload, artifact_id="artifact-final"):
    return ExecutionRequest(job_id="job-master", project_id="project-1", stage="master", payload=payload, artifact_id=artifact_id)

def passing_payload():
    return {"artifact":"Final artifact text.","critic_council":{"approved":True,"blockers":[]},"quality_evidence":{gate:{"passed":True} for gate in REQUIRED_GATES}}

def reference_context():
    return {"project_identity":"Original machine-world family drama","project_constraints":["functional machinery"],"reference_ids":["creator:test"],"principles":["visual storytelling"],"limitations":["do not imitate signature forms"],"provenance":["curated profile"],"contract":{"principle_only":True,"project_identity_overrides_reference_influence":True}}

def test_master_gate_approves_only_complete_evidence():
    result=asyncio.run(execute_master(request(passing_payload())))
    assert result.output["approved"] is True; assert result.output["status"]=="master"; assert result.output["artifact_id"]=="artifact-final"; assert result.output["passed_gates"]==list(REQUIRED_GATES)

def test_master_gate_requires_post_revision_council_approval():
    payload=passing_payload(); payload["critic_council"]["approved"]=False
    with pytest.raises(ValueError,match="approved post-revision"): asyncio.run(execute_master(request(payload)))

def test_master_gate_rejects_council_blockers_even_when_approved_flag_is_true():
    payload=passing_payload(); payload["critic_council"]["blockers"]=["hermes:internal_logic"]
    with pytest.raises(ValueError,match="Council blockers"): asyncio.run(execute_master(request(payload)))

def test_master_gate_fails_closed_on_missing_or_failed_evidence():
    payload=passing_payload(); del payload["quality_evidence"]["continuity"]; payload["quality_evidence"]["visual_quality"]={"passed":False}
    with pytest.raises(ValueError) as error: asyncio.run(execute_master(request(payload)))
    assert "missing evidence: continuity" in str(error.value); assert "failed gates: visual_quality" in str(error.value)

def test_master_gate_rejects_unknown_gate_names():
    payload=passing_payload(); payload["applicable_gates"]=["creative_approval","imaginary_gate"]
    with pytest.raises(ValueError,match="unknown master gates: imaginary_gate"): asyncio.run(execute_master(request(payload)))

def test_master_gate_requires_council_reference_boundary_verification():
    payload=passing_payload(); payload["reference_context"]=reference_context()
    with pytest.raises(ValueError,match="verification of reference boundaries"): asyncio.run(execute_master(request(payload)))

def test_master_gate_requires_originality_when_references_participated():
    payload=passing_payload(); payload["reference_context"]=reference_context(); payload["critic_council"]["reference_context_verified"]=True
    payload["applicable_gates"]=["creative_approval","story_quality"]
    with pytest.raises(ValueError,match="originality"): asyncio.run(execute_master(request(payload)))

def test_master_gate_records_verified_reference_boundaries():
    payload=passing_payload(); payload["reference_context"]=reference_context(); payload["critic_council"]["reference_context_verified"]=True
    result=asyncio.run(execute_master(request(payload)))
    assert result.output["approved"] is True; assert result.output["reference_boundaries_verified"] is True; assert "originality" in result.output["passed_gates"]
