from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(frozen=True)
class CostLine:
    name: str
    unit_cost: float
    quantity: float = 1.0

    @property
    def total(self) -> float:
        if self.unit_cost < 0 or self.quantity < 0:
            raise ValueError("Costs and quantities must be non-negative")
        return round(self.unit_cost * self.quantity, 2)


@dataclass(frozen=True)
class ManufacturingInputs:
    materials: List[CostLine] = field(default_factory=list)
    hardware: List[CostLine] = field(default_factory=list)
    labor_hours: float = 0.0
    labor_rate: float = 0.0
    packaging_cost: float = 0.0
    overhead_rate: float = 0.15
    waste_rate: float = 0.08
    repair_reserve_rate: float = 0.03
    wholesale_margin: float = 0.45
    retail_margin: float = 0.65


@dataclass(frozen=True)
class ManufacturingEstimate:
    direct_materials: float
    direct_hardware: float
    labor: float
    waste: float
    packaging: float
    overhead: float
    repair_reserve: float
    unit_cost: float
    wholesale_price: float
    suggested_retail: float


class ManufacturingCostEngine:
    """Produces transparent prototype and production pricing estimates."""

    @staticmethod
    def _validate_rate(name: str, value: float) -> None:
        if not 0.0 <= value < 1.0:
            raise ValueError(f"{name} must be between 0.0 and 1.0")

    def estimate(self, inputs: ManufacturingInputs) -> ManufacturingEstimate:
        for name, value in {
            "overhead_rate": inputs.overhead_rate,
            "waste_rate": inputs.waste_rate,
            "repair_reserve_rate": inputs.repair_reserve_rate,
            "wholesale_margin": inputs.wholesale_margin,
            "retail_margin": inputs.retail_margin,
        }.items():
            self._validate_rate(name, value)

        if inputs.labor_hours < 0 or inputs.labor_rate < 0 or inputs.packaging_cost < 0:
            raise ValueError("Labor and packaging values must be non-negative")

        materials = round(sum(line.total for line in inputs.materials), 2)
        hardware = round(sum(line.total for line in inputs.hardware), 2)
        labor = round(inputs.labor_hours * inputs.labor_rate, 2)
        waste_base = materials + hardware
        waste = round(waste_base * inputs.waste_rate, 2)
        direct = materials + hardware + labor + waste + inputs.packaging_cost
        overhead = round(direct * inputs.overhead_rate, 2)
        repair_reserve = round((direct + overhead) * inputs.repair_reserve_rate, 2)
        unit_cost = round(direct + overhead + repair_reserve, 2)
        wholesale = round(unit_cost / (1.0 - inputs.wholesale_margin), 2)
        retail = round(wholesale / (1.0 - inputs.retail_margin), 2)

        return ManufacturingEstimate(
            direct_materials=materials,
            direct_hardware=hardware,
            labor=labor,
            waste=waste,
            packaging=round(inputs.packaging_cost, 2),
            overhead=overhead,
            repair_reserve=repair_reserve,
            unit_cost=unit_cost,
            wholesale_price=wholesale,
            suggested_retail=retail,
        )
