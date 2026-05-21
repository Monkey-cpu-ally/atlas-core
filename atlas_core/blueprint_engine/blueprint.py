"""Blueprint engine — each core mentally simulates before answering.

Two flows:

  1. `design()` — original 5-phase plan flow (used by /api/atlas/blueprint).
  2. `tri_council()` — three voices in parallel + synthesis (used by the
     HUD's Blueprint Workbench).

In `tri_council()` each core is invoked with a specialized framing prompt:

  • Ajani   → STRUCTURAL / SYSTEM reasoning
  • Minerva → HUMAN / ECOSYSTEM / EMOTIONAL reasoning
  • Hermes  → ADAPTIVE / INVENTIVE reasoning

A fourth LLM call (the synthesizer) merges the three voices into a single
blueprint document. Calls happen in parallel via `asyncio.gather`.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Dict, Optional

from ..cores import CORES, get_core


async def _simulate_all(concept: str) -> Dict[str, str]:
    """Run all three cores' mental simulation in parallel."""
    tasks = {k: core.mental_simulate(concept) for k, core in CORES.items()}
    keys = list(tasks)
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    out: Dict[str, str] = {}
    for k, r in zip(keys, results):
        out[k] = f"[simulation failed: {r}]" if isinstance(r, Exception) else r
    return out


PLAN_PROMPT = """You are the ATLAS Blueprint Engine synthesizer. Given a
concept plus three private simulations (Ajani / Minerva / Hermes), produce a
five-phase plan. Output ONLY a JSON object:

{
  "concept": "<echoed>",
  "domain": "<elemental_kinetics | bio_genesis | nano_synthesis | other>",
  "phases": {
    "philosophy": { "core_belief": "...", "why_it_matters": "...", "ethical_anchors": ["..."] },
    "research":   { "known": ["..."], "unknown": ["..."], "prior_art": ["..."] },
    "blueprint":  { "components": ["..."], "data_flows": ["..."], "interfaces": ["..."] },
    "simulation": { "test_plan": ["..."], "success_criteria": ["..."], "risks": ["..."] },
    "physical":   { "build_steps": ["..."], "safety_gates": ["..."], "containment": ["..."] }
  },
  "minerva_concerns": ["..."],
  "hermes_validations": ["..."]
}

Every phase MUST include at least one safety_gate or ethical_anchor.
"""


def _extract_json(text: str) -> dict:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in plan response")
    return json.loads(match.group(0))


async def design(
    concept: str,
    *,
    with_plan: bool = True,
    synthesizer: str = "hermes",
) -> Dict:
    """Run the full blueprint cycle."""
    sims = await _simulate_all(concept)

    plan = None
    if with_plan:
        synth = get_core(synthesizer)
        body = json.dumps({"concept": concept, "simulations": sims}, indent=2)
        raw = await synth.think(
            f"{PLAN_PROMPT}\n\nINPUT:\n{body}",
        )
        try:
            plan = _extract_json(raw)
        except Exception as exc:
            plan = {"error": f"plan parsing failed: {exc}", "raw": raw}

    return {
        "concept": concept,
        "simulations": sims,
        "plan": plan,
    }


# ---------------------------------------------------------------------------
# Tri-council blueprint — used by the HUD Blueprint Workbench
# ---------------------------------------------------------------------------

