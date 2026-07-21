import pytest

from atlas_core.luxury.certification import FailureArchive, FailureRecord, MasterpieceCertificationEngine
from atlas_core.luxury.collections import CollectionProduct, DesignCollection
from atlas_core.luxury.prototypes import PrototypeLaboratory, PrototypeRecord, PrototypeTest
from atlas_core.luxury.suppliers import Supplier, SupplierRegistry, SupplierStatus


def test_supplier_requires_threshold_for_approval():
    registry = SupplierRegistry()
    supplier = Supplier("s1", "Example Tannery", "leather", "US", quality_score=90, reliability_score=80, sustainability_score=70)
    registry.add(supplier)
    approved = registry.approve("s1")
    assert approved.status is SupplierStatus.APPROVED
    assert approved.weighted_score == 82.5


def test_low_supplier_score_is_rejected():
    registry = SupplierRegistry()
    registry.add(Supplier("s1", "Weak Supplier", "hardware", "US", quality_score=40, reliability_score=40, sustainability_score=40))
    with pytest.raises(ValueError):
        registry.approve("s1")


def test_prototype_requires_all_tests_to_pass():
    laboratory = PrototypeLaboratory()
    record = PrototypeRecord("p1", "d1", 1)
    laboratory.register(record)
    laboratory.add_test("p1", PrototypeTest("strap load", 120, 100))
    laboratory.add_test("p1", PrototypeTest("water ingress", 2, 3, higher_is_better=False))
    assert record.passed is True
    assert record.pass_rate == 100.0
    assert laboratory.latest_passed("d1") == record


def test_collection_cohesion_and_readiness():
    collection = DesignCollection("c1", "Garden Between Worlds", "living architecture", "Nature reclaiming monuments", {"teal", "ivory"}, {"leather", "brass"})
    collection.add_product(CollectionProduct("d1", "hero", {"teal"}, {"leather"}, "thorn", {"garden"}))
    collection.add_product(CollectionProduct("d2", "supporting", {"ivory"}, {"brass"}, "thorn", {"garden"}))
    collection.add_product(CollectionProduct("d3", "supporting", {"teal"}, {"leather"}, "thorn", {"garden"}))
    assert collection.cohesion_score() == 100.0
    assert collection.readiness_issues() == []


def test_masterpiece_certification_fails_single_gate():
    engine = MasterpieceCertificationEngine()
    scores = {key: 100.0 for key in engine.thresholds}
    scores["repairability"] = 70.0
    result = engine.evaluate("d1", scores)
    assert result.certified is False
    assert result.failed_gates == ["repairability"]


def test_failure_archive_searches_lessons():
    archive = FailureArchive()
    archive.add(FailureRecord("d1", 1, "Strap attachment failed under load", "Hermes", ["engineering"], ["silhouette"]))
    assert len(archive.search("strap")) == 1
    assert len(archive.for_design("d1")) == 1
