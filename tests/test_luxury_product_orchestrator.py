from atlas_core.luxury.design_dna import DesignDNA
from atlas_core.luxury.digital_twin import ProductDigitalTwin
from atlas_core.luxury.digital_twin_store import DigitalTwinStore
from atlas_core.luxury.product_orchestrator import LuxuryProductOrchestrator
from atlas_core.luxury.readiness import ProductReadinessLevel


def make_dna(product_id: str, score: float) -> DesignDNA:
    values = {
        "heritage": score,
        "modernity": score,
        "elegance": score,
        "utility": score,
        "boldness": score,
        "innovation": score,
        "craftsmanship": score,
        "repairability": score,
        "exclusivity": score,
    }
    return DesignDNA(
        product_id=product_id,
        values=values,
        silhouette_tags=frozenset({"structured"}),
        material_tags=frozenset({"leather"}),
        pattern_family="Knight Grid",
        hardware_family="Sapphire Knight",
    )


def test_orchestrator_registers_and_assesses_product(tmp_path):
    store = DigitalTwinStore(tmp_path / "twins.db")
    orchestrator = LuxuryProductOrchestrator(store)
    twin = ProductDigitalTwin("bag-1", "Archive Bag")
    orchestrator.register_product(twin, make_dna("bag-1", 80))

    assessment = orchestrator.assess("bag-1", make_dna("house", 80))
    assert assessment.identity_status == "too_repetitive"
    assert assessment.readiness_level == ProductReadinessLevel.IDEA
    assert assessment.lifecycle_event_count >= 1


def test_orchestrator_tracks_revisions_and_delta(tmp_path):
    store = DigitalTwinStore(tmp_path / "twins.db")
    orchestrator = LuxuryProductOrchestrator(store)
    orchestrator.register_product(ProductDigitalTwin("coat-1", "Council Coat"), make_dna("coat-1", 75))

    assert orchestrator.add_revision("coat-1", "initial", ("base",), 70, 800, 80) is None
    delta = orchestrator.add_revision("coat-1", "improved", ("hardware",), 84, 830, 90)
    assert delta is not None
    assert delta.genome_delta == 14
    assert delta.cost_delta == 30
    assert delta.prototype_delta == 10
    assert delta.improved

    restored = store.load("coat-1")
    assert restored is not None
    assert restored.design_revision == 2
    assert len(restored.events) >= 3


def test_orchestrator_promotes_readiness_with_evidence(tmp_path):
    store = DigitalTwinStore(tmp_path / "twins.db")
    orchestrator = LuxuryProductOrchestrator(store)
    orchestrator.register_product(ProductDigitalTwin("boot-1", "Field Boot"), make_dna("boot-1", 70))

    level = orchestrator.add_readiness_evidence(
        "boot-1",
        "research",
        "concept",
        "engineering_review",
        "prototype",
        "prototype_tests",
        "council_approval",
        "manufacturing_plan",
    )
    assert level == ProductReadinessLevel.MANUFACTURING_READY
    restored = store.load("boot-1")
    assert restored is not None
    assert restored.readiness_level == ProductReadinessLevel.MANUFACTURING_READY
