from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CouncilVerdict(str, Enum):
    APPROVE = "approve"
    REVISE = "revise"
    REJECT = "reject"


@dataclass(slots=True, frozen=True)
class CouncilVote:
    agent: str
    score: float
    verdict: CouncilVerdict
    rationale: str = ""


@dataclass(slots=True, frozen=True)
class WeightedDecision:
    domain: str
    score: float
    verdict: CouncilVerdict
    weights: dict[str, float]


DEFAULT_WEIGHTS: dict[str, dict[str, float]] = {
    "engineering": {"Hermes": 0.60, "Minerva": 0.20, "Ajani": 0.20},
    "design": {"Hermes": 0.20, "Minerva": 0.60, "Ajani": 0.20},
    "business": {"Hermes": 0.20, "Minerva": 0.20, "Ajani": 0.60},
    "balanced": {"Hermes": 1 / 3, "Minerva": 1 / 3, "Ajani": 1 / 3},
}


class WeightedCouncil:
    def decide(self, domain: str, votes: list[CouncilVote]) -> WeightedDecision:
        if not votes:
            raise ValueError("At least one vote is required")
        weights = DEFAULT_WEIGHTS.get(domain.lower(), DEFAULT_WEIGHTS["balanced"])
        vote_map = {vote.agent: vote for vote in votes}
        present_weight = sum(weights.get(agent, 0.0) for agent in vote_map)
        if present_weight <= 0:
            raise ValueError("No recognized Council agents supplied")
        score = sum(vote_map[agent].score * weights.get(agent, 0.0) for agent in vote_map) / present_weight
        score = round(score, 2)
        veto = any(vote.verdict is CouncilVerdict.REJECT and weights.get(vote.agent, 0.0) >= 0.5 for vote in votes)
        if veto or score < 60:
            verdict = CouncilVerdict.REJECT
        elif score < 80 or any(vote.verdict is CouncilVerdict.REVISE for vote in votes):
            verdict = CouncilVerdict.REVISE
        else:
            verdict = CouncilVerdict.APPROVE
        return WeightedDecision(domain, score, verdict, dict(weights))
