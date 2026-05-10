"""Blueprint engine — each core mentally simulates before answering.

Given a high-level concept, the engine runs each of the three cores through
their private `mental_simulate()` pass IN PARALLEL, then assembles a single
blueprint that lists each core's:

  • assumptions
  • unknowns
  • failure modes
  • who they think should consult next

The final response also includes a synthesized 5-phase plan when
`with_plan=True`. The 5-phase plan is what the Atlas Blueprint Workbench in
the HUD calls (Philosophy → Research → Blueprint → Simulation → Physical).
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
        # We override the system prompt for this single call by passing the
        # whole instruction inside the user message. Cleaner than mutating
        # the synth core's identity.
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
