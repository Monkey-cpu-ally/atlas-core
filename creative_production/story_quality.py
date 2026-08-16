"""Story Quality Director for ATLAS Creative Studio."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class StoryQualityIssue:
    category: str
    severity: str
    message: str


@dataclass(frozen=True)
class StoryQualityReport:
    scores: Dict[str, int]
    issues: List[StoryQualityIssue]

    @property
    def passes(self) -> bool:
        hard = {"originality", "character_motivation", "internal_logic", "emotional_authenticity"}
        return (
            not any(issue.severity == "blocker" for issue in self.issues)
            and all(self.scores.get(key, 0) >= 80 for key in hard)
            and sum(self.scores.values()) / max(1, len(self.scores)) >= 85
        )


class StoryQualityDirector:
    """Scores story craft and blocks cheap/recycled/rushed writing patterns."""

    DIMENSIONS = (
        "originality", "character_depth", "dialogue", "emotional_authenticity",
        "theme", "structure", "pacing", "worldbuilding", "conflict",
        "setup_payoff", "tone", "humor_restraint", "audience_maturity",
        "ending_quality", "internal_logic", "character_motivation",
    )

    def evaluate(self, *, scores: Dict[str, int], flags: Iterable[str] = ()) -> StoryQualityReport:
        normalized = {dimension: max(0, min(100, int(scores.get(dimension, 0)))) for dimension in self.DIMENSIONS}
        issues: List[StoryQualityIssue] = []
        blockers = {
            "recycled_plot": "Story feels derivative or recycled.",
            "unmotivated_character": "A character acts without credible motivation.",
            "logic_break": "Internal story logic is broken.",
            "fake_emotion": "Emotional beat is unearned or manipulative.",
        }
        warnings = {
            "forced_humor": "Humor feels forced or over-written.",
            "generic_dialogue": "Dialogue lacks character-specific voice.",
            "rushed_pacing": "Story progression feels rushed.",
            "kiddy_tone": "Tone is more childish than the intended audience requires.",
            "exposition_dump": "Exposition is carrying information that should be dramatized.",
            "predictable_twist": "Major turn is too easy to anticipate.",
        }
        for flag in flags:
            if flag in blockers:
                issues.append(StoryQualityIssue(flag, "blocker", blockers[flag]))
            elif flag in warnings:
                issues.append(StoryQualityIssue(flag, "warning", warnings[flag]))
        for key in ("originality", "character_motivation", "internal_logic", "emotional_authenticity"):
            if normalized[key] < 80:
                issues.append(StoryQualityIssue(key, "blocker", f"{key} score is below the production floor."))
        return StoryQualityReport(normalized, issues)
