"""Evidence-bound visual analysis contract for ATLAS Art Study.

This module does not claim to see pixels. A vision provider must supply structured
observations tied to source regions/frames. ATLAS validates that evidence before it can
become an ArtStudy and later a TechniqueProfile.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from creative_intelligence.art_study import ART_STUDY_DIMENSIONS, ArtStudy


@dataclass(frozen=True)
class VisualEvidence:
    locator: str
    dimension: str
    observation: str
    confidence: float

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "VisualEvidence":
        if not isinstance(payload, Mapping):
            raise ValueError("visual evidence must be an object")
        locator = payload.get("locator")
        dimension = payload.get("dimension")
        observation = payload.get("observation")
        confidence = payload.get("confidence")
        if not isinstance(locator, str) or not locator.strip():
            raise ValueError("visual evidence locator is required")
        if dimension not in ART_STUDY_DIMENSIONS:
            raise ValueError("visual evidence dimension must be a known Art Study dimension")
        if not isinstance(observation, str) or not observation.strip():
            raise ValueError("visual evidence observation is required")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ValueError("visual evidence confidence must be numeric")
        confidence = float(confidence)
        if confidence < 0.0 or confidence > 1.0:
            raise ValueError("visual evidence confidence must be between 0 and 1")
        return cls(locator.strip(), str(dimension), observation.strip(), confidence)


@dataclass(frozen=True)
class VisualAnalysis:
    provider: str
    evidence: Tuple[VisualEvidence, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "VisualAnalysis":
        if not isinstance(payload, Mapping):
            raise ValueError("visual analysis must be an object")
        provider = payload.get("provider")
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("visual analysis provider is required")
        raw_evidence = payload.get("evidence")
        if not isinstance(raw_evidence, (list, tuple)) or not raw_evidence:
            raise ValueError("visual analysis requires evidence")
        evidence = tuple(VisualEvidence.from_mapping(item) for item in raw_evidence)
        return cls(provider.strip(), evidence)

    def to_art_study(self, source: Mapping[str, object], *, minimum_confidence: float = 0.60) -> ArtStudy:
        if minimum_confidence < 0.0 or minimum_confidence > 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        accepted = tuple(item for item in self.evidence if item.confidence >= minimum_confidence)
        if not accepted:
            raise ValueError("no visual evidence meets the confidence threshold")

        payload = dict(source)
        payload["observations"] = list(dict.fromkeys(item.observation for item in accepted))
        payload["dimensions"] = list(dict.fromkeys(item.dimension for item in accepted))
        provenance = payload.get("provenance")
        if not isinstance(provenance, (list, tuple)):
            raise ValueError("source provenance must be a list before visual analysis")
        payload["provenance"] = list(provenance) + [f"visual-analysis-provider:{self.provider}"]
        return ArtStudy.from_mapping(payload)


def analyzer_contract() -> dict:
    return {
        "pixel_analysis_implemented_here": False,
        "external_vision_evidence_required": True,
        "evidence_locator_required": True,
        "dimension_bound_evidence_required": True,
        "confidence_required": True,
        "rights_checked_by_art_study": True,
        "principles_only": True,
        "direct_imitation_forbidden": True,
    }
