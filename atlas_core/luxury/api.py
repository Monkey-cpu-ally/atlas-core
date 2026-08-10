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

from .digital_twin import LifecycleEvent, LifecycleEventType, ProductDigitalTwin
from .digital_twin_store import DigitalTwinStore
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


    class DigitalTwinCreateRequest(BaseModel):
        product_id: str
        product_name: str
        collection_id: str | None = None
        serial_number: str | None = None
        materials: List[str] = []
        hardware: List[str] = []
        readiness_level: int = Field(default=1, ge=1, le=9)
        owner_reference: str | None = None


    class DigitalTwinEventRequest(BaseModel):
        event_type: LifecycleEventType
        summary: str
        metadata: dict[str, object] = {}


    class DigitalTwinRevisionRequest(BaseModel):
        revision: int = Field(ge=2)
        summary: str


    class DigitalTwinRepairRequest(BaseModel):
        summary: str
        provider: str | None = None
        cost: float | None = Field(default=None, ge=0)


    class DigitalTwinReadinessRequest(BaseModel):
        readiness_level: int = Field(ge=1, le=9)


def create_app(database_path: str = "atlas_luxury.db"):
    if FastAPI is None:
        raise RuntimeError(
            "FastAPI support requires optional dependencies: pip install fastapi uvicorn"
        ) from _IMPORT_ERROR

    app = FastAPI(
        title="ATLAS House of Frazier API",
        version="0.2.0",
        description="Engineering, manufacturing, design workflow, and lifecycle services.",
    )
    twin_store = DigitalTwinStore(database_path)

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

    @app.post("/digital-twins")
    def create_digital_twin(request: DigitalTwinCreateRequest):
        if twin_store.load(request.product_id) is not None:
            raise HTTPException(status_code=409, detail="Digital twin already exists")
        twin = ProductDigitalTwin(**request.model_dump())
        twin.add_event(LifecycleEvent(LifecycleEventType.CREATED, "Digital twin created"))
        twin_store.save(twin)
        return asdict(twin)

    @app.get("/digital-twins/{product_id}")
    def get_digital_twin(product_id: str):
        twin = twin_store.load(product_id)
        if twin is None:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        return asdict(twin)

    @app.post("/digital-twins/{product_id}/events")
    def add_digital_twin_event(product_id: str, request: DigitalTwinEventRequest):
        twin = twin_store.load(product_id)
        if twin is None:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        twin.add_event(LifecycleEvent(request.event_type, request.summary, request.metadata))
        twin_store.save(twin)
        return asdict(twin)

    @app.post("/digital-twins/{product_id}/revisions")
    def revise_digital_twin(product_id: str, request: DigitalTwinRevisionRequest):
        twin = twin_store.load(product_id)
        if twin is None:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        try:
            twin.record_revision(request.revision, request.summary)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        twin_store.save(twin)
        return asdict(twin)

    @app.post("/digital-twins/{product_id}/repairs")
    def repair_digital_twin(product_id: str, request: DigitalTwinRepairRequest):
        twin = twin_store.load(product_id)
        if twin is None:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        twin.record_repair(request.summary, request.provider, request.cost)
        twin_store.save(twin)
        return asdict(twin)

    @app.put("/digital-twins/{product_id}/readiness")
    def set_digital_twin_readiness(product_id: str, request: DigitalTwinReadinessRequest):
        twin = twin_store.load(product_id)
        if twin is None:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        twin.readiness_level = request.readiness_level
        twin_store.save(twin)
        return asdict(twin)

    return app


app = create_app() if FastAPI is not None else None
