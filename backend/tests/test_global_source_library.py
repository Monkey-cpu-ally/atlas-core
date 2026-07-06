from services import global_source_library as gsl


def setup_function():
    gsl.reset_in_memory_state()


def test_seed_foundation_sources_creates_global_catalog():
    result = gsl.seed_foundation_sources()
    summary = gsl.source_summary()

    assert result["created_or_updated"] >= 25
    assert summary["source_count"] >= 25
    assert summary["country_count"] >= 10
    assert summary["trust_tiers"]["tier_1_official"] >= 10
    assert summary["owner_ai"]["Hermes"] >= 1
    assert summary["owner_ai"]["Minerva"] >= 1


def test_filter_sources_by_domain_country_and_type():
    gsl.seed_foundation_sources()

    robotics = gsl.list_sources(domain="Robotics")
    japan = gsl.list_sources(country="Japan")
    standards = gsl.list_sources(source_type="standards_body")

    assert any(item["name"] == "NASA" for item in robotics)
    assert any(item["name"] == "JAXA" for item in japan)
    assert any(item["name"] == "ISO" for item in standards)


def test_register_source_rejects_invalid_tier():
    try:
        gsl.register_source(
            name="Bad Source",
            source_type="documentation",
            trust_tier="not_real",
            domains=["Testing"],
        )
    except ValueError as exc:
        assert "invalid trust_tier" in str(exc)
    else:
        raise AssertionError("Expected invalid trust tier to fail")


def test_mark_reviewed_updates_status():
    source = gsl.register_source(
        name="Review Source",
        source_type="documentation",
        trust_tier="tier_1_official",
        domains=["Software Engineering"],
        owner_ai="Ajani",
    )
    reviewed = gsl.mark_reviewed(
        source_id=source["source_id"],
        reviewer="Council",
        ingestion_status="approved",
        notes="Approved for manual review ingestion.",
    )

    assert reviewed["ingestion_status"] == "approved"
    assert reviewed["reviewer"] == "Council"
    assert reviewed["last_reviewed_at"] is not None
