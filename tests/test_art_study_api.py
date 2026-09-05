import pytest
from fastapi import HTTPException

from backend.routes.creative_studio import ArtStudyRequest, analyze_art_study, get_art_study_contract
from backend.services import art_study_provider_registry
from creative_intelligence.vision_provider import VisionProvider


class FakeVisionProvider(VisionProvider):
    @property
    def provider_id(self): return "api-test-vision"
    def analyze(self, source_reference, request):
        return {"provider":self.provider_id,"evidence":[{"locator":"frame:1 subject","dimension":"shape_and_silhouette","observation":"Readable silhouette","confidence":0.98}]}


def body(rights="user_provided"):
    return ArtStudyRequest(source_reference="asset://frame-1",request={"study":["silhouette"]},source={"source_id":"api-study-1","medium":"ink animation","source_kind":"animation frame","rights_basis":rights,"transferable_principles":["Solve silhouette first"],"construction_steps":["Gesture","Silhouette","Detail"],"limitations":["Do not imitate or copy distinctive creator expression"],"provenance":["user-authorized source"]},project_identity="ATLAS original production",project_constraints=["preserve character model","no generic AI look"])


@pytest.fixture(autouse=True)
def clean_registry():
    art_study_provider_registry.clear(); yield; art_study_provider_registry.clear()


@pytest.mark.asyncio
async def test_art_study_api_fails_closed_without_provider():
    with pytest.raises(HTTPException) as exc: await analyze_art_study(body())
    assert exc.value.status_code==503


@pytest.mark.asyncio
async def test_art_study_api_runs_full_safe_runtime_contract():
    art_study_provider_registry.register(FakeVisionProvider())
    result=await analyze_art_study(body())
    assert result["technique_profile"]["source_ids"]==["api-study-1"]
    assert set(result["ai_interpretations"])=={"ajani","minerva","hermes"}
    assert result["visual_direction"]["project_identity"]=="ATLAS original production"
    assert result["visual_direction"]["project_constraints"]==["preserve character model","no generic AI look"]
    assert result["runtime_contract"]["direct_imitation_forbidden"] is True


@pytest.mark.asyncio
async def test_art_study_api_rejects_unapproved_source_rights():
    art_study_provider_registry.register(FakeVisionProvider())
    with pytest.raises(HTTPException) as exc: await analyze_art_study(body("scraped_unknown"))
    assert exc.value.status_code==422


@pytest.mark.asyncio
async def test_art_study_contract_reports_provider_and_safety_state():
    contract=await get_art_study_contract(); assert contract["provider"]["configured"] is False
    assert contract["provider"]["fail_closed_when_unconfigured"] is True
    assert contract["principles_only"] is True and contract["project_identity_authoritative"] is True
