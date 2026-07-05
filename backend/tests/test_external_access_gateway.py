from services import external_access_gateway as gateway


def setup_function():
    gateway.reset_in_memory_state()


def test_seed_default_connections_creates_expected_sources():
    result = gateway.seed_default_connections()
    connector_types = {item["connector_type"] for item in result["items"]}

    assert result["created_or_updated"] >= 6
    assert "ivytech" in connector_types
    assert "youtube" in connector_types
    assert "gallery" in connector_types
    assert "figma" in connector_types
    assert "google_drive" in connector_types
    assert "cad" in connector_types


def test_connection_requires_valid_permission_level():
    try:
        gateway.create_connection(
            name="Bad Connector",
            connector_type="youtube",
            purpose="Test invalid permissions.",
            owner_ai="Council",
            permission_level="unlimited",
        )
    except gateway.ExternalAccessError as exc:
        assert "invalid permission_level" in str(exc)
    else:
        raise AssertionError("Expected invalid permission to fail")


def test_import_plan_respects_connection_state_and_permission():
    conn = gateway.create_connection(
        name="Approved YouTube Channel",
        connector_type="youtube",
        purpose="Summarize approved public learning videos.",
        owner_ai="Minerva",
        permission_level="read_approved",
        status="connected",
    )

    plan = gateway.create_import_plan(
        connection_id=conn["connection_id"],
        requested_scope="Approved robotics learning playlist",
        related_projects=["project:weaver"],
    )

    assert plan["import_plan_id"].startswith("IMPORT-")
    assert plan["connection_id"] == conn["connection_id"]
    assert plan["owner_ai"] == "Minerva"
    assert plan["require_council_review"] is True
    assert gateway.get_connection(conn["connection_id"])["last_import_plan_id"] == plan["import_plan_id"]
