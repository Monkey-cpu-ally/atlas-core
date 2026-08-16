"""ATLAS Art Style Director: project-specific visual-language governance."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ArtStyleBible:
    project: str
    shape_language: str
    silhouette_rules: str
    anatomy_proportions: str
    line_edge_treatment: str
    palette_logic: str
    lighting_philosophy: str
    texture_material_language: str
    environment_architecture: str
    facial_expression_language: str
    composition_perspective: str
    detail_policy: str
    animation_principles: str
    forbidden_traits: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArtStyleAssessment:
    scores: Dict[str, int]
    violations: List[str]
    warnings: List[str]

    @property
    def average(self) -> float:
        return sum(self.scores.values()) / len(self.scores) if self.scores else 0.0

    @property
    def production_ready(self) -> bool:
        hard = ("style_identity", "character_consistency", "visual_coherence", "originality")
        return not self.violations and self.average >= 90 and all(self.scores.get(k, 0) >= 90 for k in hard)


class ArtStyleDirector:
    """Rejects generic, derivative, drifting, or internally incoherent visual direction."""

    DIMENSIONS = (
        "style_identity", "originality", "shape_language", "silhouette_readability",
        "character_consistency", "palette_coherence", "lighting_coherence", "material_coherence",
        "environment_coherence", "composition", "perspective", "detail_control", "visual_coherence",
    )

    GENERIC_MARKERS = (
        "generic ai", "prompt soup", "plastic skin", "random neon", "cinematic wallpaper",
        "over-rendered", "style drift", "cheap 3d", "stock concept art", "default anime",
    )
    DERIVATIVE_MARKERS = ("copy", "clone", "trace", "exactly like", "identical to", "replicate")

    def assess(self, bible: ArtStyleBible, *, observations: List[str], scores: Dict[str, int]) -> ArtStyleAssessment:
        normalized = {k: max(0, min(100, int(scores.get(k, 0)))) for k in self.DIMENSIONS}
        text = " ".join(observations).lower()
        violations: List[str] = []
        warnings: List[str] = []

        if any(marker in text for marker in self.DERIVATIVE_MARKERS):
            violations.append("derivative_reference_imitation")
        if normalized["style_identity"] < 90:
            violations.append("weak_project_visual_identity")
        if normalized["originality"] < 90:
            violations.append("insufficient_visual_originality")
        if normalized["character_consistency"] < 90:
            violations.append("character_style_drift")
        if normalized["visual_coherence"] < 90:
            violations.append("incoherent_visual_language")
        if any(marker in text for marker in self.GENERIC_MARKERS):
            warnings.append("generic_or_cheap_visual_tendency")

        for forbidden in bible.forbidden_traits:
            if forbidden.lower() in text:
                violations.append(f"forbidden_trait:{forbidden}")

        return ArtStyleAssessment(normalized, list(dict.fromkeys(violations)), list(dict.fromkeys(warnings)))
