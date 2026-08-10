import pytest

from atlas_core.luxury.design_dna import DesignDNA, DesignDNAEngine
from atlas_core.luxury.evolution import DesignEvolutionEngine, DesignRevision
from atlas_core.luxury.readiness import ProductReadiness, ProductReadinessLevel


def dna(product_id: str, value: float) -> DesignDNA:
    return DesignDNA(
        product_id=product_id,
        values={
            "heritage": value,
            "modernity": value,
            "elegance": value,
            "utility": value,
            "boldness": value,
            "innovation": value,
            "craftsmanship": value,
            "repairability": value,
            "exclusivity": value,
        },
        silhouette_tags=frozenset({"structured", "architectural"}),
        material_tags=frozenset({"leather", "metal"}),
        pattern_family="Knight Grid",
        hardware_family="Sapphire Knight",
    )


def test_dna_detects_excessive_repetition():
    engine = DesignDNAEngine()
    assert engine.identity_status(dna("a", 80), dna("b", 80)) == "too_repetitive"


def test_dna_rejects_invalid_scores():
    with pytest.raises(ValueError):
        dna("bad", 101)


def test_readiness_requires_evidence_for_manufacturing():
    readiness = ProductReadiness("bag-1")
    readiness.add_evidence("idea", "research", "concept", "engineering_review", "prototype", "prototype_tests")
    assert readiness.level == ProductReadinessLevel.TESTED
    assert not readiness.can_enter_production()
    assert "council_approval" in readiness.missing_for(ProductReadinessLevel.MANUFACTURING_READY)


def test_evolution_compares_latest_versions():
    engine = DesignEvolutionEngine()
    engine.add_revision("bag-1", DesignRevision(1, "first", ("initial",), 72, 500, 80))
    engine.add_revision("bag-1", DesignRevision(2, "stronger", ("hardware",), 84, 525, 92))
    delta = engine.compare_latest("bag-1")
    assert delta is not None
    assert delta.genome_delta == 12
    assert delta.cost_delta == 25
    assert delta.prototype_delta == 12
    assert delta.improved
