from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class EnvironmentDesignPlan:
    name: str
    function: str
    history: str
    architecture: List[str] = field(default_factory=list)
    ecology: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    lighting: List[str] = field(default_factory=list)
    story_details: List[str] = field(default_factory=list)
    revision_checks: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.name}", "", f"Function: {self.function}", f"History: {self.history}", ""]
        sections = [
            ("Architecture", self.architecture),
            ("Ecology", self.ecology),
            ("Materials", self.materials),
            ("Lighting", self.lighting),
            ("Story Details", self.story_details),
            ("Revision Checks", self.revision_checks),
        ]
        for title, items in sections:
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)


class EnvironmentDesignEngine:
    def build_plan(self, name: str, function: str, history: str) -> EnvironmentDesignPlan:
        return EnvironmentDesignPlan(
            name=name,
            function=function,
            history=history,
            architecture=[
                "Let structure reveal power, culture, climate, and technology.",
                "Design circulation, scale, entrances, exits, and sight lines.",
                "Use damage, repairs, and additions to show time.",
            ],
            ecology=[
                "Define weather, plants, water, animals, and seasonal change.",
                "Nature should influence movement, maintenance, and survival.",
            ],
            materials=[
                "Choose local and imported materials with reasons.",
                "Define aging, corrosion, staining, breakage, and repair patterns.",
            ],
            lighting=[
                "Define natural and artificial light sources.",
                "Use light to reveal paths, danger, history, and emotion.",
            ],
            story_details=[
                "Place objects and wear patterns that imply past events.",
                "Use signs, rituals, tools, sound, and absence as story clues.",
            ],
            revision_checks=[
                "Could people or creatures actually live here?",
                "Does the environment reveal history without exposition?",
                "Is the visual identity distinct from generic fantasy or science fiction?",
                "Does the location feel ATLAS-native?",
            ],
        )
