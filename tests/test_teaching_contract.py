from pathlib import Path

import pytest

from atlas_core.teaching_engine import LEARNING_LEVELS
from atlas_core.teaching_engine.contract import (
    DELIVERY_LAW,
    PERSONA_TEACHING_STYLES,
    normalize_learning_level,
    teaching_contract,
)


ROOT = Path(__file__).resolve().parents[1]


def test_contract_uses_the_bookshelfs_exact_seven_levels():
    assert LEARNING_LEVELS == (
        "foundation",
        "beginner",
        "intermediate",
        "advanced",
        "undergraduate",
        "graduate",
        "research",
    )


def test_depth_and_clarity_are_independent_requirements():
    prompt = teaching_contract("research", "hermes")

    assert "SELECTED KNOWLEDGE LEVEL: RESEARCH" in prompt
    assert "PhD/frontier depth" in prompt
    assert "sixth-to-seventh-grade sentence clarity" in prompt
    assert "ADHD-friendly delivery is always on" in prompt
    assert "do not fall back to a beginner lesson" in prompt
    assert "equations" in prompt


@pytest.mark.parametrize("persona", ["ajani", "minerva", "hermes", "council"])
def test_every_persona_has_an_explicit_teaching_style(persona):
    prompt = teaching_contract("graduate", persona)
    assert PERSONA_TEACHING_STYLES[persona] in prompt


def test_unknown_level_fails_closed_instead_of_guessing():
    with pytest.raises(ValueError, match="unknown learning level"):
        normalize_learning_level("expert-ish")


@pytest.mark.asyncio
async def test_teaching_engine_injects_level_delivery_and_persona(monkeypatch):
    from atlas_core.teaching_engine import teaching

    captured = {}

    class Teacher:
        async def think(self, prompt, context=None):
            captured["prompt"] = prompt
            captured["context"] = context
            return "lesson"

    monkeypatch.setattr(teaching, "get_core", lambda _key: Teacher())

    result = await teaching.teach(
        "quantum entanglement",
        core="hermes",
        learning_level="research",
        context="selected bookshelf source",
    )

    assert result["learning_level"] == "research"
    assert result["teacher"] == "hermes"
    assert "SELECTED KNOWLEDGE LEVEL: RESEARCH" in captured["prompt"]
    assert "ADHD-friendly delivery is always on" in captured["prompt"]
    assert PERSONA_TEACHING_STYLES["hermes"] in captured["prompt"]
    assert captured["context"] == "selected bookshelf source"


def test_hud_sends_selected_level_to_teaching_api():
    source = (
        ROOT / "frontend" / "src" / "components" / "HUD" / "TeachingWorkbench.js"
    ).read_text(encoding="utf-8")

    for level in LEARNING_LEVELS:
        assert f"'{level}'" in source
    assert "learning_level: learningLevel" in source
    assert 'data-testid="teach-learning-level"' in source


def test_bookshelf_carries_level_into_teach_and_persona_actions():
    source = (
        ROOT / "frontend" / "src" / "components" / "HUD" / "KnowledgeBookshelf.js"
    ).read_text(encoding="utf-8")

    assert "detail: { resource: selected, learningLevel }" in source
    assert "Selected knowledge depth: ${learningLevel}" in source


def test_personality_bible_contains_the_governing_principle():
    bible = (ROOT / "UX_DIVISION" / "05_AI_PERSONALITY_INTERACTION_BIBLE.md").read_text(
        encoding="utf-8"
    )
    assert "never lower the intelligence of the lesson" in bible.lower()
    assert "ADHD-friendly structure always active" in bible
    assert "Research" in bible


def test_delivery_law_rejects_dumbing_down():
    assert "Clear language is not permission to remove" in DELIVERY_LAW
