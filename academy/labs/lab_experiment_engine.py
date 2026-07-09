from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LabExperiment:
    title: str
    lab_name: str
    question: str
    starting_idea: str
    constraints: List[str] = field(default_factory=list)
    versions: List[str] = field(default_factory=list)
    critique: List[str] = field(default_factory=list)
    final_direction: str = ""
    lessons_saved: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", f"Lab: {self.lab_name}", f"Question: {self.question}", f"Starting Idea: {self.starting_idea}", ""]
        for title, items in [
            ("Constraints", self.constraints),
            ("Versions", self.versions),
            ("Critique", self.critique),
            ("Lessons Saved", self.lessons_saved),
        ]:
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        lines.append("## Final Direction")
        lines.append(self.final_direction)
        return "\n".join(lines)


class LabExperimentEngine:
    def create_experiment(self, title: str, lab_name: str, question: str, starting_idea: str) -> LabExperiment:
        return LabExperiment(
            title=title,
            lab_name=lab_name,
            question=question,
            starting_idea=starting_idea,
            constraints=[
                "Create at least two different versions.",
                "The first version cannot be final.",
                "The final version must be more specific than the starting idea.",
            ],
            versions=[
                "Version A: direct practical solution.",
                "Version B: more emotional and visually distinct solution.",
                "Version C: ATLAS-native synthesis that improves function, identity, and story.",
            ],
            critique=[
                "Identify what feels too familiar.",
                "Identify what lacks emotional purpose.",
                "Identify what needs stronger visual or structural identity.",
            ],
            final_direction="Revise toward the version with the strongest identity, function, and emotional purpose.",
            lessons_saved=[
                "Good ideas improve through comparison.",
                "Specificity beats generic cool factor.",
                "Council critique is part of the creative process.",
            ],
        )
