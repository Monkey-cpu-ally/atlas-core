"""End-to-end quality orchestration for ATLAS Creative Intelligence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Tuple, TypeVar

from .critic_council import CouncilDecision
from .reference_library.loader import CreativeReference, CreativeReferenceLibrary
from .reference_provenance import OriginalityAssessment
from .revision_loop import CreativeRevisionLoop, RevisionResult

T = TypeVar("T")


@dataclass(frozen=True)
class CreativeQualityResult(Generic[T]):
    approved: bool
    references: Tuple[CreativeReference, ...]
    originality: OriginalityAssessment
    revision: RevisionResult[T] | None
    blockers: Tuple[str, ...]


class CreativeQualityPipeline(Generic[T]):
    """Reference-aware, originality-gated, critique/revision quality pipeline."""

    def __init__(self, library: CreativeReferenceLibrary | None = None, max_revisions: int = 3):
        self.library = library or CreativeReferenceLibrary.load_default()
        self.max_revisions = max_revisions

    def run(self, *, artifact: T, reference_queries: Tuple[str, ...],
            originality: OriginalityAssessment,
            evaluate: Callable[[T], CouncilDecision],
            revise: Callable[[T, Tuple[str, ...]], T]) -> CreativeQualityResult[T]:
        references = self._resolve_references(reference_queries)
        blockers = []
        if not references:
            blockers.append("no_reference_context")
        if not originality.passes:
            blockers.extend(f"originality:{item}" for item in originality.violations)
        if blockers:
            return CreativeQualityResult(False, references, originality, None, tuple(blockers))

        revision = CreativeRevisionLoop[T](self.max_revisions).run(
            artifact=artifact, evaluate=evaluate, revise=revise
        )
        if not revision.approved:
            blockers.append(f"critique:{revision.stop_reason}")
        return CreativeQualityResult(
            revision.approved and not blockers,
            references,
            originality,
            revision,
            tuple(blockers),
        )

    def _resolve_references(self, queries: Tuple[str, ...]) -> Tuple[CreativeReference, ...]:
        found = []
        seen = set()
        for query in queries:
            for ref in self.library.search(query):
                if ref.reference_id not in seen:
                    found.append(ref)
                    seen.add(ref.reference_id)
        return tuple(found)
