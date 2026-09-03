import pytest
from fastapi import HTTPException
from backend.routes.creative_studio import list_references,retrieve_references,synthesize_references
@pytest.mark.asyncio
async def test_reference_list_exposes_deep_profile_fields():
    p=await list_references(q="Syd Mead"); assert p["items"]; r=p["items"][0]
    for f in ("disciplines","techniques","strengths","study_targets","limitations","provenance","relationships"): assert f in r
    assert r["provenance"] and r["limitations"]
@pytest.mark.asyncio
async def test_ranked_reference_api_exposes_explainable_contract():
    p=await retrieve_references(q="industrial science fiction design",limit=4,kind=None); assert p["items"] and all(i["score"]>0 and i["matched_terms"] for i in p["items"]); assert p["retrieval_contract"]=={"ranked":True,"explainable":True,"vector_ready":True,"principle_only":True}
@pytest.mark.asyncio
async def test_synthesis_api_preserves_constraints_as_boundaries_not_inspiration():
    p=await synthesize_references(q="minimal dialogue visual storytelling",limit=4,minimum_references=2,project_identity="original industrial science-fiction story",project_constraints=["functional machinery","avoid copied designs"]); assert len(p["references"])>=2; assert p["principles"] and p["study_targets"] and p["provenance"] and p["limitations"]; assert p["project_identity"]=="original industrial science-fiction story"; assert p["project_constraints"]==["functional machinery","avoid copied designs"]; assert p["synthesis_contract"]=={"multi_reference":True,"deterministic":True,"principle_only":True,"provenance_preserved":True,"anti_imitation_boundaries_preserved":True,"project_identity_overrides_reference_influence":True,"project_constraints_preserved":True,"constraints_are_not_inspiration":True,"diversity_aware_selection":True}
@pytest.mark.asyncio
async def test_synthesis_api_rejects_duplicate_constraints():
    with pytest.raises(HTTPException) as exc:
        await synthesize_references(q="visual storytelling",limit=4,minimum_references=2,project_identity="original project",project_constraints=["No gore","no gore"])
    assert exc.value.status_code==422; assert "duplicate project constraints" in str(exc.value.detail)
@pytest.mark.asyncio
async def test_synthesis_api_fails_closed_when_contract_cannot_be_met():
    with pytest.raises(HTTPException) as exc:
        await synthesize_references(q="zzzzzz-no-reference-match",limit=4,minimum_references=2,project_identity="",project_constraints=[])
    assert exc.value.status_code==422; assert "insufficient references" in str(exc.value.detail)