# Specialized framing prompts. Each core is told WHICH lens to use so the
# three voices stay distinct instead of all producing generic analysis.
TRI_FRAMINGS = {
    "ajani": (
        "Reason about this concept through a STRUCTURAL / SYSTEM lens.\n"
        "Cover:\n"
        "  • core architecture (components, interfaces, data/energy flows)\n"
        "  • dependencies, prerequisites, bottlenecks\n"
        "  • failure points and how to harden them\n"
        "  • a concrete first-week action plan\n"
        "Be tactical. Avoid philosophy."
    ),
    "minerva": (
        "Reason about this concept through a HUMAN / ECOSYSTEM / EMOTIONAL "
        "lens.\nCover:\n"
        "  • who is affected, helped, displaced, or burdened\n"
        "  • ecological and cultural ripples\n"
        "  • the emotional weight of using or refusing this\n"
        "  • one short proverb that captures the principle at stake\n"
        "Stay grounded; do not moralize."
    ),
    "hermes": (
        "Reason about this concept through an ADAPTIVE / INVENTIVE lens.\n"
        "Cover:\n"
        "  • cross-domain analogies (patterns from biology, physics, "
        "economics, language, etc.)\n"
        "  • unconventional substitutes for the obvious components\n"
        "  • leverage points where a small change yields a big result\n"
        "  • two 'what if we inverted X' explorations\n"
        "Pattern hunting, not feasibility scoring."
    ),
}


SYNTHESIS_PROMPT = """You are the ATLAS Blueprint Synthesizer. Three sibling
cores have each given their take on a concept through a different lens:

  - AJANI:   STRUCTURAL / SYSTEM reasoning
  - MINERVA: HUMAN / ECOSYSTEM / EMOTIONAL reasoning
  - HERMES:  ADAPTIVE / INVENTIVE reasoning

Merge them into ONE coherent blueprint. Output ONLY a JSON object with this
exact shape:

{
  "concept": "<echoed>",
  "headline": "<one sentence summarizing the merged blueprint>",
  "structural_pillar": ["<3-6 bullets from Ajani's lens>"],
  "human_pillar":      ["<3-6 bullets from Minerva's lens>"],
  "inventive_pillar":  ["<3-6 bullets from Hermes's lens>"],
  "tensions": [
    "<a real disagreement or trade-off between two pillars, named>"
  ],
  "first_actions":  ["<3 concrete next steps, ordered by leverage>"],
  "open_questions": ["<3 questions that must be answered before committing>"]
}

Do NOT regenerate the lens content — distill it. Keep each bullet under
~140 characters. Never invent rules; respect what each sibling said.
"""


async def tri_council(concept: str) -> Dict:
    """Three lenses + synthesis.

    Returns:
        {
          "concept": <str>,
          "voices": {
            "ajani":   { "lens": "structural", "reasoning": <str> },
            "minerva": { "lens": "human",      "reasoning": <str> },
            "hermes":  { "lens": "inventive",  "reasoning": <str> },
          },
          "synthesis": <dict or {"error": ..., "raw": ...}>
        }
    """
    async def _voice(core_key: str) -> str:
        core = get_core(core_key)
        framing = TRI_FRAMINGS[core_key]
        return await core.think(
            f"CONCEPT:\n{concept}\n\nFRAMING:\n{framing}"
        )

    # Run the three voices in parallel.
    ajani_text, minerva_text, hermes_text = await asyncio.gather(
        _voice("ajani"), _voice("minerva"), _voice("hermes"),
        return_exceptions=True,
    )

    def _safe(v):
        if isinstance(v, Exception):
            return f"[voice failed: {v}]"
        return v

    voices = {
        "ajani":   {"lens": "structural",  "reasoning": _safe(ajani_text)},
        "minerva": {"lens": "human",       "reasoning": _safe(minerva_text)},
        "hermes":  {"lens": "inventive",   "reasoning": _safe(hermes_text)},
    }

    # Synthesis pass — Hermes plays the synthesizer.
    synthesizer = get_core("hermes")
    body = json.dumps({"concept": concept, "voices": voices}, indent=2)
    try:
        raw = await synthesizer.think(f"{SYNTHESIS_PROMPT}\n\nINPUT:\n{body}")
    except Exception as exc:
        raw = ""
        synthesis = {"error": f"synthesis call failed: {exc}", "raw": ""}
    else:
        try:
            synthesis = _extract_json(raw)
        except Exception as exc:
            synthesis = {"error": f"synthesis JSON parse failed: {exc}", "raw": raw}

    return {
        "concept": concept,
        "voices": voices,
        "synthesis": synthesis,
    }

