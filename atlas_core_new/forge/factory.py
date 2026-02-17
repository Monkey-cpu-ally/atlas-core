"""
atlas_core/forge/factory.py

Cauldron-Lite Factory and Federated Orchestrator.
"""

import time
from dataclasses import dataclass
from typing import List, Tuple
from .core import Decision, TaskType
from .safety import SafetyKernel
from .authority import RefusalEngine
from .blueprints import Blueprint


@dataclass
class CauldronLiteFactory:
    """
    This factory is intentionally limited:
    - Only builds from approved blueprints
    - Only uses safe materials set
    - Refuses forbidden geometries automatically
    - No autonomous deployment (must be instructed)
    """
    safety: SafetyKernel
    refusal: RefusalEngine
    safe_materials: Tuple[str, ...] = (
        "biopolymer", "recycled_aluminum", "bamboo_composite", "silicone", "rubber",
    )

    def build(self, bp: Blueprint, uncertainty: float = 0.2) -> str:
        report = self.refusal.evaluate(bp, uncertainty)
        decision = report["overall_decision"]
        violations = report["violations"]
        reviews = report["reviews"]

        if decision != Decision.APPROVE:
            reasons = []
            for v in violations:  # type: ignore
                reasons.append(f"[{v.severity.name}] {v.message}")
            for rv in reviews:  # type: ignore
                if rv.decision != Decision.APPROVE:
                    reasons.append(f"{rv.reviewer}: {rv.decision.name} — {', '.join(rv.reasons)}")
            return "REFUSED BUILD:\n- " + "\n- ".join(reasons)

        time.sleep(0.01)
        return f"BUILT OK: {bp.name} (biomimic={bp.biomimic}, task={bp.task_type.name})"


@dataclass
class FederatedOrchestrator:
    """
    Not a god-AI:
    - Only orchestrates proposals
    - Cannot directly fabricate or deploy
    - Must go through RefusalEngine + Factory
    """
    name: str = "GAIA-Lite Orchestrator"
    max_batch: int = 3

    def propose_batch(self, needs: List[TaskType]) -> List[TaskType]:
        return needs[:self.max_batch]
