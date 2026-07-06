from services import global_knowledge_network as gkn


def setup_function():
    gkn.reset_in_memory_state()


def test_seed_foundation_registry_creates_global_sources():
    result = gkn.seed_foundation_registry()
    summary = gkn.global_summary()

    assert result["created_or_updated"] >= 10
    assert summary["institution_count"] >= 10
    assert summary["country_count"] >= 8
    assert summary["regions"]["Asia"] > 0
    assert summary["regions"]["Europe"] > 0
    assert summary["regions"]["North America"] > 0
    assert summary["trust_tiers"]["tier_1_official"] > 0


def test_institution_filters_by_country_owner_and_discipline():
    gkn.seed_foundation_registry()

    japan = gkn.list_institutions(country="Japan")
    hermes = gkn.list_institutions(owner="Hermes")
    robotics = gkn.list_institutions(discipline="Robotics")

    assert any(item["name"] == "JAXA" for item in japan)
    assert all(item["primary_ai_owner"] == "Hermes" for item in hermes)
    assert any("Robotics" in item["primary_disciplines"] for item in robotics)


def test_create_institution_rejects_invalid_region():
    try:
        gkn.create_institution(
            name="Invalid Research Org",
            country="Nowhere",
            region="Moon Base",
            organization_type="test",
            primary_disciplines=["Robotics"],
            research_strengths=["testing"],
            trust_tier="tier_2_academic",
            evidence_level="test evidence",
            primary_ai_owner="Minerva",
        )
    except ValueError as exc:
        assert "invalid region" in str(exc)
    else:
        raise AssertionError("Expected invalid region to fail")


def test_create_institution_rejects_invalid_ai_owner():
    try:
        gkn.create_institution(
            name="Invalid Owner Org",
            country="United States",
            region="North America",
            organization_type="test",
            primary_disciplines=["AI"],
            research_strengths=["testing"],
            trust_tier="tier_2_academic",
            evidence_level="test evidence",
            primary_ai_owner="Unknown",
        )
    except ValueError as exc:
        assert "invalid primary_ai_owner" in str(exc)
    else:
        raise AssertionError("Expected invalid AI owner to fail")
