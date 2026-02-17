"""Hermes-style policy evaluation and hard-rule enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PolicyDecision:
    blocked: bool = False
    flagged: bool = False
    safety_mode: str = "normal"
    checks: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    enforced_constraints: list[str] = field(default_factory=list)


class PolicyEngine:
    _blocked_terms = (
        "weapon",
        "bomb",
        "kill",
        "harm someone",
        "illegal",
        "bypass law",
        "malware",
        "exploit vulnerability",
    )
    _bio_terms = (
        "gene edit",
        "pathogen",
        "virus",
        "bioweapon",
        "wet lab",
        "dna synthesis",
        "crispr",
    )

    def evaluate(self, user_input: str) -> PolicyDecision:
        decision = PolicyDecision()
        lowered = user_input.lower()

        decision.checks.append("Checked harmful/illegal intent.")
        if any(term in lowered for term in self._blocked_terms):
            decision.blocked = True
            decision.safety_mode = "blocked"
            decision.flags.append("harmful_or_illegal_request")
            decision.blocked_reasons.append(
                "Request appears harmful, illegal, or weaponization-related."
            )
            decision.enforced_constraints.append("Hard block applied by Hermes policy gate.")
            return decision

        decision.checks.append("Checked bio-safety boundaries.")
        if any(term in lowered for term in self._bio_terms):
            decision.flagged = True
            decision.safety_mode = "simulation_only"
            decision.flags.append("bio_request_simulation_only")
            decision.enforced_constraints.append(
                "Bio topics are limited to simulation-only and safe research mode."
            )

        decision.checks.append("Checked weaponization restrictions.")
        decision.enforced_constraints.append("No weaponization instructions.")
        decision.enforced_constraints.append("Outputs must include measurable requirements.")
        decision.enforced_constraints.append("Outputs must include testable steps.")
        return decision

