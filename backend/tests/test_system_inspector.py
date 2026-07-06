from services import system_inspector


def test_system_inspector_report_has_headquarters_structure():
    report = system_inspector.inspect_repository()

    assert report["title"] == "ATLAS System Inspector Report"
    assert "counts" in report
    assert "findings" in report
    assert "health_score" in report
    assert 0 <= report["health_score"] <= 100
    assert report["headquarters_rule"].startswith("No subsystem is complete")


def test_technical_debt_register_is_deterministic_shape():
    register = system_inspector.technical_debt_register()

    assert register["title"] == "ATLAS Technical Debt Register"
    assert isinstance(register["count"], int)
    assert isinstance(register["items"], list)


def test_certification_report_has_seven_seals():
    report = system_inspector.certification_report()

    seals = {item["seal"] for item in report["seals"]}
    assert report["title"] == "ATLAS Headquarters Certification Report"
    assert len(seals) == 7
    assert "Architecture" in seals
    assert "Engineering" in seals
    assert "Testing" in seals
    assert "Documentation" in seals
    assert "Security" in seals
    assert "Performance" in seals
    assert "Luxury Review" in seals
    assert report["overall_status"] in {"approved", "needs_refinement"}
