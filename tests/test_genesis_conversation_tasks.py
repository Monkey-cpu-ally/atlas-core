from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "frontend" / "src" / "genesis" / "voice" / "conversationTask.js"
ROUTER = ROOT / "frontend" / "src" / "genesis" / "voice" / "voiceCommandRouter.js"


def test_conversation_task_source_exists():
    assert TASKS.exists()


def test_conversation_task_contains_structured_handoff_fields():
    source = TASKS.read_text(encoding="utf-8")
    for field in (
        "projectId",
        "projectTitle",
        "owner",
        "intent",
        "objective",
        "topic",
        "status",
        "approvalRequired",
        "createdAt",
    ):
        assert field in source


def test_design_review_and_plan_tasks_require_approval():
    source = TASKS.read_text(encoding="utf-8")
    assert 'new Set(["design", "review", "plan"])' in source
    assert '"proposed"' in source
    assert '"ready"' in source
    assert 'approvalRequired: status === "proposed"' in source


def test_task_preserves_conversation_resolution_context():
    source = TASKS.read_text(encoding="utf-8")
    assert "resolvedFromConversationMemory" in source
    assert "resolvedFromClarification" in source
    assert "conversational: true" in source


def test_router_attaches_task_before_memory_and_dispatch():
    source = ROUTER.read_text(encoding="utf-8")
    assert 'import { attachConversationTask } from "./conversationTask"' in source
    assert "const enrichedCommand = attachConversationTask(command)" in source
    assert "rememberVoiceContext(enrichedCommand)" in source
    assert "return enrichedCommand" in source
