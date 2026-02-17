from typing import Dict, Any
from ..schema import ProjectSpec

def simulate(spec: ProjectSpec) -> Dict[str, Any]:
    p_density = float(spec.assumptions.get("rf_power_density_w_m2", 1e-4))
    capture_area = float(spec.assumptions.get("capture_area_m2", max(spec.scale_m**2, 1e-6)))
    eff = float(spec.assumptions.get("rf_to_dc_efficiency", 0.2))
    harvest_w = p_density * capture_area * eff

    return {
        "model": "rf_harvest_v0",
        "rf_power_density_w_m2": p_density,
        "capture_area_m2": capture_area,
        "rf_to_dc_efficiency": eff,
        "pred_harvest_w": harvest_w
    }
