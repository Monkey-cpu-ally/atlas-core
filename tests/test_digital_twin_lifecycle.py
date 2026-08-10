from pathlib import Path

from atlas_core.luxury.digital_twin import LifecycleEvent, LifecycleEventType, ProductDigitalTwin
from atlas_core.luxury.digital_twin_store import DigitalTwinStore


def test_digital_twin_round_trip(tmp_path: Path):
    store = DigitalTwinStore(tmp_path / "luxury.db")
    twin = ProductDigitalTwin(
        product_id="hof-bag-001",
        product_name="Sapphire Knight Travel Bag",
        collection_id="sapphire-knight",
        serial_number="SK-0001",
        materials=["vegetable-tanned leather"],
        hardware=["Sapphire Knight clasp"],
        readiness_level=6,
    )
    twin.add_event(LifecycleEvent(LifecycleEventType.CREATED, "Created"))
    twin.record_repair("Reconditioned edge finish", provider="House of Frazier Atelier", cost=45)
    store.save(twin)

    restored = store.load("hof-bag-001")
    assert restored is not None
    assert restored.product_name == "Sapphire Knight Travel Bag"
    assert restored.readiness_level == 6
    assert restored.repair_count == 1
    assert restored.events[-1].metadata["cost"] == 45


def test_revision_must_move_forward():
    twin = ProductDigitalTwin("p-1", "Council Coat", design_revision=2)
    try:
        twin.record_revision(2, "same revision")
    except ValueError as exc:
        assert "move forward" in str(exc)
    else:
        raise AssertionError("Expected revision validation error")


def test_store_lists_twins(tmp_path: Path):
    store = DigitalTwinStore(tmp_path / "luxury.db")
    store.save(ProductDigitalTwin("p-1", "One"))
    store.save(ProductDigitalTwin("p-2", "Two"))
    assert [item.product_id for item in store.list_twins()] == ["p-1", "p-2"]
