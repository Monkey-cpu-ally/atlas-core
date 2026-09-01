"""Evidence-bound ideation helpers for ATLAS Discovery Intelligence.

These functions structure cross-disciplinary analogies and candidate hypotheses.
They do not claim an analogy is valid, an idea is novel, or a hypothesis is true.
"""
from __future__ import annotations
from typing import Any, Dict, List
from uuid import uuid4


class DiscoveryIdeationError(RuntimeError):
    pass


def build_analogy(*, source_subject: str, target_subject: str, source_mechanism: str, target_problem: str, shared_principle: str, assumptions: List[str], failure_modes: List[str]) -> Dict[str, Any]:
    required = [source_subject, target_subject, source_mechanism, target_problem, shared_principle]
    if any(not value.strip() for value in required):
        raise DiscoveryIdeationError("analogy requires source, target, mechanism, problem, and shared principle")
    if source_subject.casefold() == target_subject.casefold():
        raise DiscoveryIdeationError("cross-disciplinary analogy requires different source and target subjects")
    if not failure_modes:
        raise DiscoveryIdeationError("analogy requires at least one failure mode")
    return {
        "analogy_id": f"ANA-{str(uuid4())[:8]}", "source_subject": source_subject.strip(),
        "target_subject": target_subject.strip(), "source_mechanism": source_mechanism.strip(),
        "target_problem": target_problem.strip(), "shared_principle": shared_principle.strip(),
        "assumptions": assumptions, "failure_modes": failure_modes, "status": "UNVALIDATED_ANALOGY",
        "claim_rule": "Analogy suggests a test direction; it is not evidence that the mechanism transfers.",
    }


def hypothesis_from_analogy(*, analogy: Dict[str, Any], measurable_effect: str, comparison: str, falsification_criteria: List[str]) -> Dict[str, Any]:
    if analogy.get("status") != "UNVALIDATED_ANALOGY":
        raise DiscoveryIdeationError("hypothesis generation requires an unvalidated analogy record")
    if not measurable_effect.strip() or not comparison.strip() or not falsification_criteria:
        raise DiscoveryIdeationError("candidate hypothesis requires a measurable effect, comparison, and falsification criteria")
    statement = f"Applying {analogy['shared_principle']} to {analogy['target_problem']} will {measurable_effect.strip()} compared with {comparison.strip()}."
    return {
        "candidate_id": f"HC-{str(uuid4())[:8]}", "statement": statement,
        "rationale": f"Cross-disciplinary lead from {analogy['source_subject']} to {analogy['target_subject']}: {analogy['source_mechanism']}",
        "falsification_criteria": falsification_criteria, "assumptions": analogy.get("assumptions", []),
        "source_analogy_id": analogy["analogy_id"], "status": "CANDIDATE_ONLY",
        "required_next_steps": ["prior_art_search", "evidence_review", "experiment_design"],
        "claim_rule": "Candidate hypotheses are not discoveries until tested and independently reviewed.",
    }
