from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ColorLightingPlan:
    title: str
    scene_or_design: str
    target_emotion: str
    palette_logic: List[str] = field(default_factory=list)
    lighting_logic: List[str] = field(default_factory=list)
    shadow_logic: List[str] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", f"Scene or Design: {self.scene_or_design}", f"Target Emotion: {self.target_emotion}", ""]
        for title, items in [
            ("Palette Logic", self.palette_logic),
            ("Lighting Logic", self.lighting_logic),
            ("Shadow Logic", self.shadow_logic),
            ("Checks", self.checks),
        ]:
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)


class ColorLightingEngine:
    def build_plan(self, title: str, scene_or_design: str, target_emotion: str) -> ColorLightingPlan:
        return ColorLightingPlan(
            title=title,
            scene_or_design=scene_or_design,
            target_emotion=target_emotion,
            palette_logic=[
                "Choose a dominant color family tied to the main emotion.",
                "Choose a secondary color family tied to contrast or conflict.",
                "Choose one accent color for story focus or danger.",
                "Track saturation changes as emotion rises or falls.",
            ],
            lighting_logic=[
                "Define the key light source and why it exists in the world.",
                "Use fill light only when it supports readability or mood.",
                "Use rim light to separate important shapes from the background.",
                "Let lighting guide the viewer before dialogue explains anything.",
            ],
            shadow_logic=[
                "Use shadow to hide information, reveal danger, or frame emotion.",
                "Control value contrast so the focal point is clear.",
                "Avoid muddy lighting unless confusion is the intentional emotion.",
            ],
            checks=[
                "Can the image read in grayscale?",
                "Does the palette match the story moment?",
                "Does the lighting feel motivated by the environment?",
                "Is the viewer's eye guided to the right place?",
            ],
        )
