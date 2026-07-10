from services import atlas_os_control_plane as control_plane


def test_registry_is_valid_and_has_core_services():
    result = control_plane.validate_registry()

    assert result["valid"] is True
    assert result["service_count"] >= 8
    assert "engineering_os" in result["startup_order"]
    assert "knowledge_bank" in result["startup_order"]
    assert result["duplicate_routes"] == {}


def test_dependencies_are_ordered_before_dependents():
    order = control_plane.dependency_order()

    assert order.index("knowledge_graph") < order.index("knowledge_bank")
    assert order.index("knowledge_bank") < order.index("digital_twin")
    assert order.index("engineering_os") < order.index("mission_scheduler")
    assert order.index("engineering_os") < order.index("project_intelligence")


def test_service_filters_support_ai_ownership_and_category():
    hermes_services = control_plane.list_services(owner_ai="Hermes")
    knowledge_services = control_plane.list_services(category="knowledge")

    assert hermes_services
    assert all(item["owner_ai"] == "Hermes" for item in hermes_services)
    assert knowledge_services
    assert all(item["category"] == "knowledge" for item in knowledge_services)


def test_platform_summary_exposes_operational_map():
    summary = control_plane.platform_summary()

    assert summary["platform"] == "AtlasOS"
    assert summary["status"] == "operational"
    assert summary["service_count"] == len(summary["services"])
    assert summary["owners"]["Hermes"] >= 1
    assert summary["owners"]["Minerva"] >= 1
    assert summary["owners"]["Ajani"] >= 1


def test_unknown_service_returns_none():
    assert control_plane.get_service("does_not_exist") is None
