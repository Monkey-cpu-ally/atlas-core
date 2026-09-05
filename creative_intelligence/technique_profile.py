"""Deterministic synthesis of Art Study records into reusable technique profiles.

Profiles preserve provenance and safety boundaries. They describe transferable craft
principles and construction processes; they are never creator-style cloning recipes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from creative_intelligence.art_study import ArtStudy


@dataclass(frozen=True)
class TechniqueProfile:
    source_ids: Tuple[str, ...]
    media: Tuple[str, ...]
    dimensions: Tuple[str, ...]
    observations: Tuple[str, ...]
    principles: Tuple[str, ...]
    construction_steps: Tuple[str, ...]
    limitations: Tuple[str, ...]
    provenance: Tuple[str, ...]
    principles_only: bool = True
    direct_imitation_forbidden: bool = True
    project_identity_authoritative: bool = True

    def as_dict(self) -> dict:
        return {
            "source_ids": list(self.source_ids), "media": list(self.media),
            "dimensions": list(self.dimensions), "observations": list(self.observations),
            "principles": list(self.principles), "construction_steps": list(self.construction_steps),
            "limitations": list(self.limitations), "provenance": list(self.provenance),
            "principles_only": self.principles_only,
            "direct_imitation_forbidden": self.direct_imitation_forbidden,
            "project_identity_authoritative": self.project_identity_authoritative,
        }


def _unique(values: Iterable[str]) -> Tuple[str, ...]:
    seen=set(); result=[]
    for value in values:
        key=value.casefold()
        if key not in seen: seen.add(key); result.append(value)
    return tuple(result)


def synthesize_technique_profile(studies: Iterable[ArtStudy]) -> TechniqueProfile:
    """Combine validated studies without weakening provenance or source identity."""
    records=tuple(studies)
    if not records: raise ValueError("at least one validated ArtStudy is required")
    if not all(isinstance(study,ArtStudy) for study in records): raise ValueError("technique profiles accept only validated ArtStudy records")
    source_keys=[study.source_id.casefold() for study in records]
    if len(source_keys)!=len(set(source_keys)):
        raise ValueError("duplicate ArtStudy source_id is not allowed in one technique profile")
    return TechniqueProfile(
        source_ids=tuple(study.source_id for study in records),
        media=_unique(study.medium for study in records),
        dimensions=_unique(d for study in records for d in study.dimensions),
        observations=_unique(i for study in records for i in study.observations),
        principles=_unique(i for study in records for i in study.transferable_principles),
        construction_steps=_unique(i for study in records for i in study.construction_steps),
        limitations=_unique(i for study in records for i in study.limitations),
        provenance=_unique(i for study in records for i in study.provenance),
    )
