"""Tests for the subject-aware bridge layered on the existing research pipeline."""
import pytest

from services.research_orchestrator_bridge import orchestrate_research


@pytest.mark.asyncio
async def test_orchestrator_resolves_subject_and_existing_resources_without_live_web():
    result = await orchestrate_research(
        subject="robotics",
        query="software engineering",
        top_n=5,
        use_live_web=False,
        ingest_catalog_resources=False,
    )
    assert result["kind"] == "orchestrated_research"
    assert result["subject"] == "Robotics"
    assert "nasa_ntrs" in result["preferred_sources"]
    assert result["all_personas_have_access"] is True
    assert result["live_web"] is None
    assert result["existing_resources"]
    assert any("Robotics" in r.get("subjects", []) for r in result["existing_resources"])


@pytest.mark.asyncio
async def test_orchestrator_rejects_unknown_subject():
    with pytest.raises(ValueError):
        await orchestrate_research(
            subject="not-a-real-atlas-subject",
            query="test",
            use_live_web=False,
        )


@pytest.mark.asyncio
async def test_orchestrator_does_not_ingest_catalog_unless_requested():
    result = await orchestrate_research(
        subject="Artificial Intelligence",
        query="software engineering",
        use_live_web=False,
        ingest_catalog_resources=False,
    )
    assert result["catalog_ingestion"]["requested"] is False
    assert result["catalog_ingestion"]["ingested"] == []
    assert result["catalog_ingestion"]["errors"] == []
