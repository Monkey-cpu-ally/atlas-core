"""
atlas_core/core/agent/governance.py

Content governance and policy enforcement.
"""

from dataclasses import dataclass


@dataclass
class GovernanceDecision:
    allowed: bool
    reason: str = ""
    severity: str = "low"


class Governance:
    """
    Safety + policy layer. Keep it simple now; expand later.
    """
    def evaluate(self, user_text: str) -> GovernanceDecision:
        lowered = user_text.lower()
        if "write a virus" in lowered or "steal passwords" in lowered:
            return GovernanceDecision(False, "Disallowed: harmful cybersecurity content.", "high")
        return GovernanceDecision(True)
