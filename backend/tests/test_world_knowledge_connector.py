"""Tests for the ATLAS World Knowledge Connector Engine.

These tests intentionally avoid live web/API calls. The first connector layer
must be deterministic: registry loading, filtering, stats, dry-run job planning,
and knowledge record templates.
"""
import pytest

from services import world_knowledge_connector as wkc


def test_source_registry_loads():
    registry = wkc.load_source_registry()
    assert registry["schema_version"] == "1.0"
    assert isinstance(registry.get("sources"), list)
    assert len(registry["sources"]) >= 50


def test_sources_include_core_global_sources():
    ids = {source["id"] for source in wkc.list_sources()}
    assert "nasa" in ids
    assert "jaxa" in ids
    assert "pubmed" in ids
    assert "ieee" in ids
    assert "github" in ids


def test_filter_by_ai_owner():
    ajani_sources = wkc.list_sources(ai_owner="Ajani")
    assert ajani_sources
    assert all(source["ai_owner"] == "Ajani" for source in ajani_sources)


@pytest.mark.parametrize("country,expected_id", [
    ("Japan", "jaxa"),
    ("India", "isro"),
    ("Taiwan", "itri_taiwan"),
])
def test_filter_by_country(country, expected_id):
    sources = wkc.list_sources(country=country)
    ids = {source["id"] for source in sources}
    assert expected_id in ids


def test_stats_shape():
    stats = wkc.stats()
    assert stats["status"] == "registered_not_live_synced"
    assert stats["total_sources"] >= 50
    assert "Ajani" in stats["by_owner"]
    assert "Hermes" in stats["by_owner"]
    assert "Minerva" in stats["by_owner"]
    assert "Council" in stats["by_owner"]


def test_plan_sync_job_is_dry_run():
    job = wkc.plan_sync_job("nasa", mission="Check aerospace robotics updates")
    assert job["source_id"] == "nasa"
    assert job["ai_owner"] == "Ajani"
    assert job["status"] == "planned"
    assert job["dry_run"] is True
    assert job["connector_type"] in {"rss", "api", "web_metadata", "github", "youtube", "patent"}


def test_knowledge_record_template_keeps_citation_backlink():
    record = wkc.build_knowledge_record_template(
        "jaxa",
        title="Sample JAXA robotics note",
        summary="ATLAS summary written in its own words for a dry-run test.",
    )
    assert record["source_id"] == "jaxa"
    assert record["source_name"] == "Japan Aerospace Exploration Agency"
    assert record["original_url"]
    assert record["summary_in_own_words"].startswith("ATLAS summary")
    assert record["verification_status"] == "single_source"
    assert record["version"] == 1


def test_unknown_source_raises_error():
    with pytest.raises(wkc.WorldKnowledgeError):
        wkc.plan_sync_job("not-a-real-source")
