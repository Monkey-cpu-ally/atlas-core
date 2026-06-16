"""Council router — decides which core leads, which supports, which critiques.

The Council never *speaks* directly to the user. It only orchestrates roles
across the three cores, then assembles their outputs into a single response.

Routing heuristic (fast, deterministic, no LLM call needed):

  • If the question is about ethics / culture / people / story / art
        → Minerva leads, Hermes critiques, Ajani supports with action.
  • If the question is about math / physics / code / proof / edge-cases
        → Hermes leads, Ajani supports with strategy, Minerva watches ethics.
  • Otherwise (default: action / build / strategy)
        → Ajani leads, Hermes critiques math, Minerva watches ethics.

The heuristic can be replaced by an LLM classifier later without changing
callers — `route()` returns a `CouncilDecision` regardless.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..cores import CORES, get_core


# Lightweight keyword lexicons. Deliberately overlapping — score-based.
ETHICS_LEX = {
    "ethic", "ethical", "right", "wrong", "harm", "consent", "culture",
    "history", "story", "people", "ancestor", "elder", "community",
    "dignity", "respect", "tradition", "myth", "art", "psychology",
    "emotion", "feeling", "should", "ought",
}

TECHNICAL_LEX = {
    "prove", "proof", "equation", "math", "code", "algorithm",
    "complexity", "physics", "quantum", "chemistry", "molecule",
    "compile", "stack", "performance", "edge case", "edge-case",
    "rigorous", "theorem", "formula", "calculate",
}


@dataclass
class CouncilDecision:
    lead: str
    support: str
    critic: str
    rationale: str
    scores: Dict[str, int]


def _score(text: str, lex) -> int:
    text = text.lower()
    return sum(1 for w in lex if w in text)


def route_internal(question: str) -> CouncilDecision:
    """Pick lead / support / critic for one question.

    Renamed from `route` in Phase 0 cleanup to disambiguate from the
    public `/api/council/route` endpoint defined in routes/council.py.
    External callers use the lighter keyword-based router in
    routing.topic_router; this function adds support/critic assignment
    and a textual rationale, used by atlas_core's blueprint engine.
    """
    ethics = _score(question, ETHICS_LEX)
    techni = _score(question, TECHNICAL_LEX)

    if ethics > techni and ethics > 0:
        decision = CouncilDecision(
            lead="minerva",
            support="ajani",
            critic="hermes",
            rationale="Ethics / culture / human-system question — Minerva leads.",
            scores={"ethics": ethics, "technical": techni},
        )
    elif techni > ethics and techni > 0:
        decision = CouncilDecision(
            lead="hermes",
            support="ajani",
            critic="minerva",
            rationale="Technical / mathematical / proof question — Hermes leads.",
            scores={"ethics": ethics, "technical": techni},
        )
    else:
        decision = CouncilDecision(
            lead="ajani",
            support="hermes",
            critic="minerva",
            rationale="Default: action / strategy / build — Ajani leads.",
            scores={"ethics": ethics, "technical": techni},
        )
    return decision


async def assemble(
    question: str,
    *,
    context: Optional[str] = None,
    include_critique: bool = True,
) -> Dict:
    """Run the full Council process and return a structured response.

    Sequence:
      1) Decide roles via `route()`.
      2) Lead drafts the main answer.
      3) Critic (optionally) lists open concerns.
      4) Support adds one short action step.
    """
    decision = route(question)
    lead_core = get_core(decision.lead)
    critic_core = get_core(decision.critic)
    support_core = get_core(decision.support)

    lead_answer = await lead_core.think(question, context=context)

    critique = None
    if include_critique:
        critic_prompt = (
            f"A sibling ({lead_core.identity.name}) just answered the user's "
            f"question:\n\n---\n{lead_answer}\n---\n\n"
            f"Your job: in 2-3 short bullets, list what they MISSED or any "
            f"risk inside their own field. Do not rewrite the answer."
        )
        critique = await critic_core.think(critic_prompt)

    support_prompt = (
        f"The lead answer was:\n\n---\n{lead_answer}\n---\n\n"
        "Give exactly one concrete next-step action. One line, no preamble."
    )
    support_action = await support_core.think(support_prompt)

    return {
        "decision": {
            "lead": decision.lead,
            "support": decision.support,
            "critic": decision.critic,
            "rationale": decision.rationale,
            "scores": decision.scores,
        },
        "lead_answer": lead_answer,
        "critique": critique,
        "next_step": support_action,
    }
