from typing import Tuple
from .schema import ProjectSpec

def scale_sanity(spec: ProjectSpec) -> Tuple[bool, str]:
    if spec.scale_m <= 0:
        return False, "scale_m must be > 0"
    if not (0 < spec.duty_cycle <= 1):
        return False, "duty_cycle must be in (0, 1]"
    if spec.target_power_w <= 0:
        return False, "target_power_w must be > 0"
    return True, "ok"

def claim_mismatch(spec: ProjectSpec) -> Tuple[bool, str]:
    if "nano" in spec.name.lower() and spec.scale_m > 1e-3:
        return False, "Name claims nano-scale but scale_m > 1 mm. Rename as macro demonstrator or fix scale."
    return True, "ok"

def rf_harvest_gate(spec: ProjectSpec) -> Tuple[bool, str, str]:
    p_density = float(spec.assumptions.get("rf_power_density_w_m2", 1e-4))
    capture_area = float(spec.assumptions.get("capture_area_m2", max(spec.scale_m**2, 1e-6)))
    eff = float(spec.assumptions.get("rf_to_dc_efficiency", 0.2))

    harvest_w = p_density * capture_area * eff
    required_avg_w = spec.target_power_w * spec.duty_cycle

    if harvest_w < required_avg_w:
        warn = f"RF harvest shortfall: harvest={harvest_w:.6g}W < required_avg={required_avg_w:.6g}W"
        return False, "Ambient RF cannot meet stated average power without stronger source / more area / higher efficiency.", warn

    return True, "ok", ""
