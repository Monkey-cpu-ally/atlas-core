from __future__ import annotations

from typing import Iterable, Mapping

from .council import CouncilReviewEngine
from .critique import LuxuryCritiqueEngine, OriginalityEngine
from .genome import DesignGenomeEngine
from .models import AIReview, DesignConcept, ForgeRecord, ForgeStage, ReviewVerdict


class DesignForge:
    """Coordinates scoring, critique, originality checks, and Council review."""

    def __init__(
        self,
        genome_engine: DesignGenomeEngine | None = None,
        critique_engine: LuxuryCritiqueEngine | None = None,
        originality_engine: OriginalityEngine | None = None,
        council_engine: CouncilReviewEngine | None = None,
    ) -> None:
        self.genome_engine = genome_engine or DesignGenomeEngine()
        self.critique_engine = critique_engine or LuxuryCritiqueEngine()
        self.originality_engine = originality_engine or OriginalityEngine()
        self.council_engine = council_engine or CouncilReviewEngine()

    def begin(self, concept: DesignConcept) -> ForgeRecord:
        record = ForgeRecord(concept=concept)
        record.history.append("idea: concept entered the Design Forge")
        return record

    def evaluate(
        self,
        record: ForgeRecord,
        evidence_scores: Mapping[str, float],
        reasons: Mapping[str, str] | None = None,
    ) -> ForgeRecord:
        record.advance(ForgeStage.CRITIQUE, "design genome and critique started")
        record.genome = self.genome_engine.score(record.concept, evidence_scores, reasons)
        record.critiques = self.critique_engine.critique(record.concept, record.genome)
        record.critiques.extend(self.originality_engine.inspect(record.concept))
        record.history.append(
            f"critique: {len(record.critiques)} finding(s), genome {record.genome.overall:.2f}/100"
        )
        return record

    def submit_to_council(self, record: ForgeRecord, reviews: Iterable[AIReview]) -> ForgeRecord:
        if record.genome is None:
            raise RuntimeError("Evaluate the design before Council submission")
        record.advance(ForgeStage.COUNCIL, "submitted to Hermes, Minerva, and Ajani")
        record.council_decision = self.council_engine.decide(record.concept, reviews)
        if record.council_decision.verdict == ReviewVerdict.APPROVE:
            record.advance(ForgeStage.ARCHIVE, "approved design archived as an official version")
        else:
            record.history.append(
                f"council: returned for {record.council_decision.verdict.value}"
            )
        return record
