"""Knowledge Bank bridge for validated ATLAS Art Study technique profiles."""
from __future__ import annotations

import json
from typing import Dict, List

from backend.services import memory_bank
from creative_intelligence.art_study import AI_ROLES
from creative_intelligence.technique_profile import TechniqueProfile

PERSONAS = ("ajani", "minerva", "hermes")


def _profile_content(profile: TechniqueProfile) -> str:
    if not isinstance(profile, TechniqueProfile):
        raise ValueError("validated TechniqueProfile is required")
    if not profile.principles_only or not profile.direct_imitation_forbidden:
        raise ValueError("unsafe technique profile cannot enter Knowledge Bank")
    return json.dumps(profile.as_dict(), sort_keys=True, separators=(",", ":"))


def interpretation_for(persona: str, profile: TechniqueProfile) -> Dict[str, object]:
    name = (persona or "").lower()
    if name not in PERSONAS:
        raise ValueError("persona must be ajani, minerva, or hermes")
    _profile_content(profile)
    return {
        "persona": name,
        "role_focus": list(AI_ROLES[name]),
        "principles": list(profile.principles),
        "construction_steps": list(profile.construction_steps),
        "dimensions": list(profile.dimensions),
        "source_ids": list(profile.source_ids),
        "provenance": list(profile.provenance),
        "direct_imitation_forbidden": True,
        "project_identity_authoritative": True,
    }


async def store_profile(profile: TechniqueProfile) -> Dict[str, object]:
    """Persist one canonical shared-bank profile; fail closed if storage fails."""
    content = _profile_content(profile)
    source_id = profile.source_ids[0] if len(profile.source_ids) == 1 else "art-study:multi-source"
    row = await memory_bank.auto_store(
        content,
        persona="council",
        category="research",
        source_type="art_study_technique_profile",
        source_id=source_id,
        tags=["art-study", "technique-profile", *profile.dimensions],
    )
    if row is None:
        raise RuntimeError("Art Study Knowledge Bank persistence failed")
    return row


async def retrieve_profiles(query: str, *, top_k: int = 5) -> List[Dict[str, object]]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query is required")
    rows = await memory_bank.search_memory(
        query.strip(), persona="council", category="research", top_k=top_k, min_score=0.0
    )
    return [row for row in rows if row.get("source_type") == "art_study_technique_profile"]


def council_interpretations(profile: TechniqueProfile) -> Dict[str, Dict[str, object]]:
    return {persona: interpretation_for(persona, profile) for persona in PERSONAS}
