"""Teaching engine — PhD depth, 6th-grade clarity, adult respect.

Pipeline:
  1) Pick the right core for the subject (default: Minerva for soft
     subjects, Hermes for STEM, Ajani for skills/strategy).
  2) Ask that core to teach the topic at four nested depth bands:
       • SEED      — one sentence, no jargon.
       • SHAPE     — short paragraph with one analogy.
       • SUBSTANCE — full explanation, terminology introduced *after* use.
       • SHADOWS   — failure modes, edge cases, what we still do not know.

The caller can request any subset of bands.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from cores import get_core


DEFAULT_BANDS = ["seed", "shape", "substance", "shadows"]


def _pick_core(topic: str) -> str:
    """Crude domain router. Replaceable later with a learned classifier."""
    t = topic.lower()
    stem = ("math", "physics", "chemistry", "code", "algorithm", "computer",
            "quantum", "engineering", "data structure")
    soft = ("history", "philosophy", "psychology", "ethics", "culture",
            "art", "story", "language", "religion", "myth")
    if any(k in t for k in stem):
        return "hermes"
    if any(k in t for k in soft):
        return "minerva"
    return "ajani"


BAND_PROMPTS = {
    "seed": (
        "Explain the SEED of this topic in ONE sentence using everyday "
        "words. Anyone aged 11+ must understand it."
    ),
    "shape": (
        "Now give the SHAPE: a short paragraph (3-5 sentences) with one "
        "concrete analogy. Still no jargon."
    ),
    "substance": (
        "Now give the SUBSTANCE: a full explanation. Use technical terms "
        "ONLY AFTER showing the everyday version. Treat the reader as a "
        "smart adult; never condescend."
    ),
    "shadows": (
        "Finally, the SHADOWS: list 3-5 failure modes, edge cases, common "
        "misconceptions, or open questions. Be specific."
    ),
}


async def teach(
    topic: str,
    *,
    core: Optional[str] = None,
    bands: Optional[List[str]] = None,
    context: Optional[str] = None,
) -> Dict:
    """Teach `topic` at the requested depth bands."""
    core_key = (core or _pick_core(topic)).lower()
    teacher = get_core(core_key)
    use_bands = [b for b in (bands or DEFAULT_BANDS) if b in BAND_PROMPTS]

    instructions = "\n".join(
        f"### {b.upper()}\n{BAND_PROMPTS[b]}" for b in use_bands
    )
    full_prompt = (
        f"Teach this topic: {topic!r}\n\n"
        f"Return your answer with each band as a markdown heading exactly "
        f"matching this template:\n\n{instructions}\n\n"
        "Doctrine reminders:\n"
        " - PhD depth, 6th-7th grade clarity, adult respect.\n"
        " - No academic fluff. No 'in conclusion'. No 'as we have seen'.\n"
        " - Concrete examples first, terms second.\n"
    )

    answer = await teacher.think(full_prompt, context=context)
    return {
        "topic": topic,
        "teacher": core_key,
        "bands_requested": use_bands,
        "lesson": answer,
    }
