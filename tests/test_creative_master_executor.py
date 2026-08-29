import asyncio

import pytest

from creative_intelligence.executor_registry import ExecutionRequest
from backend.services.creative_master_executor import REQUIRED_GATES, execute_master


def request(payload, artifact_id="artifact-final"):
    return ExecutionRequest(job_id="job-master", project_id="project-1", stage="master", payload=payload, artifact_id=artifact_id)


def passing_payload():
    return {
        "artifact": "Final artifact text.",
        "critic_council": {"approved": True, "blockers": []},
        "quality_evidence": {gate: {"passed": True} for gate in REQUIRED_GATES},
    }


def test_master_gate_approves_only_complete_evidence():
    result = asyncio.run(execute_master(request(passing_payload())))
    assert result.output["approved"] is True
    assert result.output["status"] == "master"
    assert result.output["artifact_id"] == "artifact-final"
    assert result.output["passed_gates"] == list(REQUIRED_GATES)


def test_master_gate_requires_post_revision_council_approval():
    payload = passing_payload()
    payload["critic_council"]["approved"] = False
    with pytest.raises(ValueError, match="approved post-revision"):
        asyncio.run(execute_master(request(payload)))


def test_master_gate_rejects_council_blockers_even_when_approved_flag_is_true():
    payload = passing_payload()
    payload["critic_council"]["blockers"] = ["hermes:internal_logic"]
    with pytest.raises(ValueError, match="Council blockers"):
        asyncio.run(execute_master(request(payload)))


def test_master_gate_fails_closed_on_missing_or_failed_evidence():
    payload = passing_payload()
    del payload["quality_evidence"]["continuity"]
    payload["quality_evidence"]["visual_quality"] = {"passed": False}
    with pytest.raises(ValueError) as error:
        asyncio.run(execute_master(request(payload)))
    message = str(error.value)
    assert "missing evidence: continuity" in message
    assert "failed gates: visual_quality" in message


def test_master_gate_rejects_unknown_gate_names():
    payload = passing_payload()
    payload["applicable_gates"] = ["creative_approval", "imaginary_gate"]
    with pytest.raises(ValueError, match="unknown master gates: imaginary_gate"):
        asyncio.run(execute_master(request(payload)))
