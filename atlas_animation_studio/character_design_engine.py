from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class CharacterDesignPlan:
    name: str
    role: str
    emotional_core: str
    silhouette: List[str] = field(default_factory=list)
    costume: List[str] = field(default_factory=list)
    posture: List[str] = field(default_factory=list)
    facial_language: List[str] = field(default_factory=list)
    props: List[str] = field(default_factory=list)
    revision_checks: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.name}", "", f"Role: {self.role}", f"Emotional Core: {self.emotional_core}", ""]
        sections = [
            ("Silhouette", self.silhouette),
            ("Costume", self.costume),
            ("Posture", self.posture),
            ("Facial Language", self.facial_language),
            ("Props", self.props),
            ("Revision Checks", self.revision_checks),
        ]
        for title, items in sections:
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)


class CharacterDesignEngine:
    def build_plan(self, name: str, role: str, emotional_core: str) -> CharacterDesignPlan:
        return CharacterDesignPlan(
            name=name,
            role=role,
            emotional_core=emotional_core,
            silhouette=[
                "Create a shape that reflects role and personality.",
                "Test readability at small size.",
                "Avoid details that do not support identity.",
            ],
            costume=[
                "Choose clothing based on culture, work, climate, and history.",
                "Use wear, repairs, and fit to reveal daily life.",
                "Keep one signature element that can become iconic.",
            ],
            posture=[
                "Define default stance and center of gravity.",
                "Show confidence, fear, injury, or secrecy through body language.",
            ],
            facial_language=[
                "Define resting expression and stress expression.",
                "Use eye direction and mouth tension intentionally.",
            ],
            props=[
                "Give the character tools or objects with story purpose.",
                "Every prop should reveal habit, status, memory, or function.",
            ],
            revision_checks=[
                "Would this character be recognizable without color?",
                "Does the design reveal personality before dialogue?",
                "Does every major detail have a reason?",
                "Does the character feel ATLAS-native?",
            ],
        )
