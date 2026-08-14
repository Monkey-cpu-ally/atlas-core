"""Reference intelligence for ATLAS creative systems.

This module converts creator/work references into reusable craft principles.
It deliberately retrieves multiple references and produces synthesis guidance
instead of instructing ATLAS to imitate a single creator's distinctive style.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

from .masters_library import CREATIVE_MASTERS


@dataclass(frozen=True)
class ReferencePrinciple:
    source: str
    principle: str
    application: str
    tags: tuple[str, ...] = ()


@dataclass
class ReferenceSynthesis:
    goal: str
    references: List[str] = field(default_factory=list)
    principles: List[ReferencePrinciple] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    synthesis_questions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "references": self.references,
            "principles": [p.__dict__ for p in self.principles],
            "constraints": self.constraints,
            "synthesis_questions": self.synthesis_questions,
        }


class ReferenceIntelligenceEngine:
    """Retrieve craft references and turn them into original-design guidance."""

    def search(self, terms: Iterable[str], limit: int = 8) -> List[str]:
        wanted = {term.casefold() for term in terms if term.strip()}
        scored: list[tuple[int, str]] = []
        for name, profile in CREATIVE_MASTERS.items():
            haystack = " ".join(
                [name, *profile.craft_focus, profile.atlas_use]
            ).casefold()
            score = sum(1 for term in wanted if term in haystack)
            if score:
                scored.append((score, name))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [name for _, name in scored[:limit]]

    def extract_principles(self, names: Sequence[str]) -> List[ReferencePrinciple]:
        principles: List[ReferencePrinciple] = []
        for name in names:
            profile = CREATIVE_MASTERS.get(name)
            if not profile:
                continue
            for focus in profile.craft_focus:
                principles.append(
                    ReferencePrinciple(
                        source=name,
                        principle=focus,
                        application=profile.atlas_use,
                        tags=tuple(domain.value for domain in profile.domains),
                    )
                )
        return principles

    def synthesize(
        self,
        goal: str,
        terms: Iterable[str],
        *,
        project_constraints: Sequence[str] = (),
        minimum_references: int = 3,
        limit: int = 8,
    ) -> ReferenceSynthesis:
        references = self.search(terms, limit=limit)
        if len(references) < minimum_references:
            # Add high-priority references for diversity rather than pretending
            # a narrow match is enough to define a creative direction.
            ranked = sorted(
                CREATIVE_MASTERS.values(),
                key=lambda profile: (-profile.priority, profile.name),
            )
            for profile in ranked:
                if profile.name not in references:
                    references.append(profile.name)
                if len(references) >= minimum_references:
                    break

        return ReferenceSynthesis(
            goal=goal,
            references=references,
            principles=self.extract_principles(references),
            constraints=[
                *project_constraints,
                "Use references as craft evidence, not imitation targets.",
                "Combine principles from multiple sources.",
                "Preserve project lore, function, audience, and cultural context.",
                "Reject results that depend on recognizable copying of one creator.",
            ],
            synthesis_questions=[
                "Which principles solve the actual project problem?",
                "Which references disagree, and what can ATLAS learn from that tension?",
                "How can function, history, and materials change the familiar solution?",
                "What can be removed while preserving the strongest idea?",
                "What makes the result belong to this project rather than its references?",
            ],
        )
