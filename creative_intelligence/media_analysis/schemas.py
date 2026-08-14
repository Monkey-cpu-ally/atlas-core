from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class VisualObservation:
    subject: str
    silhouette: List[str] = field(default_factory=list)
    shape_language: List[str] = field(default_factory=list)
    proportion: List[str] = field(default_factory=list)
    line: List[str] = field(default_factory=list)
    color: List[str] = field(default_factory=list)
    value: List[str] = field(default_factory=list)
    lighting: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    composition: List[str] = field(default_factory=list)
    perspective: List[str] = field(default_factory=list)
    costume: List[str] = field(default_factory=list)
    movement: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class StoryObservation:
    title: str
    premise: str
    character_goals: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    reveals: List[str] = field(default_factory=list)
    pacing_notes: List[str] = field(default_factory=list)
    visual_storytelling: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    scene_changes: List[str] = field(default_factory=list)


@dataclass
class MediaStudyReport:
    source_name: str
    source_type: str
    visual: VisualObservation | None = None
    story: StoryObservation | None = None
    extracted_principles: List[str] = field(default_factory=list)
    application_notes: List[str] = field(default_factory=list)
    originality_guardrails: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# Media Study: {self.source_name}", "", f"Type: {self.source_type}", ""]
        if self.visual:
            lines.extend(["## Visual Analysis", f"Subject: {self.visual.subject}"])
            for title, items in [
                ("Silhouette", self.visual.silhouette),
                ("Shape Language", self.visual.shape_language),
                ("Proportion", self.visual.proportion),
                ("Line", self.visual.line),
                ("Color", self.visual.color),
                ("Value", self.visual.value),
                ("Lighting", self.visual.lighting),
                ("Materials", self.visual.materials),
                ("Composition", self.visual.composition),
                ("Perspective", self.visual.perspective),
                ("Costume", self.visual.costume),
                ("Movement", self.visual.movement),
            ]:
                if items:
                    lines.append(f"### {title}")
                    lines.extend(f"- {item}" for item in items)
        if self.story:
            lines.extend(["", "## Story Analysis", f"Premise: {self.story.premise}"])
            for title, items in [
                ("Character Goals", self.story.character_goals),
                ("Conflicts", self.story.conflicts),
                ("Reveals", self.story.reveals),
                ("Pacing", self.story.pacing_notes),
                ("Visual Storytelling", self.story.visual_storytelling),
                ("Themes", self.story.themes),
                ("Scene Changes", self.story.scene_changes),
            ]:
                if items:
                    lines.append(f"### {title}")
                    lines.extend(f"- {item}" for item in items)
        lines.extend(["", "## Extracted Principles"])
        lines.extend(f"- {item}" for item in self.extracted_principles)
        lines.extend(["", "## Application Notes"])
        lines.extend(f"- {item}" for item in self.application_notes)
        lines.extend(["", "## Originality Guardrails"])
        lines.extend(f"- {item}" for item in self.originality_guardrails)
        return "\n".join(lines)
