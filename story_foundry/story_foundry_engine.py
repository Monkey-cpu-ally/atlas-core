"""ATLAS Story Foundry starter engine.

This module creates original story blueprints using ATLAS role logic.
It is intentionally lightweight so it can be expanded into a full story system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class StorySeed:
    title: str
    genre: str
    core_idea: str
    target_emotion: str
    style_notes: List[str] = field(default_factory=list)


@dataclass
class StoryBlueprint:
    title: str
    premise: str
    ajani_pass: List[str]
    minerva_pass: List[str]
    hermes_pass: List[str]
    council_notes: List[str]

    def to_markdown(self) -> str:
        sections = [
            f"# {self.title}",
            "",
            "## Premise",
            self.premise,
            "",
            "## Ajani Pass",
            *[f"- {item}" for item in self.ajani_pass],
            "",
            "## Minerva Pass",
            *[f"- {item}" for item in self.minerva_pass],
            "",
            "## Hermes Pass",
            *[f"- {item}" for item in self.hermes_pass],
            "",
            "## Council Notes",
            *[f"- {item}" for item in self.council_notes],
        ]
        return "\n".join(sections)


class StoryFoundryEngine:
    """Creates original ATLAS story blueprints from a seed idea."""

    def build_blueprint(self, seed: StorySeed) -> StoryBlueprint:
        premise = (
            f"An original {seed.genre} story built around: {seed.core_idea}. "
            f"The emotional target is {seed.target_emotion}. "
            "The final version must preserve Frazier's vision while rejecting generic execution."
        )
        return StoryBlueprint(
            title=seed.title,
            premise=premise,
            ajani_pass=[
                "Define the protagonist's want, wound, contradiction, and breaking point.",
                "Create conflict that forces hard choices instead of random events.",
                "Build escalation through consequence, not noise.",
            ],
            minerva_pass=[
                "Create lore with origin, ritual, symbol, cost, and contradiction.",
                "Reveal world history through environment, behavior, music, tools, and ruins.",
                "Connect mystery to emotion so the audience cares about the answer.",
            ],
            hermes_pass=[
                "Design silhouettes for characters, locations, creatures, props, and machines.",
                "Use visual storytelling before exposition.",
                "Make every object feel engineered, historical, and emotionally present.",
            ],
            council_notes=[
                "Run originality review before outlining scenes.",
                "Reject any version that feels like a thin copy of a known story.",
                "First unique. Then beautiful. Then functional. Never generic.",
            ],
        )
