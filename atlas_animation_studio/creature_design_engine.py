from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class CreatureDesignPlan:
    name: str
    habitat: str
    ecological_role: str
    anatomy: List[str] = field(default_factory=list)
    locomotion: List[str] = field(default_factory=list)
    behavior: List[str] = field(default_factory=list)
    surface_materials: List[str] = field(default_factory=list)
    visual_identity: List[str] = field(default_factory=list)
    revision_checks: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.name}", "", f"Habitat: {self.habitat}", f"Ecological Role: {self.ecological_role}", ""]
        sections = [
            ("Anatomy", self.anatomy),
            ("Locomotion", self.locomotion),
            ("Behavior", self.behavior),
            ("Surface Materials", self.surface_materials),
            ("Visual Identity", self.visual_identity),
            ("Revision Checks", self.revision_checks),
        ]
        for title, items in sections:
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)


class CreatureDesignEngine:
    def build_plan(self, name: str, habitat: str, ecological_role: str) -> CreatureDesignPlan:
        return CreatureDesignPlan(
            name=name,
            habitat=habitat,
            ecological_role=ecological_role,
            anatomy=[
                "Build anatomy from survival needs, not random decoration.",
                "Define skeleton, muscle logic, feeding method, and sensory systems.",
                "Use asymmetry only when it has biological or story purpose.",
            ],
            locomotion=[
                "Describe walking, running, climbing, flying, swimming, or burrowing mechanics.",
                "Show weight, balance, acceleration, and recovery.",
            ],
            behavior=[
                "Define hunting, defense, mating, nesting, migration, and social behavior.",
                "Behavior should affect how scenes are staged.",
            ],
            surface_materials=[
                "Choose skin, fur, feather, shell, membrane, or synthetic surfaces based on habitat.",
                "Define moisture, wear, scars, temperature response, and reflectivity.",
            ],
            visual_identity=[
                "Create a recognizable silhouette tied to ecological function.",
                "Use color and pattern for camouflage, warning, courtship, or communication.",
            ],
            revision_checks=[
                "Could this creature survive in its environment?",
                "Does its movement match its anatomy?",
                "Does it avoid familiar monster shortcuts?",
                "Is its design memorable and ATLAS-native?",
            ],
        )
