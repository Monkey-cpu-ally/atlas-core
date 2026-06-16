"""Teaching engine — ATLAS teaching law.

The teaching law (per architect-in-chief): PhD-level depth, 6th–7th grade
clarity, adult respect, no academic fluff. Concrete examples first,
terminology second. Always teach failure modes early.

Pipeline:

  1) Determine the LEAD CORE via the council router (`council.route`) so the
     "right voice" teaches each topic.
  2) Generate FOUR layered explanations at distinct depths:

         simple        — one short paragraph, everyday words, no jargon
         systems       — how it connects to other things, the big picture
         advanced      — full PhD-depth treatment with terminology
         speculative   — open questions, research frontiers, what we still
                         don't know, healthy skepticism

The four bands are alias-friendly: the legacy aliases (`seed`, `shape`,
`substance`, `shadows`) still work so callers do not break.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..cores import get_core
from ..council.router import route_internal as council_route


# Canonical band order matches what the user requested.
DEFAULT_BANDS: List[str] = ["simple", "systems", "advanced", "speculative"]

# Backwards-compatible aliases for the prior naming.
_BAND_ALIASES = {
    "seed":      "simple",
    "shape":     "systems",
    "substance": "advanced",
    "shadows":   "speculative",
}


BAND_PROMPTS: Dict[str, str] = {
    "simple": (
        "Give a SIMPLE understanding. One short paragraph (3-5 sentences) "
        "using only everyday words. No jargon. A curious 11-year-old must "
        "follow it. Use one concrete analogy."
    ),
    "systems": (
        "Now give the SYSTEMS understanding. Explain how this topic "
        "connects to neighboring fields and to the bigger system it lives "
        "in. Show 3-5 connections, each in one or two sentences. Use "
        "high-school vocabulary."
    ),
    "advanced": (
        "Now give the ADVANCED understanding: PhD-level depth, but written "
        "with full clarity. Introduce technical terms ONLY AFTER the "
        "everyday meaning is clear. Cover mechanisms, key equations or "
        "models, and current best-practice. Treat the reader as a smart "
        "adult — never condescend."
    ),
    "speculative": (
        "Finally, the SPECULATIVE / RESEARCH understanding: list 3-5 open "
        "questions, frontier debates, common misconceptions, or "
        "controversial claims. Note what we still do NOT know. Where "
        "speculative, label it clearly."
    ),
}


def _normalize_band(b: str) -> str:
    """Map legacy aliases to canonical names."""
    b = b.lower().strip()
    return _BAND_ALIASES.get(b, b)


def _pick_core(topic: str) -> str:
    """Lead-core routing via the council heuristic.

    The teaching engine's "determine the lead core" step uses the same
    keyword scoring the council uses, so a STEM topic goes to Hermes, a
    cultural topic goes to Minerva, and a build/strategy topic goes to
    Ajani. This keeps routing consistent with `/api/atlas/council/preview`.
    """
    decision = council_route(topic)
    return decision.lead


async def teach(
    topic: str,
    *,
    core: Optional[str] = None,
    bands: Optional[List[str]] = None,
    context: Optional[str] = None,
) -> Dict:
    """Teach `topic` at the requested depth bands.

    Returns:
        {
          "topic":            <str>,
          "teacher":          <core_key>,        # who taught it
          "lead_via_council": <bool>,            # True iff core was auto-picked
          "bands_requested":  ["simple", ...],   # canonical names
          "lesson":           <markdown str>,    # one block, headed per band
        }
    """
    auto_pick = core is None
    core_key = (core or _pick_core(topic)).lower()
    teacher = get_core(core_key)

    requested = [_normalize_band(b) for b in (bands or DEFAULT_BANDS)]
    use_bands = [b for b in requested if b in BAND_PROMPTS]

    instructions = "\n".join(
        f"### {b.upper()}\n{BAND_PROMPTS[b]}" for b in use_bands
    )
    full_prompt = (
        f"Teach this topic: {topic!r}\n\n"
        f"Return your answer with each band as a markdown heading exactly "
        f"matching this template:\n\n{instructions}\n\n"
        "ATLAS TEACHING LAW:\n"
        " - PhD depth, 6th-7th grade clarity, adult respect.\n"
        " - No academic fluff. No 'in conclusion'. No 'as we have seen'.\n"
        " - Concrete examples first, terminology second.\n"
        " - Surface failure modes and edge cases early, not at the end.\n"
        " - Admit uncertainty plainly; never fake confidence.\n"
    )

    answer = await teacher.think(full_prompt, context=context)
    return {
        "topic": topic,
        "teacher": core_key,
        "lead_via_council": auto_pick,
        "bands_requested": use_bands,
        "lesson": answer,
    }
