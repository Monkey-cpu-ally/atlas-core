from services import headquarters_engine


def test_headquarters_status_exposes_atlas_identity():
    status = headquarters_engine.headquarters_status()

    assert status["name"] == "ATLAS Headquarters"
    assert status["standard"] == "ATLAS Luxury Engineering Standard"
    assert status["release_posture"] == "not_ready_until_verified"
    assert len(status["seals"]) == 7
    assert any(division["owner"] == "Minerva" for division in status["divisions"])
    assert any(division["owner"] == "Hermes" for division in status["divisions"])
    assert status["technical_debt"]["active_count"] >= 1


def test_quality_gate_report_requires_all_completion_gates():
    report = headquarters_engine.quality_gate_report()
    gate_names = {gate["gate"] for gate in report["gates"]}

    assert report["approval_status"] == "pending"
    assert {
        "Built",
        "Connected",
        "Tested",
        "Cleaned",
        "Documented",
        "Approved",
    }.issubset(gate_names)
    assert all(gate["required"] for gate in report["gates"])


def test_atlas_standard_maps_generic_routes_to_headquarters_language():
    standard = headquarters_engine.atlas_standard()
    replacement_map = standard["generic_replacement_map"]

    assert "Truth over assumptions." in standard["principles"]
    assert replacement_map["/api/discovery-approval"] == "/api/headquarters/knowledge-gate"
    assert replacement_map["/api/external-access"] == "/api/headquarters/source-clearance"
    assert replacement_map["/api/project-intelligence"] == "/api/headquarters/project-briefing"


def test_mission_control_blocks_new_phase_until_verification():
    mission = headquarters_engine.mission_control()

    assert mission["active"]["operation"] == "Operation ATLAS Refinement"
    assert mission["blocked_until"] == "Phase 14 verification passes."
    assert any("route-level tests" in item for item in mission["queue"])


def test_technical_debt_register_prioritizes_visible_debt():
    report = headquarters_engine.technical_debt_register()
    debt_ids = {item["debt_id"] for item in report["items"]}

    assert report["title"] == "ATLAS Technical Debt Register"
    assert report["active_count"] >= 1
    assert report["highest_open_severity"] in {"high", "critical"}
    assert "DEBT-PERSIST-001" in debt_ids
    assert report["by_quality_gate"]["Engineering"] >= 1


def test_technical_debt_register_can_filter_by_status_and_severity():
    open_report = headquarters_engine.technical_debt_register(status="open")
    high_report = headquarters_engine.technical_debt_register(severity="high")

    assert open_report["items"]
    assert all(item["status"] == "open" for item in open_report["items"])
    assert high_report["items"]
    assert all(item["severity"] == "high" for item in high_report["items"])


def test_refinement_surface_includes_technical_debt_summary():
    surface = headquarters_engine.refinement()

    assert surface["title"] == "ATLAS Refinement Office"
    assert surface["technical_debt"]["title"] == "ATLAS Technical Debt Register"
    assert surface["technical_debt"]["active_count"] >= 1
