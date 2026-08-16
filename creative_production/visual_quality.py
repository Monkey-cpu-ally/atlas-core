"""ATLAS Visual Quality Director: strict technical and aesthetic asset QA."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class VisualQualityAssessment:
    scores: Dict[str, int]
    violations: List[str]
    warnings: List[str]

    @property
    def average(self) -> float:
        return sum(self.scores.values()) / len(self.scores) if self.scores else 0.0

    @property
    def production_ready(self) -> bool:
        hard = (
            "anatomy", "face_integrity", "hand_integrity", "identity_consistency",
            "artifact_free", "perspective_geometry", "resolution_fidelity",
        )
        return not self.violations and self.average >= 95 and all(self.scores.get(k, 0) >= 95 for k in hard)


class VisualQualityDirector:
    """Rejects technically flawed, inconsistent, generic, or visibly synthetic production assets."""

    DIMENSIONS = (
        "anatomy", "face_integrity", "hand_integrity", "identity_consistency",
        "pose_physics", "perspective_geometry", "lighting_consistency", "shadow_consistency",
        "material_fidelity", "edge_integrity", "artifact_free", "background_geometry",
        "costume_accuracy", "prop_accuracy", "composition", "focal_hierarchy",
        "resolution_fidelity", "texture_fidelity", "style_fidelity", "production_polish",
    )

    HARD_FLOOR = 95
    OVERALL_FLOOR = 95

    DEFECT_MARKERS = {
        "extra fingers": "hand_defect",
        "missing fingers": "hand_defect",
        "fused fingers": "hand_defect",
        "warped hand": "hand_defect",
        "asymmetric eyes": "face_defect",
        "warped face": "face_defect",
        "identity drift": "identity_drift",
        "extra limb": "anatomy_defect",
        "missing limb": "anatomy_defect",
        "broken anatomy": "anatomy_defect",
        "melted": "generation_artifact",
        "watermark": "unwanted_text_or_watermark",
        "unwanted text": "unwanted_text_or_watermark",
        "broken perspective": "perspective_failure",
        "impossible shadow": "lighting_shadow_failure",
        "background warp": "background_geometry_failure",
        "low resolution": "insufficient_resolution",
        "pixelated": "insufficient_resolution",
        "style drift": "style_drift",
        "plastic skin": "synthetic_material_look",
        "generic ai": "generic_generated_look",
    }

    def assess(self, *, observations: List[str], scores: Dict[str, int]) -> VisualQualityAssessment:
        normalized = {k: max(0, min(100, int(scores.get(k, 0)))) for k in self.DIMENSIONS}
        text = " ".join(observations).lower()
        violations: List[str] = []
        warnings: List[str] = []

        hard_dimensions = (
            "anatomy", "face_integrity", "hand_integrity", "identity_consistency",
            "artifact_free", "perspective_geometry", "resolution_fidelity",
        )
        for dimension in hard_dimensions:
            if normalized[dimension] < self.HARD_FLOOR:
                violations.append(f"hard_quality_failure:{dimension}")

        for marker, code in self.DEFECT_MARKERS.items():
            if marker in text:
                if code in {"synthetic_material_look", "generic_generated_look"}:
                    warnings.append(code)
                else:
                    violations.append(code)

        if normalized["production_polish"] < 90:
            violations.append("insufficient_production_polish")
        if normalized["style_fidelity"] < 90:
            violations.append("style_fidelity_failure")
        if normalized["costume_accuracy"] < 90:
            violations.append("costume_continuity_failure")
        if normalized["prop_accuracy"] < 90:
            violations.append("prop_continuity_failure")

        return VisualQualityAssessment(
            normalized,
            list(dict.fromkeys(violations)),
            list(dict.fromkeys(warnings)),
        )
