from __future__ import annotations

from dataclasses import dataclass
from math import pi


@dataclass(frozen=True)
class BagEngineeringResult:
    volume_liters: float
    strap_force_newtons: float
    force_per_strap_newtons: float
    recommended_safety_load_newtons: float


class BagEngineeringCalculator:
    GRAVITY = 9.80665

    def analyze(
        self,
        width_cm: float,
        height_cm: float,
        depth_cm: float,
        loaded_mass_kg: float,
        strap_count: int = 2,
        safety_factor: float = 3.0,
    ) -> BagEngineeringResult:
        if min(width_cm, height_cm, depth_cm, loaded_mass_kg) < 0:
            raise ValueError("Dimensions and mass must be non-negative")
        if strap_count < 1 or safety_factor < 1:
            raise ValueError("At least one strap and safety factor >= 1 are required")
        volume = width_cm * height_cm * depth_cm / 1000.0
        force = loaded_mass_kg * self.GRAVITY
        return BagEngineeringResult(
            volume_liters=round(volume, 2),
            strap_force_newtons=round(force, 2),
            force_per_strap_newtons=round(force / strap_count, 2),
            recommended_safety_load_newtons=round(force * safety_factor, 2),
        )


@dataclass(frozen=True)
class FootwearEngineeringResult:
    internal_length_mm: float
    heel_to_toe_drop_mm: float
    estimated_pair_mass_g: float


class FootwearEngineeringCalculator:
    def analyze(
        self,
        foot_length_mm: float,
        toe_allowance_mm: float,
        heel_stack_mm: float,
        forefoot_stack_mm: float,
        single_shoe_mass_g: float,
    ) -> FootwearEngineeringResult:
        if min(foot_length_mm, toe_allowance_mm, heel_stack_mm, forefoot_stack_mm, single_shoe_mass_g) < 0:
            raise ValueError("Footwear measurements must be non-negative")
        if heel_stack_mm < forefoot_stack_mm:
            raise ValueError("Heel stack cannot be lower than forefoot stack for this calculator")
        return FootwearEngineeringResult(
            internal_length_mm=round(foot_length_mm + toe_allowance_mm, 2),
            heel_to_toe_drop_mm=round(heel_stack_mm - forefoot_stack_mm, 2),
            estimated_pair_mass_g=round(single_shoe_mass_g * 2.0, 2),
        )


@dataclass(frozen=True)
class FurnitureEngineeringResult:
    design_load_kg: float
    load_per_leg_kg: float
    footprint_area_m2: float
    slenderness_ratio: float


class FurnitureEngineeringCalculator:
    def analyze(
        self,
        rated_user_mass_kg: float,
        dynamic_factor: float,
        leg_count: int,
        width_mm: float,
        depth_mm: float,
        height_mm: float,
    ) -> FurnitureEngineeringResult:
        if min(rated_user_mass_kg, width_mm, depth_mm, height_mm) <= 0:
            raise ValueError("Mass and dimensions must be positive")
        if dynamic_factor < 1 or leg_count < 1:
            raise ValueError("Dynamic factor >= 1 and at least one leg are required")
        design_load = rated_user_mass_kg * dynamic_factor
        minimum_base = min(width_mm, depth_mm)
        return FurnitureEngineeringResult(
            design_load_kg=round(design_load, 2),
            load_per_leg_kg=round(design_load / leg_count, 2),
            footprint_area_m2=round((width_mm / 1000.0) * (depth_mm / 1000.0), 4),
            slenderness_ratio=round(height_mm / minimum_base, 3),
        )


@dataclass(frozen=True)
class ApparelEngineeringResult:
    finished_measurement_cm: float
    pattern_measurement_cm: float
    estimated_fabric_m: float


class ApparelEngineeringCalculator:
    def analyze(
        self,
        body_measurement_cm: float,
        ease_cm: float,
        seam_allowance_cm: float,
        seam_count: int,
        garment_length_cm: float,
        fabric_width_cm: float,
        layout_factor: float = 1.35,
    ) -> ApparelEngineeringResult:
        if min(body_measurement_cm, seam_allowance_cm, garment_length_cm, fabric_width_cm) <= 0:
            raise ValueError("Measurements must be positive")
        if seam_count < 1 or layout_factor < 1:
            raise ValueError("At least one seam and layout factor >= 1 are required")
        finished = body_measurement_cm + ease_cm
        pattern = finished + (2.0 * seam_allowance_cm * seam_count)
        area_cm2 = pattern * garment_length_cm * layout_factor
        fabric_length_cm = area_cm2 / fabric_width_cm
        return ApparelEngineeringResult(
            finished_measurement_cm=round(finished, 2),
            pattern_measurement_cm=round(pattern, 2),
            estimated_fabric_m=round(fabric_length_cm / 100.0, 2),
        )
