from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class CharacterBible:
    name: str
    role: str
    core_wound: str
    want: str
    need: str
    fear: str
    contradiction: str
    voice: List[str] = field(default_factory=list)
    movement: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    visual_evolution: List[str] = field(default_factory=list)
    symbolism: List[str] = field(default_factory=list)
    arc_beats: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# {self.name}",
            "",
            f"Role: {self.role}",
            f"Core Wound: {self.core_wound}",
            f"Want: {self.want}",
            f"Need: {self.need}",
            f"Fear: {self.fear}",
            f"Contradiction: {self.contradiction}",
            "",
        ]
        sections = [
            ("Voice", self.voice),
            ("Movement", self.movement),
            ("Relationships", self.relationships),
            ("Visual Evolution", self.visual_evolution),
            ("Symbolism", self.symbolism),
            ("Arc Beats", self.arc_beats),
        ]
        for title, items in sections:
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)


class CharacterBibleEngine:
    def build_bible(
        self,
        name: str,
        role: str,
        core_wound: str,
        want: str,
        need: str,
        fear: str,
        contradiction: str,
    ) -> CharacterBible:
        return CharacterBible(
            name=name,
            role=role,
            core_wound=core_wound,
            want=want,
            need=need,
            fear=fear,
            contradiction=contradiction,
            voice=[
                "Define sentence length, vocabulary, rhythm, and what the character refuses to say.",
                "Create one calm voice pattern and one pressure voice pattern.",
            ],
            movement=[
                "Define posture, walk, idle behavior, stress behavior, and recovery behavior.",
                "Movement must change as the character changes.",
            ],
            relationships=[
                "Track trust, dependence, resentment, loyalty, fear, and power for each major relationship.",
                "Each relationship should change at least once across the story.",
            ],
            visual_evolution=[
                "Show growth through clothing, posture, tools, damage, repair, and color changes.",
                "Do not change the design without a story reason.",
            ],
            symbolism=[
                "Give recurring objects, colors, gestures, or locations meaning tied to the character arc.",
            ],
            arc_beats=[
                "Opening state",
                "First pressure test",
                "False solution",
                "Breaking point",
                "Choice",
                "Consequence",
                "New state",
            ],
        )
