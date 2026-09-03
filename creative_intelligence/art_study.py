"""ATLAS Art Study Engine: converts visual references into transferable craft knowledge.

This module deliberately studies construction principles rather than creator imitation.
It is generation-provider agnostic: analysis evidence must exist before learned craft
can participate in Creative Studio production.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

ART_STUDY_DIMENSIONS = (
    "construction",
    "line_and_mark",
    "composition",
    "color_and_light",
    "character_design",
    "environment_design",
    "motion_and_timing",
    "materials_and_texture",
)

AI_ROLES = {
    "minerva": ("art_history", "meaning", "visual_language", "research_context"),
    "hermes": ("construction", "perspective", "materials", "technical_execution"),
    "ajani": ("readability", "impact", "staging", "audience_experience"),
}

@dataclass(frozen=True)
class ArtStudy:
    source_id: str
    medium: str
    observations: Tuple[str, ...]
    transferable_principles: Tuple[str, ...]
    construction_steps: Tuple[str, ...]
    limitations: Tuple[str, ...]
    provenance: Tuple[str, ...]
    dimensions: Tuple[str, ...]

    @staticmethod
    def _strings(value, field: str, *, required: bool = True) -> Tuple[str, ...]:
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"{field} must be a list of strings")
        cleaned = tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
        if required and not cleaned:
            raise ValueError(f"{field} must contain non-empty strings")
        if len(cleaned) != len(value):
            raise ValueError(f"{field} must contain only non-empty strings")
        if len({item.casefold() for item in cleaned}) != len(cleaned):
            raise ValueError(f"duplicate values are not allowed in {field}")
        return cleaned

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "ArtStudy":
        if not isinstance(payload, Mapping):
            raise ValueError("art study must be an object")
        source_id = payload.get("source_id")
        medium = payload.get("medium")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("source_id is required")
        if not isinstance(medium, str) or not medium.strip():
            raise ValueError("medium is required")
        dimensions = cls._strings(payload.get("dimensions", ()), "dimensions")
        unknown = set(dimensions) - set(ART_STUDY_DIMENSIONS)
        if unknown:
            raise ValueError(f"unknown art study dimensions: {', '.join(sorted(unknown))}")
        limitations = cls._strings(payload.get("limitations", ()), "limitations")
        if not any("imitat" in rule.casefold() or "copy" in rule.casefold() for rule in limitations):
            raise ValueError("art study must declare an anti-imitation limitation")
        provenance = cls._strings(payload.get("provenance", ()), "provenance")
        return cls(
            source_id.strip(),
            medium.strip(),
            cls._strings(payload.get("observations", ()), "observations"),
            cls._strings(payload.get("transferable_principles", ()), "transferable_principles"),
            cls._strings(payload.get("construction_steps", ()), "construction_steps"),
            limitations,
            provenance,
            dimensions,
        )


def study_contract() -> dict:
    """Stable contract consumed by future analyzers, Knowledge Bank, and Creative Studio."""
    return {
        "dimensions": list(ART_STUDY_DIMENSIONS),
        "ai_roles": {name: list(roles) for name, roles in AI_ROLES.items()},
        "principles_only": True,
        "direct_imitation_forbidden": True,
        "project_identity_overrides_study_influence": True,
        "provenance_required": True,
        "evidence_required_before_generation": True,
    }
