from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Set

from .models import ForgeRecord, ForgeStage, ReviewVerdict


class ForgeTransitionError(ValueError):
    """Raised when a design attempts an invalid Forge transition."""


@dataclass(frozen=True)
class StageRequirement:
    key: str
    description: str


class ForgeStateMachine:
    """Enforces ordered progress and evidence gates for House of Frazier designs."""

    ORDER = [
        ForgeStage.IDEA,
        ForgeStage.RESEARCH,
        ForgeStage.STORY,
        ForgeStage.FORM,
        ForgeStage.MATERIALS,
        ForgeStage.PATTERN,
        ForgeStage.ENGINEERING,
        ForgeStage.VIABILITY,
        ForgeStage.CRITIQUE,
        ForgeStage.COUNCIL,
        ForgeStage.ARCHIVE,
    ]

    REQUIREMENTS: Dict[ForgeStage, tuple[StageRequirement, ...]] = {
        ForgeStage.RESEARCH: (
            StageRequirement("research_complete", "Research notes must be completed."),
        ),
        ForgeStage.STORY: (
            StageRequirement("story_complete", "The design narrative must be defined."),
        ),
        ForgeStage.FORM: (
            StageRequirement("form_defined", "The silhouette or form must be defined."),
        ),
        ForgeStage.MATERIALS: (
            StageRequirement("materials_selected", "At least one approved material must be selected."),
        ),
        ForgeStage.PATTERN: (
            StageRequirement("surface_language_reviewed", "Pattern or surface treatment must be reviewed."),
        ),
        ForgeStage.ENGINEERING: (
            StageRequirement("engineering_review_passed", "Hermes engineering review must pass."),
        ),
        ForgeStage.VIABILITY: (
            StageRequirement("cost_estimate_complete", "Manufacturing cost estimate must exist."),
            StageRequirement("prototype_plan_complete", "A prototype and test plan must exist."),
        ),
        ForgeStage.CRITIQUE: (
            StageRequirement("genome_scored", "A Design Genome score must exist."),
            StageRequirement("critique_complete", "A critique report must exist."),
        ),
        ForgeStage.COUNCIL: (
            StageRequirement("all_ai_reviews_complete", "Hermes, Minerva, and Ajani reviews are required."),
            StageRequirement("originality_review_passed", "Originality review must pass."),
        ),
        ForgeStage.ARCHIVE: (
            StageRequirement("council_approved", "Council approval is required before archiving as approved."),
        ),
    }

    def allowed_next(self, current: ForgeStage) -> ForgeStage | None:
        index = self.ORDER.index(current)
        if index == len(self.ORDER) - 1:
            return None
        return self.ORDER[index + 1]

    def missing_requirements(
        self,
        target: ForgeStage,
        evidence: Mapping[str, bool],
    ) -> list[StageRequirement]:
        return [
            requirement
            for requirement in self.REQUIREMENTS.get(target, ())
            if not evidence.get(requirement.key, False)
        ]

    def transition(
        self,
        record: ForgeRecord,
        target: ForgeStage,
        evidence: Mapping[str, bool],
        note: str = "",
    ) -> ForgeRecord:
        expected = self.allowed_next(record.stage)
        if expected is None:
            raise ForgeTransitionError("Archived designs cannot advance further.")
        if target != expected:
            raise ForgeTransitionError(
                f"Invalid transition from {record.stage.value} to {target.value}; "
                f"expected {expected.value}."
            )

        missing = self.missing_requirements(target, evidence)
        if missing:
            details = "; ".join(item.description for item in missing)
            raise ForgeTransitionError(f"Cannot enter {target.value}: {details}")

        if target is ForgeStage.ARCHIVE:
            decision = record.council_decision
            if decision is None or decision.verdict is not ReviewVerdict.APPROVE:
                raise ForgeTransitionError("Council must approve the design before archival approval.")

        record.advance(target, note or "Requirements verified")
        return record

    def completion_percentage(self, stage: ForgeStage) -> float:
        index = self.ORDER.index(stage)
        return round((index / (len(self.ORDER) - 1)) * 100.0, 2)
