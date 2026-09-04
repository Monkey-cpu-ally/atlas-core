"""Callable Art Study runtime pipeline used by Creative Studio API."""
from __future__ import annotations

from typing import Mapping

from backend.services.art_study_knowledge import council_interpretations
from creative_intelligence.technique_profile import TechniqueProfile
from creative_intelligence.vision_provider import VisionProvider, analyze_to_technique_profile
from creative_intelligence.visual_direction import build_visual_direction, generation_context


def run_art_study(
    *,
    provider: VisionProvider,
    request: Mapping[str, object],
    source: Mapping[str, object],
    project_identity: str,
    project_constraints: list[str] | tuple[str, ...],
    minimum_confidence: float = 0.60,
) -> dict:
    """Execute provider -> evidence -> ArtStudy -> profile -> ATLAS visual direction."""
    profile: TechniqueProfile = analyze_to_technique_profile(
        provider, request, source, minimum_confidence=minimum_confidence
    )
    direction = build_visual_direction(
        profile,
        project_identity=project_identity,
        project_constraints=project_constraints,
    )
    return {
        "technique_profile": profile.as_dict(),
        "ai_interpretations": council_interpretations(profile),
        "visual_direction": dict(generation_context(direction)),
        "runtime_contract": {
            "validated_evidence_required": True,
            "rights_declaration_required": True,
            "principles_only": True,
            "direct_imitation_forbidden": True,
            "project_identity_authoritative": True,
        },
    }
