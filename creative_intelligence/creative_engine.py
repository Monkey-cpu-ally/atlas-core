"""Main orchestration engine for ATLAS Creative Intelligence."""

from __future__ import annotations

from typing import Iterable, List

from .creative_council import CreativeCouncil
from .masters_library import get_creator
from .originality_engine import scan_similarity_risks
from .schemas import CraftLesson, CreativeBrief, CreativePlan
from .style_synthesis import synthesize_atlas_direction


class CreativeIntelligenceEngine:
    """Builds ATLAS-native creative plans from briefs and craft-study profiles."""

    def __init__(self) -> None:
        self.council = CreativeCouncil()

    def study_creator(self, creator_name: str) -> CraftLesson:
        creator = get_creator(creator_name)
        return CraftLesson(
            creator_name=creator.name,
            extracted_principles=list(creator.craft_focus),
            possible_atlas_applications=[creator.atlas_use],
            avoid_copying=[
                creator.caution,
                "Transform the principle through ATLAS style pillars before using it.",
                "Combine multiple influences so no single creator dominates the output.",
            ],
        )

    def build_plan(self, brief: CreativeBrief, creator_names: Iterable[str]) -> CreativePlan:
        lessons: List[CraftLesson] = [self.study_creator(name) for name in creator_names]
        atlas_direction = synthesize_atlas_direction(brief, lessons)
        council_notes = self.council.review(brief)
        originality_warnings = scan_similarity_risks(brief)
        next_steps = [
            "Write the ATLAS identity sentence.",
            "Create a one-page outline with beginning, escalation, reversal, and consequence.",
            "Create a visual design sheet: silhouettes, materials, symbols, locations, and color logic.",
            "Run originality review again after the outline and before final drafting.",
            "Generate scenes using ATLAS scene rules, then revise for clarity and emotional force.",
        ]
        return CreativePlan(
            title=brief.title,
            atlas_direction=atlas_direction,
            craft_lessons=lessons,
            council_notes=council_notes,
            originality_warnings=originality_warnings,
            next_steps=next_steps,
        )
