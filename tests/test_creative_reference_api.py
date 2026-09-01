import pytest
from fastapi import HTTPException

from backend.routes.creative_studio import list_references, retrieve_references, synthesize_references


@pytest.mark.asyncio
async def test_reference_list_exposes_deep_profile_fields():
    payload = await list_references(q="Syd Mead")
    assert payload["items"]
    reference = payload["items"][0]
    for field in ("disciplines", "techniques", "strengths", "study_targets", "limitations", "provenance", "relationships"):
        assert field in reference
    assert reference["provenance"]
    assert reference["limitations"]


@pytest.mark.asyncio
async def test_ranked_reference_api_exposes_explainable_contract():
    payload = await retrieve_references(q="industrial science fiction design", limit=4, kind=None)
    assert payload["items"]
    assert all(item["score"] > 0 for item in payload["items"])
    assert all(item["matched_terms"] for item in payload["items"])
    assert payload["retrieval_contract"] == {"ranked": True, "explainable": True, "vector_ready": True, "principle_only": True}


@pytest.mark.asyncio
async def test_synthesis_api_preserves_provenance_and_project_contract():
    payload = await synthesize_references(
        q="minimal dialogue visual storytelling",
        limit=4,
        minimum_references=2,
        project_identity="original industrial science-fiction story",
        project_constraints=["functional machinery", "avoid copied designs", "functional machinery"],
    )
    assert len(payload["references"]) >= 2
    assert payload["principles"] and payload["study_targets"] and payload["provenance"] and payload["limitations"]
    assert any("do not" in limitation.casefold() for limitation in payload["limitations"])
    assert payload["project_identity"] == "original industrial science-fiction story"
    assert payload["project_constraints"] == ["functional machinery", "avoid copied designs"]
    assert payload["diversity_dimensions"]
    assert len(payload["diversity_dimensions"]) == len(set(payload["diversity_dimensions"]))
    assert payload["synthesis_contract"] == {
        "multi_reference": True,
        "deterministic": True,
        "principle_only": True,
        "provenance_preserved": True,
        "anti_imitation_boundaries_preserved": True,
        "project_identity_overrides_reference_influence": True,
        "project_constraints_applied_to_retrieval": True,
        "diversity_aware_selection": True,
    }


@pytest.mark.asyncio
async def test_synthesis_api_fails_closed_when_contract_cannot_be_met():
    with pytest.raises(HTTPException) as exc_info:
        await synthesize_references(q="zzzzzz-no-reference-match", limit=4, minimum_references=2, project_identity="", project_constraints=[])
    assert exc_info.value.status_code == 422
    assert "insufficient references" in str(exc_info.value.detail)
