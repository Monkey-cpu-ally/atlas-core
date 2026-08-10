from __future__ import annotations

from dataclasses import dataclass

from .design_dna import DNAComparison, DesignDNA, DesignDNAEngine
from .digital_twin import LifecycleEvent, LifecycleEventType, ProductDigitalTwin
from .digital_twin_store import DigitalTwinStore
from .evolution import DesignEvolutionEngine, DesignRevision, RevisionDelta
from .readiness import ProductReadiness, ProductReadinessLevel


@dataclass(slots=True, frozen=True)
class ProductAssessment:
    product_id: str
    identity_status: str
    identity_similarity: float
    readiness_level: int
    latest_revision: int
    revision_delta: RevisionDelta | None
    lifecycle_event_count: int


class LuxuryProductOrchestrator:
    """Coordinates identity, readiness, evolution, and lifecycle state for one product."""

    def __init__(self, store: DigitalTwinStore) -> None:
        self.store = store
        self.dna_engine = DesignDNAEngine()
        self.evolution = DesignEvolutionEngine()
        self.readiness: dict[str, ProductReadiness] = {}
        self.dna_profiles: dict[str, DesignDNA] = {}

    def register_product(
        self,
        twin: ProductDigitalTwin,
        dna: DesignDNA,
        evidence: set[str] | None = None,
    ) -> None:
        if twin.product_id != dna.product_id:
            raise ValueError("Digital twin and DNA product ids must match")
        self.store.save(twin)
        self.dna_profiles[twin.product_id] = dna
        readiness = ProductReadiness(twin.product_id)
        readiness.add_evidence(*(evidence or {"idea"}))
        self.readiness[twin.product_id] = readiness
        twin.readiness_level = int(readiness.level)
        twin.add_event(
            LifecycleEvent(
                LifecycleEventType.CREATED,
                "Product registered with orchestration service",
                {"readiness_level": int(readiness.level)},
            )
        )
        self.store.save(twin)

    def add_revision(
        self,
        product_id: str,
        summary: str,
        changes: tuple[str, ...],
        genome_score: float,
        estimated_cost: float,
        prototype_pass_rate: float | None = None,
    ) -> RevisionDelta | None:
        twin = self._require_twin(product_id)
        revision_number = len(self.evolution.history(product_id)) + 1
        revision = DesignRevision(
            revision=revision_number,
            summary=summary,
            changes=changes,
            genome_score=genome_score,
            estimated_cost=estimated_cost,
            prototype_pass_rate=prototype_pass_rate,
        )
        self.evolution.add_revision(product_id, revision)
        if revision_number > twin.design_revision:
            twin.record_revision(revision_number, summary)
        else:
            twin.add_event(
                LifecycleEvent(
                    LifecycleEventType.REVISION,
                    summary,
                    {"revision": revision_number, "changes": list(changes)},
                )
            )
        self.store.save(twin)
        return self.evolution.compare_latest(product_id)

    def add_readiness_evidence(self, product_id: str, *evidence: str) -> ProductReadinessLevel:
        twin = self._require_twin(product_id)
        readiness = self.readiness.setdefault(product_id, ProductReadiness(product_id))
        readiness.add_evidence(*evidence)
        old_level = twin.readiness_level
        twin.readiness_level = int(readiness.level)
        if twin.readiness_level != old_level:
            twin.add_event(
                LifecycleEvent(
                    LifecycleEventType.QUALITY,
                    "Product readiness level updated",
                    {"from": old_level, "to": twin.readiness_level},
                )
            )
        self.store.save(twin)
        return readiness.level

    def update_dna(self, dna: DesignDNA) -> None:
        self._require_twin(dna.product_id)
        self.dna_profiles[dna.product_id] = dna

    def assess(self, product_id: str, house_reference: DesignDNA) -> ProductAssessment:
        twin = self._require_twin(product_id)
        dna = self.dna_profiles.get(product_id)
        if dna is None:
            raise ValueError(f"No Design DNA registered for {product_id}")
        comparison: DNAComparison = self.dna_engine.compare(dna, house_reference)
        readiness = self.readiness.setdefault(product_id, ProductReadiness(product_id))
        return ProductAssessment(
            product_id=product_id,
            identity_status=self.dna_engine.identity_status(dna, house_reference),
            identity_similarity=comparison.similarity,
            readiness_level=int(readiness.level),
            latest_revision=twin.design_revision,
            revision_delta=self.evolution.compare_latest(product_id),
            lifecycle_event_count=len(twin.events),
        )

    def _require_twin(self, product_id: str) -> ProductDigitalTwin:
        twin = self.store.load(product_id)
        if twin is None:
            raise KeyError(f"Unknown digital twin: {product_id}")
        return twin
