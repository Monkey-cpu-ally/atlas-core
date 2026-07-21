from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable, List, Mapping

from .models import CritiqueFinding, DesignConcept, DesignGenome


class OriginalityEngine:
    """Flags likely derivative language using transparent text similarity checks.

    This is an early warning system, not a legal trademark or design-patent opinion.
    """

    def __init__(self, protected_references: Mapping[str, Iterable[str]] | None = None) -> None:
        self.protected_references = {
            name: [phrase.lower().strip() for phrase in phrases]
            for name, phrases in (protected_references or {}).items()
        }

    def inspect(self, concept: DesignConcept, threshold: float = 0.72) -> List[CritiqueFinding]:
        text_fragments = [
            concept.name,
            concept.description,
            concept.story,
            *concept.patterns,
            *concept.hardware,
            *concept.inspirations,
        ]
        design_text = " ".join(text_fragments).lower()
        findings: List[CritiqueFinding] = []

        for reference_name, phrases in self.protected_references.items():
            for phrase in phrases:
                ratio = SequenceMatcher(None, design_text, phrase).ratio()
                direct_match = phrase in design_text
                if direct_match or ratio >= threshold:
                    findings.append(
                        CritiqueFinding(
                            category="originality",
                            severity="high",
                            observation=(
                                f"The concept may resemble the protected identity or signature language "
                                f"associated with {reference_name}: '{phrase}'."
                            ),
                            recommendation=(
                                "Redesign the repeat, silhouette, hardware, naming, or surface language "
                                "using House of Frazier geometry and mythology."
                            ),
                        )
                    )
        return findings


class LuxuryCritiqueEngine:
    def critique(self, concept: DesignConcept, genome: DesignGenome) -> List[CritiqueFinding]:
        findings: List[CritiqueFinding] = []
        score_map = genome.as_dict()

        for category, score in score_map.items():
            if score < 55:
                findings.append(
                    CritiqueFinding(
                        category=category,
                        severity="high" if score < 40 else "medium",
                        observation=f"{category.replace('_', ' ').title()} scored {score:.1f}/100.",
                        recommendation=self._recommendation(category),
                    )
                )

        if not concept.repair_plan.strip():
            findings.append(
                CritiqueFinding(
                    category="repairability",
                    severity="medium",
                    observation="No repair or service plan is documented.",
                    recommendation="Define replaceable hardware, repair access, lining service, and restoration steps.",
                )
            )

        if len(concept.patterns) > 3:
            findings.append(
                CritiqueFinding(
                    category="restraint",
                    severity="medium",
                    observation="The concept uses several pattern systems at once and may become visually crowded.",
                    recommendation="Choose one dominant pattern, one supporting detail, and move the rest to hidden layers.",
                )
            )

        if not concept.manufacturing_notes.strip():
            findings.append(
                CritiqueFinding(
                    category="manufacturability",
                    severity="high",
                    observation="The design lacks a manufacturing approach.",
                    recommendation="Document construction order, tools, tolerances, stress points, and service access.",
                )
            )

        return findings

    @staticmethod
    def _recommendation(category: str) -> str:
        recommendations = {
            "beauty": "Review proportion, focal point, visual weight, and silhouette before adding detail.",
            "story": "Strengthen one clear narrative idea and remove symbols that do not support it.",
            "engineering": "Resolve load paths, movement, attachment points, and failure modes.",
            "craftsmanship": "Specify seams, edges, tolerances, finishing, and quality checkpoints.",
            "materials": "Choose materials by behavior, aging, compatibility, and repair needs.",
            "innovation": "Add a useful advancement rather than novelty for its own sake.",
            "originality": "Replace borrowed visual language with Frazier-owned geometry, symbols, and hardware.",
            "repairability": "Make common failure components replaceable and document restoration procedures.",
            "longevity": "Improve wear surfaces, reinforcement, finish durability, and aging strategy.",
            "manufacturability": "Reduce unnecessary complexity and define a realistic build sequence.",
            "comfort": "Test contact points, weight distribution, movement, heat, and long-duration use.",
            "emotional_impact": "Clarify the intended feeling and connect it to form, material, and story.",
        }
        return recommendations.get(category, "Review the weak category and document a measurable improvement.")
