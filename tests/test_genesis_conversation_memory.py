from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONVERSATION_MEMORY = ROOT / "frontend" / "src" / "genesis" / "voice" / "conversationMemory.js"
VOICE_ROUTER = ROOT / "frontend" / "src" / "genesis" / "voice" / "voiceCommandRouter.js"


def test_conversation_memory_source_exists():
    assert CONVERSATION_MEMORY.exists()


def test_conversation_memory_tracks_active_turn_context():
    source = CONVERSATION_MEMORY.read_text(encoding="utf-8")
    assert "conversationMemory" in source
    assert "getConversationMemory" in source
    assert "resetConversationMemory" in source
    assert "rememberConversationTurn" in source
    assert "projectId" in source
    assert "persona" in source
    assert "intent" in source
    assert "topic" in source
    assert "turnCount" in source


def test_conversation_memory_recognizes_short_followups():
    source = CONVERSATION_MEMORY.read_text(encoding="utf-8")
    assert "looksLikeConversationFollowUp" in source
    assert "referencesPriorSubject" in source
    assert "compactFollowUp" in source
    for phrase in ("lighter", "smaller", "research", "review", "explain"):
        assert phrase in source


def test_voice_router_uses_multi_turn_memory_for_followups():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    assert 'from "./conversationMemory"' in source
    assert "conversationFollowUpDefaults" in source
    assert "looksLikeConversationFollowUp" in source
    assert "rememberConversationTurn" in source
    assert "resetConversationMemory" in source
    assert "resolvedFromConversationMemory" in source
    assert "explicitProject || followUp.project" in source
    assert "explicitPersona || followUp.persona" in source


def test_reset_voice_context_also_resets_conversation_memory():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    reset_block = source.split("export function resetVoiceContext()", 1)[1].split("}", 1)[0]
    assert "resetConversationMemory()" in reset_block
