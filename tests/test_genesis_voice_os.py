from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOICE_ROUTER = ROOT / "frontend" / "src" / "genesis" / "voice" / "voiceCommandRouter.js"
VOICE_HOOK = ROOT / "frontend" / "src" / "genesis" / "voice" / "useAtlasVoice.js"
MINIMAL_HOME = ROOT / "frontend" / "src" / "genesis" / "minimal" / "MinimalHome.jsx"
GENESIS_HUB = ROOT / "frontend" / "src" / "genesis" / "GenesisHub.jsx"


def test_voice_os_sources_exist():
    assert VOICE_ROUTER.exists()
    assert VOICE_HOOK.exists()


def test_voice_router_has_core_commands():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    for command in ("persona", "observatory", "projects", "mission", "pulse", "awareness", "home"):
        assert f'type: "{command}"' in source
    for persona in ("ajani", "minerva", "hermes", "council"):
        assert persona in source


def test_minimal_home_uses_real_voice_controller():
    source = MINIMAL_HOME.read_text(encoding="utf-8")
    assert "useAtlasVoice" in source
    assert "voice.start()" in source
    assert "voice.stop()" in source
    assert "onVoiceCommand" in source


def test_genesis_hub_routes_voice_to_existing_actions():
    source = GENESIS_HUB.read_text(encoding="utf-8")
    assert "routeVoiceCommand" in source
    assert "handleVoiceCommand" in source
    assert "kernel.openProjects()" in source
    assert "kernel.openPulse()" in source
    assert "kernel.openAwareness()" in source
    assert "selectPersona(command.persona)" in source
