from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MINIMAL_HOME = ROOT / "frontend" / "src" / "genesis" / "minimal" / "MinimalHome.jsx"
GENESIS_HUB = ROOT / "frontend" / "src" / "genesis" / "GenesisHub.jsx"


def test_minimal_home_exists_and_is_voice_first():
    assert MINIMAL_HOME.exists(), "Minimal home component is missing"
    source = MINIMAL_HOME.read_text(encoding="utf-8")
    assert "Hold to speak" in source
    assert "Current Mission" in source
    assert "Current Project" in source
    assert "buildAiActivities" in source


def test_genesis_hub_uses_minimal_home_and_hides_utilities():
    source = GENESIS_HUB.read_text(encoding="utf-8")
    assert 'import MinimalHome from "./minimal/MinimalHome"' in source
    assert "showMinimalHome" in source
    assert "!showMinimalHome" in source
    assert "developerMode ? <div className=\"genesis-hub__connection\"" in source
