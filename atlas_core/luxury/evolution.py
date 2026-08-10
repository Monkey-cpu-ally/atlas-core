from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True, frozen=True)
class DesignRevision:
    revision: int
    summary: str
    changes: tuple[str, ...]
    genome_score: float
    estimated_cost: float
    prototype_pass_rate: float | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True, frozen=True)
class RevisionDelta:
    genome_delta: float
    cost_delta: float
    prototype_delta: float | None
    improved: bool


class DesignEvolutionEngine:
    def __init__(self) -> None:
        self._history: dict[str, list[DesignRevision]] = {}

    def add_revision(self, product_id: str, revision: DesignRevision) -> None:
        history = self._history.setdefault(product_id, [])
        expected = len(history) + 1
        if revision.revision != expected:
            raise ValueError(f"Expected revision {expected}, received {revision.revision}")
        history.append(revision)

    def history(self, product_id: str) -> tuple[DesignRevision, ...]:
        return tuple(self._history.get(product_id, ()))

    def compare_latest(self, product_id: str) -> RevisionDelta | None:
        history = self._history.get(product_id, [])
        if len(history) < 2:
            return None
        previous, current = history[-2], history[-1]
        prototype_delta = None
        if previous.prototype_pass_rate is not None and current.prototype_pass_rate is not None:
            prototype_delta = round(current.prototype_pass_rate - previous.prototype_pass_rate, 2)
        genome_delta = round(current.genome_score - previous.genome_score, 2)
        cost_delta = round(current.estimated_cost - previous.estimated_cost, 2)
        improved = genome_delta > 0 and (prototype_delta is None or prototype_delta >= 0)
        return RevisionDelta(genome_delta, cost_delta, prototype_delta, improved)
