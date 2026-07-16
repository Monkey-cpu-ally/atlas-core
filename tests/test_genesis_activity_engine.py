from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVITY_ENGINE = ROOT / "frontend" / "src" / "genesis" / "activity" / "aiActivityEngine.js"
OPERATIONS_ENGINE = ROOT / "frontend" / "src" / "genesis" / "activity" / "operationsTimeline.js"
OBSERVATORY = ROOT / "frontend" / "src" / "genesis" / "observatory" / "Observatory.jsx"


def test_activity_engine_is_present_and_exports_builder():
    assert ACTIVITY_ENGINE.exists(), "AI Activity Engine source file is missing"
    source = ACTIVITY_ENGINE.read_text(encoding="utf-8")
    assert "export function buildAiActivities" in source
    assert all(persona in source for persona in ("ajani", "minerva", "hermes"))
    assert "priority" in source


def test_operations_timeline_is_present_and_uses_verified_sources():
    assert OPERATIONS_ENGINE.exists(), "Operations Timeline source file is missing"
    source = OPERATIONS_ENGINE.read_text(encoding="utf-8")
    assert "export function buildOperationsTimeline" in source
    assert all(source_name in source for source_name in ("pulseItems", "awarenessItems", "projects", "mission"))


def test_observatory_uses_activity_and_operations_output():
    source = OBSERVATORY.read_text(encoding="utf-8")
    assert "buildAiActivities" in source
    assert "activity.task" in source
    assert "activity.progress" in source
    assert "buildOperationsTimeline" in source
    assert "operations.map" in source
