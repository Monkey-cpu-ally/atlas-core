import json
import pytest
from creative_intelligence.executor_registry import ExecutionRequest
from backend.services import creative_critique_executor as executor


def reference_context():
    return {"query":"visual storytelling","project_identity":"original industrial story","project_constraints":["no gore"],"diversity_dimensions":["creator:animation","work:film"],"reference_ids":["creator:a","work:b"],"principles":["strong silhouettes"],"study_targets":["visual clarity"],"limitations":["do not imitate distinctive expression"],"provenance":["curated source"],"contract":{"principle_only":True,"project_identity_overrides_reference_influence":True}}


def review(boundary=True):
    scores={"concept_and_intent":90,"structure_and_pacing":90,"character_and_emotion":90,"dialogue_and_voice":90,"world_and_continuity":90,"originality_and_specificity":90,"craft_and_clarity":90}
    return {"scores":scores,"findings":[],"revision_requests":[],"reference_boundary_check":{"passed":boundary,"project_alignment":boundary,"constraints_respected":boundary,"anti_imitation":boundary,"findings":[] if boundary else ["boundary violation"]}}


@pytest.mark.asyncio
async def test_critics_must_prove_reference_boundaries(monkeypatch):
    async def fake_send(*args): return {"text":json.dumps(review(True))}
    monkeypatch.setattr(executor,"send",fake_send)
    result=await executor.execute_critique(ExecutionRequest("job","project","critique","artifact",{"artifact":"Original scene.","reference_context":reference_context()}))
    assert result.output["reference_boundaries_verified"] is True
    assert len(result.output["reference_boundary_checks"])==3


@pytest.mark.asyncio
async def test_missing_reference_boundary_evidence_fails_closed(monkeypatch):
    payload=review(True); payload.pop("reference_boundary_check")
    async def fake_send(*args): return {"text":json.dumps(payload)}
    monkeypatch.setattr(executor,"send",fake_send)
    with pytest.raises(ValueError,match="reference_boundary_check"):
        await executor.execute_critique(ExecutionRequest("job","project","critique","artifact",{"artifact":"Scene.","reference_context":reference_context()}))


@pytest.mark.asyncio
async def test_failed_reference_boundary_blocks_verification(monkeypatch):
    async def fake_send(*args): return {"text":json.dumps(review(False))}
    monkeypatch.setattr(executor,"send",fake_send)
    result=await executor.execute_critique(ExecutionRequest("job","project","critique","artifact",{"artifact":"Scene.","reference_context":reference_context()}))
    assert result.output["reference_boundaries_verified"] is False
    assert any("reference_boundary" in blocker for blocker in result.output["blockers"])
