from __future__ import annotations

from dataclasses import dataclass

from .schemas import MediaStudyReport, StoryObservation, VisualObservation
from .story_analyzer import StoryStructureAnalyzer
from .visual_analyzer import VisualCraftAnalyzer


@dataclass
class ReferenceMediaAnalyzer:
    visual_analyzer: VisualCraftAnalyzer = VisualCraftAnalyzer()
    story_analyzer: StoryStructureAnalyzer = StoryStructureAnalyzer()

    def build_report(
        self,
        *,
        source_name: str,
        source_type: str,
        visual: VisualObservation | None = None,
        story: StoryObservation | None = None,
    ) -> MediaStudyReport:
        principles: list[str] = []
        if visual:
            principles.extend(self.visual_analyzer.principle_candidates(visual))
        if story:
            principles.extend(self.story_analyzer.principle_candidates(story))

        return MediaStudyReport(
            source_name=source_name,
            source_type=source_type,
            visual=visual,
            story=story,
            extracted_principles=self._dedupe(principles),
            application_notes=[
                "Translate observed craft into project-specific constraints.",
                "Compare this source with multiple unrelated references before synthesis.",
                "Record what works and fails in Creative Memory after application.",
            ],
            originality_guardrails=[
                "Do not treat one creator or work as a complete style recipe.",
                "Avoid reproducing distinctive protected expression from a single source.",
                "Prefer high-level craft properties, production methods, and design principles.",
                "Require project-specific function, lore, audience, and cultural context.",
            ],
        )

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for value in values:
            key = value.casefold()
            if key not in seen:
                seen.add(key)
                output.append(value)
        return output
