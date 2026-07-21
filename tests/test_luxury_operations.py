from pathlib import Path

import pytest

from atlas_core.luxury.engineering import (
    ApparelEngineeringCalculator,
    BagEngineeringCalculator,
    FootwearEngineeringCalculator,
    FurnitureEngineeringCalculator,
)
from atlas_core.luxury.evaluation_store import EvaluationStore
from atlas_core.luxury.manufacturing import CostLine, ManufacturingCostEngine, ManufacturingInputs
from atlas_core.luxury.models import (
    AIReview,
    CouncilDecision,
    CritiqueFinding,
    DesignConcept,
    DesignGenome,
    ForgeRecord,
    ForgeStage,
    GenomeScore,
    ReviewVerdict,
)
from atlas_core.luxury.workflow import ForgeStateMachine, ForgeTransitionError


def test_workflow_rejects_skipped_stage():
    record = ForgeRecord(DesignConcept("d-1", "Bag", "bag", "Travel bag"))
    with pytest.raises(ForgeTransitionError):
        ForgeStateMachine().transition(record, ForgeStage.STORY, {"story_complete": True})


def test_workflow_accepts_next_stage_with_evidence():
    record = ForgeRecord(DesignConcept("d-2", "Boot", "footwear", "Field boot"))
    ForgeStateMachine().transition(
        record,
        ForgeStage.RESEARCH,
        {"research_complete": True},
    )
    assert record.stage is ForgeStage.RESEARCH


def test_manufacturing_estimate_is_transparent():
    result = ManufacturingCostEngine().estimate(
        ManufacturingInputs(
            materials=[CostLine("Leather", 40, 2)],
            hardware=[CostLine("Buckle", 8, 2)],
            labor_hours=3,
            labor_rate=30,
            packaging_cost=12,
        )
    )
    assert result.direct_materials == 80
    assert result.unit_cost > 198
    assert result.suggested_retail > result.wholesale_price > result.unit_cost


def test_product_calculators():
    bag = BagEngineeringCalculator().analyze(40, 30, 15, 8)
    assert bag.volume_liters == 18
    assert bag.recommended_safety_load_newtons > bag.strap_force_newtons

    footwear = FootwearEngineeringCalculator().analyze(270, 12, 30, 20, 450)
    assert footwear.internal_length_mm == 282
    assert footwear.estimated_pair_mass_g == 900

    furniture = FurnitureEngineeringCalculator().analyze(120, 2, 4, 600, 600, 800)
    assert furniture.design_load_kg == 240

    apparel = ApparelEngineeringCalculator().analyze(100, 8, 1.5, 2, 70, 150)
    assert apparel.finished_measurement_cm == 108
    assert apparel.estimated_fabric_m > 0


def test_evaluation_store_round_trip(tmp_path: Path):
    store = EvaluationStore(tmp_path / "luxury.db")
    genome = DesignGenome("d-3", [GenomeScore("originality", 88, "Distinct")])
    critiques = [CritiqueFinding("repairability", "medium", "Weak plan", "Add replaceable hardware")]
    store.save_evaluation(genome, critiques)
    loaded = store.load_evaluation("d-3")
    assert loaded is not None
    assert loaded[0].overall == 88
    assert loaded[1][0].recommendation == "Add replaceable hardware"

    decision = CouncilDecision(
        design_id="d-3",
        verdict=ReviewVerdict.APPROVE,
        overall_score=90,
        reviews=[AIReview("Hermes", ReviewVerdict.APPROVE, 90)],
        summary="Approved",
    )
    store.save_council_decision(decision)
    restored = store.load_council_decision("d-3")
    assert restored is not None
    assert restored.verdict is ReviewVerdict.APPROVE
