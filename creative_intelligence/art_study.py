"""ATLAS Art Study Engine: convert visual evidence into transferable craft knowledge.

Art Study records construction principles, not creator identity or a recipe for imitation.
Only traceable, rights-declared evidence may enter the study pipeline, and project identity
remains authoritative when study knowledge is later consumed by Creative Studio.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

ART_STUDY_DIMENSIONS = (
    "construction",
    "gesture",
    "anatomy",
    "proportion",
    "perspective",
    "shape_and_silhouette",
    "line_and_mark",
    "composition",
    "color_and_light",
    "character_design",
    "environment_design",
    "camera_and_staging",
    "motion_and_timing",
    "materials_and_texture",
)

ALLOWED_RIGHTS_BASIS = (
    "user_provided",
    "licensed",
    "public_domain",
    "authorized",
)

AI_ROLES = {
    "minerva": ("art_history", "meaning", "visual_language", "research_context"),
    "hermes": ("construction", "anatomy", "proportion", "perspective", "materials", "technical_execution"),
    "ajani": ("readability", "impact", "silhouette", "camera_and_staging", "audience_experience"),
}


@dataclass(frozen=True)
class ArtStudy:
    source_id: str
    medium: str
    source_kind: str
    rights_basis: str
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

    @staticmethod
    def _required_string(payload: Mapping[str, object], field: str) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required")
        return value.strip()

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "ArtStudy":
        if not isinstance(payload, Mapping):
            raise ValueError("art study must be an object")

        source_id = cls._required_string(payload, "source_id")
        medium = cls._required_string(payload, "medium")
        source_kind = cls._required_string(payload, "source_kind")
        rights_basis = cls._required_string(payload, "rights_basis").casefold()
        if rights_basis not in ALLOWED_RIGHTS_BASIS:
            raise ValueError(
                "rights_basis must be one of: " + ", ".join(ALLOWED_RIGHTS_BASIS)
            )

        dimensions = cls._strings(payload.get("dimensions", ()), "dimensions")
        unknown = set(dimensions) - set(ART_STUDY_DIMENSIONS)
        if unknown:
            raise ValueError(f"unknown art study dimensions: {', '.join(sorted(unknown))}")

        observations = cls._strings(payload.get("observations", ()), "observations")
        principles = cls._strings(
            payload.get("transferable_principles", ()), "transferable_principles"
        )
        construction_steps = cls._strings(
            payload.get("construction_steps", ()), "construction_steps"
        )
        limitations = cls._strings(payload.get("limitations", ()), "limitations")
        provenance = cls._strings(payload.get("provenance", ()), "provenance")

        if not any(
            "imitat" in rule.casefold()
            or "copy" in rule.casefold()
            or "distinctive expression" in rule.casefold()
            for rule in limitations
        ):
            raise ValueError("art study must declare an anti-imitation limitation")

        return cls(
            source_id=source_id,
            medium=medium,
            source_kind=source_kind,
            rights_basis=rights_basis,
            observations=observations,
            transferable_principles=principles,
            construction_steps=construction_steps,
            limitations=limitations,
            provenance=provenance,
            dimensions=dimensions,
        )


def study_contract() -> dict:
    """Stable contract consumed by analyzers, Knowledge Bank, and Creative Studio."""
    return {
        "dimensions": list(ART_STUDY_DIMENSIONS),
        "allowed_rights_basis": list(ALLOWED_RIGHTS_BASIS),
        "ai_roles": {name: list(roles) for name, roles in AI_ROLES.items()},
        "principles_only": True,
        "direct_imitation_forbidden": True,
        "project_identity_overrides_study_influence": True,
        "provenance_required": True,
        "rights_declaration_required": True,
        "evidence_required_before_generation": True,
    }
