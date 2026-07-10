import pytest
from fastapi import HTTPException

from routes import global_sources
from services import global_source_library as gsl
from services import source_reliability


@pytest.fixture(autouse=True)
def reset_source_state():
    gsl.attach_mongo(None)
    gsl.reset_in_memory_state()


def _register_sources():
    official = gsl.register_source(
        name="ATLAS Official Test Agency",
        source_type="government_agency",
        trust_tier="tier_1_official",
        domains=["Robotics", "Standards"],
        country="United States",
        region="North America",
        website="https://example.gov",
        access_method="api",
        owner_ai="Minerva",
        ingestion_status="approved",
    )
    community = gsl.register_source(
        name="ATLAS Community Notes",
        source_type="media_source",
        trust_tier="tier_4_community",
        domains=["Robotics"],
        country="International",
        region="International",
        website=None,
        access_method="not_connected",
        owner_ai="Council",
        ingestion_status="candidate",
    )
    rejected = gsl.register_source(
        name="ATLAS Rejected Archive",
        source_type="personal_archive",
        trust_tier="tier_5_personal",
        domains=["Robotics"],
        country="Personal",
        region="Personal",
        website=None,
        access_method="manual_review",
        owner_ai="Council",
        ingestion_status="rejected",
    )
    return official, community, rejected


def test_official_reviewed_source_outranks_community_and_rejected_sources():
    official, community, rejected = _register_sources()

    official_report = source_reliability.assess_source(official, domain="Robotics")
    community_report = source_reliability.assess_source(community, domain="Robotics")
    rejected_report = source_reliability.assess_source(rejected, domain="Robotics")

    assert official_report["reliability_score"] > community_report["reliability_score"]
    assert community_report["reliability_score"] > rejected_report["reliability_score"]
    assert official_report["reliability_band"] == "verified_priority"
    assert rejected_report["reliability_band"] == "restricted"
    assert rejected_report["eligible_for_automatic_priority"] is False
    assert "Source is not approved for ingestion." in rejected_report["warnings"]


def test_domain_mismatch_reduces_score_and_requires_warning():
    official, _, _ = _register_sources()

    matched = source_reliability.assess_source(official, domain="Robotics")
    mismatched = source_reliability.assess_source(official, domain="Medicine")

    assert matched["domain_match"] is True
    assert mismatched["domain_match"] is False
    assert matched["reliability_score"] > mismatched["reliability_score"]
    assert any("Medicine" in warning for warning in mismatched["warnings"])


def test_rank_sources_filters_by_minimum_score_and_orders_descending():
    official, community, rejected = _register_sources()

    ranking = source_reliability.rank_sources(
        [community, rejected, official],
        domain="Robotics",
        minimum_score=50,
        limit=10,
    )

    scores = [item["reliability_score"] for item in ranking["items"]]
    assert scores == sorted(scores, reverse=True)
    assert ranking["items"][0]["source_id"] == official["source_id"]
    assert all(score >= 50 for score in scores)
    assert rejected["source_id"] not in {item["source_id"] for item in ranking["items"]}
    assert "verified_priority" in ranking["policy"]


@pytest.mark.asyncio
async def test_source_reliability_route_returns_transparent_assessment():
    official, _, _ = _register_sources()

    response = await global_sources.source_reliability_report(
        official["source_id"],
        domain="Robotics",
    )

    assert response["source_id"] == official["source_id"]
    assert response["reliability_score"] >= 90
    assert response["factors"]["trust_tier_base"] == 92
    assert response["domain_match"] is True
    assert "does not prove individual claims" in response["rule"]


@pytest.mark.asyncio
async def test_reliability_rankings_route_uses_global_source_library():
    official, community, _ = _register_sources()

    response = await global_sources.reliability_rankings(
        domain="Robotics",
        minimum_score=0,
        limit=10,
    )

    assert response["title"] == "ATLAS Source Reliability Ranking"
    assert response["count"] == 3
    assert response["items"][0]["source_id"] == official["source_id"]
    assert any(item["source_id"] == community["source_id"] for item in response["items"])


@pytest.mark.asyncio
async def test_missing_source_reliability_route_returns_404():
    with pytest.raises(HTTPException) as exc:
        await global_sources.source_reliability_report("missing-source")

    assert exc.value.status_code == 404
