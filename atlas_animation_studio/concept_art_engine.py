from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ConceptArtBrief:
    title: str
    subject: str
    purpose: str
    emotion: str
    silhouette_notes: List[str] = field(default_factory=list)
    material_notes: List[str] = field(default_factory=list)
    color_notes: List[str] = field(default_factory=list)
    lighting_notes: List[str] = field(default_factory=list)
    movement_notes: List[str] = field(default_factory=list)
    revision_questions: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", f"Subject: {self.subject}", f"Purpose: {self.purpose}", f"Emotion: {self.emotion}", ""]
        sections = [
            ("Silhouette", self.silhouette_notes),
            ("Materials", self.material_notes),
            ("Color", self.color_notes),
            ("Lighting", self.lighting_notes),
            ("Movement", self.movement_notes),
            ("Revision Questions", self.revision_questions),
        ]
        for name, items in sections:
            lines.append(f"## {name}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)


class ConceptArtEngine:
    def build_brief(self, title: str, subject: str, purpose: str, emotion: str) -> ConceptArtBrief:
        return ConceptArtBrief(
            title=title,
            subject=subject,
            purpose=purpose,
            emotion=emotion,
            silhouette_notes=[
                "Define a readable outer shape before adding details.",
                "Create at least three variants: practical, elegant, and strange-but-functional.",
                "Remove any shape that feels familiar without purpose.",
            ],
            material_notes=[
                "Choose materials based on function, age, environment, and maintenance.",
                "Describe wear patterns, texture, weight, and reflectivity.",
                "Materials should reveal history, not just decoration.",
            ],
            color_notes=[
                "Pick colors that support emotion and world context.",
                "Balance dominant, secondary, and accent colors.",
                "Avoid random color choices; every color needs a reason.",
            ],
            lighting_notes=[
                "Define the main light source and what it reveals.",
                "Use shadow to guide attention and mood.",
                "Create day, night, and high-tension lighting notes when useful.",
            ],
            movement_notes=[
                "Describe how the design moves or is carried through space.",
                "Movement should express weight, purpose, and personality.",
            ],
            revision_questions=[
                "Is the design recognizable in silhouette?",
                "Does it solve a design problem?",
                "Does it feel emotionally connected to the project?",
                "Does it feel ATLAS-native?",
            ],
        )
