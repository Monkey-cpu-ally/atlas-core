"""Reference inspiration provenance and originality firewall for ATLAS Creative Studio."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ReferenceInfluence:
    reference_id: str
    title: str
    medium: str
    extracted_principles: List[str]
    contribution: str


@dataclass(frozen=True)
class OriginalityAssessment:
    influences: List[ReferenceInfluence]
    similarity_scores: Dict[str, float]
    violations: List[str] = field(default_factory=list)

    @property
    def passes(self) -> bool:
        return not self.violations


class ReferenceProvenanceDirector:
    """Records what ATLAS learned from references while blocking close imitation."""

    MAX_SINGLE_REFERENCE_SIMILARITY = 0.70

    def assess(self, *, influences: List[ReferenceInfluence], similarity_scores: Dict[str, float],
               output_notes: List[str] = ()) -> OriginalityAssessment:
        violations: List[str] = []
        notes = " ".join(output_notes).lower()
        forbidden = ("trace", "clone", "copy exactly", "identical composition", "replicate exactly")

        if any(term in notes for term in forbidden):
            violations.append("direct_imitation_instruction")

        for influence in influences:
            if not influence.extracted_principles:
                violations.append(f"missing_extracted_principles:{influence.reference_id}")
            if not influence.contribution.strip():
                violations.append(f"missing_contribution_record:{influence.reference_id}")

        for reference_id, similarity in similarity_scores.items():
            bounded = max(0.0, min(1.0, float(similarity)))
            if bounded > self.MAX_SINGLE_REFERENCE_SIMILARITY:
                violations.append(f"reference_similarity_too_high:{reference_id}")

        return OriginalityAssessment(
            influences=influences,
            similarity_scores={k: max(0.0, min(1.0, float(v))) for k, v in similarity_scores.items()},
            violations=list(dict.fromkeys(violations)),
        )
