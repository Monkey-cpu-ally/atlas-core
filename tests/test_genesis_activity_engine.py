from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVITY_ENGINE = ROOT / "frontend" / "src" / "genesis" / "activity" / "activityEngine.js"
OBSERVATORY = ROOT / "frontend" / "src" / "genesis" / "observatory" / "Observatory.jsx"


def test_activity_engine_is_present_and_exports_builder():
    assert ACTIVITY_ENGINE.exists(), "AI Activity Engine source file is missing"
    source = ACTIVITY_ENGINE.read_text(encoding="utf-8")
    assert "export function buildAiActivities" in source
    assert all(persona in source for persona in ("ajani", "minerva", "hermes"))


def test_observatory_uses_activity_engine_output():
    source = OBSERVATORY.read_text(encoding="utf-8")
    assert "buildAiActivities" in source
    assert "activity.task" in source
    assert "activity.progress" in source
    assert "activity.priority" in source
