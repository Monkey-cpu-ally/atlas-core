"""Shared schemas for the ATLAS Creative Intelligence Division.

These dataclasses keep the creative subsystem simple, testable, and easy to expand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Domain(str, Enum):
    HORROR = "horror"
    ANIMATION = "animation"
    CINEMA = "cinema"
    GAME_DESIGN = "game_design"
    FANTASY = "fantasy"
    STORY = "story"
    WORLD_BUILDING = "world_building"


class AIRole(str, Enum):
    AJANI = "Ajani"
    MINERVA = "Minerva"
    HERMES = "Hermes"
    COUNCIL = "Council"


@dataclass(frozen=True)
class CreatorProfile:
    name: str
    domains: List[Domain]
    priority: int
    craft_focus: List[str]
    atlas_use: str
    caution: str = "Study craft principles only. Do not copy scenes, dialogue, characters, worlds, or protected expression."


@dataclass
class CreativeBrief:
    title: str
    premise: str
    target_emotion: str
    genre: str
    user_style_notes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class CraftLesson:
    creator_name: str
    extracted_principles: List[str]
    possible_atlas_applications: List[str]
    avoid_copying: List[str]


@dataclass
class CouncilNote:
    role: AIRole
    strengths: List[str]
    risks: List[str]
    recommendations: List[str]


@dataclass
class CreativePlan:
    title: str
    atlas_direction: str
    craft_lessons: List[CraftLesson]
    council_notes: List[CouncilNote]
    originality_warnings: List[str]
    next_steps: List[str]

    def to_markdown(self) -> str:
        lines: List[str] = [f"# {self.title}", "", "## ATLAS Direction", self.atlas_direction, ""]
        lines.append("## Craft Lessons")
        for lesson in self.craft_lessons:
            lines.append(f"### {lesson.creator_name}")
            lines.append("Principles:")
            lines.extend(f"- {item}" for item in lesson.extracted_principles)
            lines.append("ATLAS Applications:")
            lines.extend(f"- {item}" for item in lesson.possible_atlas_applications)
            lines.append("Avoid Copying:")
            lines.extend(f"- {item}" for item in lesson.avoid_copying)
            lines.append("")

        lines.append("## Council Review")
        for note in self.council_notes:
            lines.append(f"### {note.role.value}")
            lines.append("Strengths:")
            lines.extend(f"- {item}" for item in note.strengths)
            lines.append("Risks:")
            lines.extend(f"- {item}" for item in note.risks)
            lines.append("Recommendations:")
            lines.extend(f"- {item}" for item in note.recommendations)
            lines.append("")

        lines.append("## Originality Warnings")
        lines.extend(f"- {item}" for item in self.originality_warnings)
        lines.append("")
        lines.append("## Next Steps")
        lines.extend(f"- {item}" for item in self.next_steps)
        return "\n".join(lines)
