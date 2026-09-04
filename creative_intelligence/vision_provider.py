"""Provider-independent vision boundary for ATLAS Art Study.

Adapters may call cloud or local multimodal models, but they must return the same
validated VisualAnalysis contract. Provider output never bypasses rights, provenance,
confidence, or anti-imitation validation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping

from creative_intelligence.technique_profile import TechniqueProfile, synthesize_technique_profile
from creative_intelligence.visual_analysis import VisualAnalysis


class VisionProvider(ABC):
    """Minimal adapter contract implemented by a concrete multimodal provider."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def analyze(self, source_reference: str, request: Mapping[str, object]) -> Mapping[str, object]:
        """Return structured evidence only; raw prose is not accepted by the pipeline."""
        raise NotImplementedError


@dataclass(frozen=True)
class ArtStudyPipelineResult:
    analysis: VisualAnalysis
    profile: TechniqueProfile


def run_art_study_pipeline(
    provider: VisionProvider,
    source_reference: str,
    source_metadata: Mapping[str, object],
    request: Mapping[str, object],
    *,
    minimum_confidence: float = 0.60,
) -> ArtStudyPipelineResult:
    if not isinstance(provider, VisionProvider):
        raise ValueError("provider must implement VisionProvider")
    if not isinstance(source_reference, str) or not source_reference.strip():
        raise ValueError("source_reference is required")
    if not isinstance(source_metadata, Mapping):
        raise ValueError("source_metadata must be an object")
    if not isinstance(request, Mapping):
        raise ValueError("request must be an object")

    raw = provider.analyze(source_reference.strip(), request)
    if not isinstance(raw, Mapping):
        raise ValueError("vision provider must return structured analysis")

    payload = dict(raw)
    declared_provider = payload.get("provider")
    if declared_provider is None:
        payload["provider"] = provider.provider_id
    elif declared_provider != provider.provider_id:
        raise ValueError("vision provider identity mismatch")

    analysis = VisualAnalysis.from_mapping(payload)
    study = analysis.to_art_study(source_metadata, minimum_confidence=minimum_confidence)
    profile = synthesize_technique_profile([study])
    return ArtStudyPipelineResult(analysis=analysis, profile=profile)


def provider_contract() -> dict:
    return {
        "provider_independent": True,
        "structured_evidence_only": True,
        "provider_identity_verified": True,
        "rights_and_provenance_validation_required": True,
        "confidence_gate_required": True,
        "direct_imitation_forbidden": True,
        "project_identity_authoritative": True,
    }
