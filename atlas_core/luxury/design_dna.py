from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt


DNA_DIMENSIONS = (
    "heritage",
    "modernity",
    "elegance",
    "utility",
    "boldness",
    "innovation",
    "craftsmanship",
    "repairability",
    "exclusivity",
)


@dataclass(slots=True, frozen=True)
class DesignDNA:
    product_id: str
    values: dict[str, float]
    silhouette_tags: frozenset[str] = field(default_factory=frozenset)
    material_tags: frozenset[str] = field(default_factory=frozenset)
    pattern_family: str | None = None
    hardware_family: str | None = None

    def __post_init__(self) -> None:
        missing = set(DNA_DIMENSIONS) - self.values.keys()
        if missing:
            raise ValueError(f"Missing DNA dimensions: {sorted(missing)}")
        invalid = {key: value for key, value in self.values.items() if not 0 <= value <= 100}
        if invalid:
            raise ValueError(f"DNA values must be between 0 and 100: {invalid}")


@dataclass(slots=True, frozen=True)
class DNAComparison:
    similarity: float
    shared_silhouettes: tuple[str, ...]
    shared_materials: tuple[str, ...]
    same_pattern_family: bool
    same_hardware_family: bool


class DesignDNAEngine:
    """Compare products against House of Frazier identity without forcing repetition."""

    @staticmethod
    def compare(left: DesignDNA, right: DesignDNA) -> DNAComparison:
        a = [left.values[key] for key in DNA_DIMENSIONS]
        b = [right.values[key] for key in DNA_DIMENSIONS]
        distance = sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
        max_distance = sqrt(len(DNA_DIMENSIONS) * (100**2))
        numeric_similarity = max(0.0, 100 * (1 - distance / max_distance))

        shared_silhouettes = tuple(sorted(left.silhouette_tags & right.silhouette_tags))
        shared_materials = tuple(sorted(left.material_tags & right.material_tags))
        pattern_match = bool(left.pattern_family and left.pattern_family == right.pattern_family)
        hardware_match = bool(left.hardware_family and left.hardware_family == right.hardware_family)

        identity_bonus = min(
            12.0,
            len(shared_silhouettes) * 2.0
            + len(shared_materials) * 1.0
            + (4.0 if pattern_match else 0.0)
            + (4.0 if hardware_match else 0.0),
        )
        similarity = round(min(100.0, numeric_similarity * 0.88 + identity_bonus), 2)
        return DNAComparison(
            similarity=similarity,
            shared_silhouettes=shared_silhouettes,
            shared_materials=shared_materials,
            same_pattern_family=pattern_match,
            same_hardware_family=hardware_match,
        )

    def identity_status(self, candidate: DesignDNA, house_reference: DesignDNA) -> str:
        similarity = self.compare(candidate, house_reference).similarity
        if similarity < 45:
            return "design_drift"
        if similarity > 92:
            return "too_repetitive"
        return "aligned"
