"""Visual Development planning that consumes learned Creative Intelligence."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol


class CreativeBriefProvider(Protocol):
    def build_brief(self, *, project: str, task: str): ...


@dataclass
class VisualDevelopmentPlan:
    project: str
    subject: str
    purpose: str
    silhouette_rules: List[str] = field(default_factory=list)
    shape_language: List[str] = field(default_factory=list)
    color_rules: List[str] = field(default_factory=list)
    lighting_rules: List[str] = field(default_factory=list)
    material_rules: List[str] = field(default_factory=list)
    composition_rules: List[str] = field(default_factory=list)
    motion_rules: List[str] = field(default_factory=list)
    creative_context: str = ""

    def to_markdown(self) -> str:
        lines = [
            f"# Visual Development — {self.project}",
            f"Subject: {self.subject}",
            f"Purpose: {self.purpose}",
        ]
        sections = [
            ("Silhouette", self.silhouette_rules),
            ("Shape Language", self.shape_language),
            ("Color", self.color_rules),
            ("Lighting", self.lighting_rules),
            ("Materials", self.material_rules),
            ("Composition", self.composition_rules),
            ("Motion", self.motion_rules),
        ]
        for title, items in sections:
            lines.extend(["", f"## {title}"])
            lines.extend(f"- {item}" for item in items)
        if self.creative_context:
            lines.extend(["", "## Creative Intelligence Context", self.creative_context])
        return "\n".join(lines)


class VisualDevelopmentEngine:
    def __init__(self, creative_bridge: CreativeBriefProvider | None = None) -> None:
        self.creative_bridge = creative_bridge

    def build_plan(self, *, project: str, subject: str, purpose: str) -> VisualDevelopmentPlan:
        creative_context = ""
        if self.creative_bridge is not None:
            brief = self.creative_bridge.build_brief(
                project=project,
                task=f"visual development for {subject}; purpose: {purpose}",
            )
            creative_context = brief.to_prompt_context()

        return VisualDevelopmentPlan(
            project=project,
            subject=subject,
            purpose=purpose,
            silhouette_rules=[
                "Make the primary read clear before internal detail.",
                "Use negative space to separate signature forms and tools.",
            ],
            shape_language=[
                "Choose a dominant geometric family that supports function and emotion.",
                "Use secondary shapes to create contrast without destroying identity.",
            ],
            color_rules=[
                "Assign color by story function, hierarchy, environment, and culture.",
                "Reserve strongest contrast for the intended focal point.",
            ],
            lighting_rules=[
                "Use light direction to reveal form, threat, mood, and material response.",
                "Preserve readable values before decorative effects.",
            ],
            material_rules=[
                "Materials must reflect manufacturing logic, wear, age, and use.",
                "Surface detail should reinforce function rather than replace structure.",
            ],
            composition_rules=[
                "Establish one dominant focal hierarchy.",
                "Use framing and depth to support story information.",
            ],
            motion_rules=[
                "Design pose and movement around weight, intention, and personality.",
                "A still silhouette should imply how the subject moves.",
            ],
            creative_context=creative_context,
        )
