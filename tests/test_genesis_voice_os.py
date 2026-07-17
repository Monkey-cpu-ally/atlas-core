from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOICE_ROUTER = ROOT / "frontend" / "src" / "genesis" / "voice" / "voiceCommandRouter.js"
CONVERSATION_INTENT = ROOT / "frontend" / "src" / "genesis" / "voice" / "conversationIntent.js"
VOICE_CLARIFICATION = ROOT / "frontend" / "src" / "genesis" / "voice" / "voiceClarification.js"
VOICE_HOOK = ROOT / "frontend" / "src" / "genesis" / "voice" / "useAtlasVoice.js"
SPEECH_HOOK = ROOT / "frontend" / "src" / "genesis" / "voice" / "useAtlasSpeech.js"
VOICE_RESPONSE = ROOT / "frontend" / "src" / "genesis" / "voice" / "voiceCommandResponse.js"
MINIMAL_HOME = ROOT / "frontend" / "src" / "genesis" / "minimal" / "MinimalHome.jsx"
GENESIS_HUB = ROOT / "frontend" / "src" / "genesis" / "GenesisHub.jsx"


def test_voice_os_sources_exist():
    assert VOICE_ROUTER.exists()
    assert CONVERSATION_INTENT.exists()
    assert VOICE_CLARIFICATION.exists()
    assert VOICE_HOOK.exists()
    assert SPEECH_HOOK.exists()
    assert VOICE_RESPONSE.exists()


def test_voice_router_has_core_commands():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    for command in (
        "wake",
        "repeat",
        "cancel",
        "project",
        "persona",
        "observatory",
        "projects",
        "mission",
        "pulse",
        "awareness",
        "home",
    ):
        assert f'type: "{command}"' in source
    for persona in ("ajani", "minerva", "hermes", "council"):
        assert persona in source


def test_voice_router_matches_real_project_records():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    assert "findVoiceProject" in source
    assert "findVoiceProjectCandidates" in source
    assert "scoreProjectMatch" in source
    assert "projectId: project.id" in source
    assert "projectSearchTerms" in source
    assert "projects = []" in source


def test_voice_router_supports_contextual_navigation():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    assert "resolveCurrentProject" in source
    assert "continue current project" in source
    assert "open it" in source
    assert "what should i do next" in source
    assert "previous screen" in source
    assert "contextual: true" in source


def test_voice_router_remembers_prior_project_and_persona_targets():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    assert "voiceContext" in source
    assert "rememberVoiceContext" in source
    assert "getVoiceContext" in source
    assert "resetVoiceContext" in source
    assert "contextualReferenceCommand" in source
    assert "resolvedFromMemory: true" in source
    assert "continue that" in source
    assert "show me the next step" in source
    assert 'voiceContext.type === "project"' in source
    assert 'voiceContext.type === "persona"' in source


def test_voice_router_supports_wake_repeat_and_cancel():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    assert "WAKE_WORDS" in source
    assert "stripWakeWord" in source
    assert "hey atlas" in source
    assert "repeat that" in source
    assert "never mind" in source


def test_natural_conversation_engine_extracts_intent_topic_and_persona():
    source = CONVERSATION_INTENT.read_text(encoding="utf-8")
    assert "detectConversationIntent" in source
    assert "inferConversationPersona" in source
    assert "extractConversationTopic" in source
    assert "buildConversationCommand" in source
    for intent in ("design", "research", "review", "plan", "explain", "brainstorm"):
        assert f'intent: "{intent}"' in source
    assert 'design: "hermes"' in source
    assert 'research: "minerva"' in source
    assert 'plan: "ajani"' in source
    assert 'review: "council"' in source


def test_voice_router_promotes_normal_speech_to_conversation_commands():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    assert 'import { buildConversationCommand }' in source
    assert "looksConversational" in source
    assert "findExplicitPersona" in source
    assert "buildConversationCommand({" in source
    assert 'command?.type === "conversation"' in source


def test_clarification_engine_tracks_and_resolves_project_choices():
    source = VOICE_CLARIFICATION.read_text(encoding="utf-8")
    assert "pendingClarification" in source
    assert "requestProjectClarification" in source
    assert "resolvePendingClarification" in source
    assert "clearPendingClarification" in source
    assert 'clarificationKind: "project"' in source
    assert "selectedByOrdinal" in source
    assert "selectedByName" in source
    assert "resolvedFromClarification: true" in source


def test_router_requests_clarification_for_close_project_matches():
    source = VOICE_ROUTER.read_text(encoding="utf-8")
    assert "hasAmbiguousProjectMatch" in source
    assert "requestProjectClarification" in source
    assert "resolvePendingClarification" in source
    assert "first.score - second.score <= 5" in source


def test_voice_response_layer_confirms_understood_action():
    source = VOICE_RESPONSE.read_text(encoding="utf-8")
    assert "buildVoiceCommandResponse" in source
    assert "Opening" in source
    assert "Continuing" in source
    assert "There is no previous response to repeat" in source
    assert "Cancelled" in source
    assert "I did not recognize that command" in source


def test_voice_response_is_persona_aware_for_conversation():
    source = VOICE_RESPONSE.read_text(encoding="utf-8")
    assert "PERSONA_OPENERS" in source
    assert "INTENT_RESPONSES" in source
    assert "buildConversationResponse" in source
    assert 'case "conversation"' in source
    assert "Hermes here" in source
    assert "Minerva is ready" in source
    assert "Ajani is with you" in source
    assert "The Council will examine it together" in source


def test_voice_response_speaks_project_clarification_options():
    source = VOICE_RESPONSE.read_text(encoding="utf-8")
    assert "buildClarificationResponse" in source
    assert 'case "clarification"' in source
    assert "Which project did you mean" in source
    assert "Clarification cancelled" in source


def test_speech_controller_uses_browser_synthesis_with_fallback():
    source = SPEECH_HOOK.read_text(encoding="utf-8")
    assert "speechSynthesis" in source
    assert "SpeechSynthesisUtterance" in source
    assert "supported" in source
    assert "cancel" in source


def test_minimal_home_preserves_completed_response_for_followups():
    source = MINIMAL_HOME.read_text(encoding="utf-8")
    assert "useAtlasVoice" in source
    assert "useAtlasSpeech" in source
    assert "buildVoiceCommandResponse" in source
    assert "lastCompletedResponse" in source
    assert 'response.command.type === "cancel"' in source
    assert "voice.start()" in source
    assert "voice.stop()" in source
    assert "speech.speak(response.message)" in source
    assert "onVoiceCommand" in source


def test_minimal_home_executes_each_resolved_command_only_once():
    source = MINIMAL_HOME.read_text(encoding="utf-8")
    assert "NON_NAVIGATING_COMMANDS" in source
    assert '"clarification"' in source
    assert "onVoiceCommand?.(response.command)" in source
    assert "navigationTranscriptFor" not in source


def test_genesis_hub_routes_resolved_voice_commands_to_existing_actions():
    source = GENESIS_HUB.read_text(encoding="utf-8")
    assert "commandOrTranscript" in source
    assert 'typeof commandOrTranscript === "string"' in source
    assert "currentProject: activeProject" in source
    assert 'case "project"' in source
    assert 'case "conversation"' in source
    assert "selectProject(command.project)" in source
    assert "kernel.openProjects()" in source
    assert "kernel.openPulse()" in source
    assert "kernel.openAwareness()" in source
    assert "selectPersona(command.persona)" in source
