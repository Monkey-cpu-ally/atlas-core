from __future__ import annotations

from dataclasses import asdict
from typing import List

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - exercised only without optional API dependencies
    FastAPI = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from .engineering import (
    ApparelEngineeringCalculator,
    BagEngineeringCalculator,
    FootwearEngineeringCalculator,
    FurnitureEngineeringCalculator,
)
from .manufacturing import CostLine, ManufacturingCostEngine, ManufacturingInputs


if FastAPI is not None:
    class CostLineRequest(BaseModel):
        name: str
        unit_cost: float = Field(ge=0)
        quantity: float = Field(default=1.0, ge=0)


    class ManufacturingRequest(BaseModel):
        materials: List[CostLineRequest] = []
        hardware: List[CostLineRequest] = []
        labor_hours: float = Field(default=0, ge=0)
        labor_rate: float = Field(default=0, ge=0)
        packaging_cost: float = Field(default=0, ge=0)
        overhead_rate: float = Field(default=0.15, ge=0, lt=1)
        waste_rate: float = Field(default=0.08, ge=0, lt=1)
        repair_reserve_rate: float = Field(default=0.03, ge=0, lt=1)
        wholesale_margin: float = Field(default=0.45, ge=0, lt=1)
        retail_margin: float = Field(default=0.65, ge=0, lt=1)


    class BagRequest(BaseModel):
        width_cm: float = Field(gt=0)
        height_cm: float = Field(gt=0)
        depth_cm: float = Field(gt=0)
        loaded_mass_kg: float = Field(ge=0)
        strap_count: int = Field(default=2, ge=1)
        safety_factor: float = Field(default=3.0, ge=1)


    class FootwearRequest(BaseModel):
        foot_length_mm: float = Field(gt=0)
        toe_allowance_mm: float = Field(ge=0)
        heel_stack_mm: float = Field(ge=0)
        forefoot_stack_mm: float = Field(ge=0)
        single_shoe_mass_g: float = Field(ge=0)


    class FurnitureRequest(BaseModel):
        rated_user_mass_kg: float = Field(gt=0)
        dynamic_factor: float = Field(default=2.0, ge=1)
        leg_count: int = Field(default=4, ge=1)
        width_mm: float = Field(gt=0)
        depth_mm: float = Field(gt=0)
        height_mm: float = Field(gt=0)


    class ApparelRequest(BaseModel):
        body_measurement_cm: float = Field(gt=0)
        ease_cm: float = 0
        seam_allowance_cm: float = Field(gt=0)
        seam_count: int = Field(ge=1)
        garment_length_cm: float = Field(gt=0)
        fabric_width_cm: float = Field(gt=0)
        layout_factor: float = Field(default=1.35, ge=1)


def create_app():
    if FastAPI is None:
        raise RuntimeError(
            "FastAPI support requires optional dependencies: pip install fastapi uvicorn"
        ) from _IMPORT_ERROR

    app = FastAPI(
        title="ATLAS House of Frazier API",
        version="0.1.0",
        description="Engineering, manufacturing, and design workflow services.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "system": "house-of-frazier"}

    @app.post("/manufacturing/estimate")
    def manufacturing_estimate(request: ManufacturingRequest):
        inputs = ManufacturingInputs(
            materials=[CostLine(**line.model_dump()) for line in request.materials],
            hardware=[CostLine(**line.model_dump()) for line in request.hardware],
            labor_hours=request.labor_hours,
            labor_rate=request.labor_rate,
            packaging_cost=request.packaging_cost,
            overhead_rate=request.overhead_rate,
            waste_rate=request.waste_rate,
            repair_reserve_rate=request.repair_reserve_rate,
            wholesale_margin=request.wholesale_margin,
            retail_margin=request.retail_margin,
        )
        return asdict(ManufacturingCostEngine().estimate(inputs))

    @app.post("/engineering/bag")
    def engineer_bag(request: BagRequest):
        return asdict(BagEngineeringCalculator().analyze(**request.model_dump()))

    @app.post("/engineering/footwear")
    def engineer_footwear(request: FootwearRequest):
        try:
            result = FootwearEngineeringCalculator().analyze(**request.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return asdict(result)

    @app.post("/engineering/furniture")
    def engineer_furniture(request: FurnitureRequest):
        return asdict(FurnitureEngineeringCalculator().analyze(**request.model_dump()))

    @app.post("/engineering/apparel")
    def engineer_apparel(request: ApparelRequest):
        return asdict(ApparelEngineeringCalculator().analyze(**request.model_dump()))

    return app


app = create_app() if FastAPI is not None else None
