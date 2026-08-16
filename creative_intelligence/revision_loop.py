"""Revision/re-evaluation state machine for ATLAS Creative Intelligence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Tuple, TypeVar

from .critic_council import CouncilDecision

T = TypeVar("T")


@dataclass(frozen=True)
class RevisionCycle(Generic[T]):
    iteration: int
    artifact: T
    decision: CouncilDecision


@dataclass(frozen=True)
class RevisionResult(Generic[T]):
    approved: bool
    final_artifact: T
    cycles: Tuple[RevisionCycle[T], ...]
    stop_reason: str


class CreativeRevisionLoop(Generic[T]):
    """Revises only from explicit criticism, re-evaluates, and stops safely."""

    def __init__(self, max_revisions: int = 3):
        if max_revisions < 0:
            raise ValueError("max_revisions must be >= 0")
        self.max_revisions = max_revisions

    def run(self, *, artifact: T, evaluate: Callable[[T], CouncilDecision],
            revise: Callable[[T, Tuple[str, ...]], T]) -> RevisionResult[T]:
        current = artifact
        cycles = []

        for iteration in range(self.max_revisions + 1):
            decision = evaluate(current)
            cycles.append(RevisionCycle(iteration, current, decision))
            if decision.approved:
                return RevisionResult(True, current, tuple(cycles), "approved")
            if iteration >= self.max_revisions:
                return RevisionResult(False, current, tuple(cycles), "revision_limit")
            if not decision.revision_plan:
                return RevisionResult(False, current, tuple(cycles), "no_actionable_revision_plan")

            revised = revise(current, decision.revision_plan)
            if revised == current:
                return RevisionResult(False, current, tuple(cycles), "revision_made_no_change")
            current = revised

        raise RuntimeError("unreachable revision loop state")
