import pytest

from routes import discovery_approval
from services import discovery_approval_pipeline, evidence_scoring, global_source_library as gsl


@pytest.fixture(autouse=True)
def reset_knowledge_state():
    gsl.attach_mongo(None)
    gsl.reset_in_memory_state()
    discovery_approval_pipeline.reset_in_memory_state()


def _register_source(*, name, trust_tier, source_type, ingestion_status, website):
    return gsl.register_source(
        name=name,
        source_type=source_type,
        trust_tier=trust_tier,
        domains=["Robotics"],
        country="International",
        region="International",
        website=website,
        access_method="website",
        owner_ai="Minerva",
        ingestion_status=ingestion_status,
    )


def test_registered_reliable_source_adds_transparent_evidence_assessment():
    official = _register_source(
        name="ATLAS Official Robotics Source",
        trust_tier="tier_1_official",
        source_type="government_agency",
        ingestion_status="approved",
        website="https://example.gov",
    )

    result = evidence_scoring.score_evidence(
        [
            {
                "source_id": official["source_id"],
                "source_type": "government",
                "domain": "Robotics",
                "citation": "Official robotics report",
                "direct_support": True,
            }
        ]
    )

    reliability = result["source_reliability"]
    assessment = reliability["assessments"][0]

    assert reliability["registered_items"] == 1
    assert reliability["unregistered_items"] == 0
    assert reliability["average_score"] >= 90
    assert assessment["source_id"] == official["source_id"]
    assert assessment["evidence_adjustment"] > 0
    assert assessment["domain_match"] is True
    assert "Council approval" in reliability["rule"]


def test_weak_rejected_source_lowers_evidence_and_requires_corroboration():
    weak = _register_source(
        name="ATLAS Weak Robotics Archive",
        trust_tier="tier_5_personal",
        source_type="personal_archive",
        ingestion_status="rejected",
        website=None,
    )

    baseline = evidence_scoring.score_evidence(
        [{"source_type": "unknown", "citation": "Unregistered comparison"}]
    )
    result = evidence_scoring.score_evidence(
        [
            {
                "source_id": weak["source_id"],
                "source_type": "unknown",
                "domain": "Robotics",
                "citation": "Rejected archive note",
            }
        ]
    )

    assessment = result["source_reliability"]["assessments"][0]

    assert assessment["evidence_adjustment"] < 0
    assert assessment["corroboration_required"] is True
    assert result["source_reliability"]["corroboration_required_count"] == 1
    assert result["score"] < baseline["score"]


def test_unregistered_source_id_is_visible_and_penalized_conservatively():
    result = evidence_scoring.score_evidence(
        [
            {
                "source_id": "SRC-missing-source",
                "source_type": "technical_documentation",
                "citation": "Unknown registered origin",
            }
        ]
    )

    reliability = result["source_reliability"]

    assert reliability["registered_items"] == 0
    assert reliability["unregistered_items"] == 1
    assert reliability["unregistered_source_ids"] == ["SRC-missing-source"]
    assert any("not registered" in reason for reason in result["reasons"])


@pytest.mark.asyncio
async def test_discovery_draft_exposes_registered_source_reliability_in_evidence_score():
    official = _register_source(
        name="ATLAS Discovery Source",
        trust_tier="tier_1_official",
        source_type="standards_body",
        ingestion_status="approved",
        website="https://standards.example.org",
    )

    draft = await discovery_approval.create_draft(
        discovery_approval.DraftRequest(
            title="Reliability-aware discovery",
            summary="Discovery Approval should expose source reliability factors without treating them as proof.",
            owner_ai="Minerva",
            evidence=[
                {
                    "source_id": official["source_id"],
                    "source_type": "standards_body",
                    "domain": "Robotics",
                    "citation": "ATLAS robotics standard fixture",
                    "direct_support": True,
                }
            ],
            source_refs=[{"source_id": official["source_id"], "title": official["name"]}],
            related_subjects=["Robotics"],
            related_projects=["Weaver"],
        )
    )

    reliability = draft["evidence_score"]["source_reliability"]

    assert reliability["registered_items"] == 1
    assert reliability["average_score"] >= 90
    assert reliability["assessments"][0]["source_name"] == official["name"]
