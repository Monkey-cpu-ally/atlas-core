"""Knowledge Bank bridge for validated ATLAS Art Study technique profiles."""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List

from backend.services import memory_bank
from creative_intelligence.art_study import AI_ROLES
from creative_intelligence.technique_profile import TechniqueProfile

PERSONAS = ("ajani", "minerva", "hermes")
SOURCE_TYPE = "art_study_technique_profile"


def _profile_content(profile: TechniqueProfile) -> str:
    if not isinstance(profile, TechniqueProfile):
        raise ValueError("validated TechniqueProfile is required")
    if not profile.principles_only or not profile.direct_imitation_forbidden:
        raise ValueError("unsafe technique profile cannot enter Knowledge Bank")
    return json.dumps(profile.as_dict(), sort_keys=True, separators=(",", ":"))


def _profile_source_id(profile: TechniqueProfile) -> str:
    """Stable identity for both single- and multi-source technique profiles."""
    if len(profile.source_ids) == 1:
        return profile.source_ids[0]
    canonical = "\n".join(sorted(source.casefold() for source in profile.source_ids))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
    return f"art-study:profile:{digest}"


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
    """Persist validated craft knowledge permanently; fail closed on storage failure."""
    content = _profile_content(profile)
    row = await memory_bank.store_memory(
        content,
        persona="council",
        category="council",
        source_type=SOURCE_TYPE,
        source_id=_profile_source_id(profile),
        tags=["art-study", "technique-profile", *profile.dimensions],
        pinned=True,
    )
    if row is None:
        raise RuntimeError("Art Study Knowledge Bank persistence failed")
    return row


async def retrieve_profiles(query: str, *, top_k: int = 5) -> List[Dict[str, object]]:
    """Retrieve from the permanent Council bank, overfetching before source filtering."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query is required")
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    rows = await memory_bank.search_memory(
        query.strip(), persona="council", category="council", top_k=max(top_k * 10, 50), min_score=0.0
    )
    matches = [row for row in rows if row.get("source_type") == SOURCE_TYPE]
    return matches[:top_k]


def council_interpretations(profile: TechniqueProfile) -> Dict[str, Dict[str, object]]:
    return {persona: interpretation_for(persona, profile) for persona in PERSONAS}
