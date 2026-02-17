from typing import Any, Dict, List, Tuple
from .schema import ProjectSpec, Tier, Confidence
from .physics import scale_sanity, claim_mismatch, rf_harvest_gate
from .simulators import SIM_MAP

def assign_tier(spec: ProjectSpec, failures: List[str], warnings: List[str]) -> Tuple[Tier, Confidence]:
    if failures:
        return "T4_SPECULATIVE", "LOW"

    needs_lab = ("cleanroom" in spec.fabrication) or (spec.scale_m < 1e-4)
    if needs_lab:
        return "T2_RESEARCH_GRADE", "MEDIUM"

    if spec.domain == "rf_energy" and (spec.target_power_w * spec.duty_cycle) > 0.01:
        return "T3_FRONTIER", "LOW"

    return "T1_BUILDABLE_NOW", "HIGH"

def validate_and_simulate(spec: ProjectSpec) -> Dict[str, Any]:
    failures: List[str] = []
    warnings: List[str] = []

    ok, msg = scale_sanity(spec)
    if not ok: failures.append(msg)

    ok, msg = claim_mismatch(spec)
    if not ok: failures.append(msg)

    if spec.domain == "rf_energy":
        ok, msg, warn = rf_harvest_gate(spec)
        if not ok: failures.append(msg)
        if warn: warnings.append(warn)

    sim_result = None
    if not failures:
        sim_fn = SIM_MAP.get(spec.domain)
        if sim_fn:
            sim_result = sim_fn(spec)
            if isinstance(sim_result, dict) and "pred_speed_m_s" in sim_result:
                if sim_result["pred_speed_m_s"] <= 0:
                    failures.append("Simulation predicts non-positive speed; revise assumptions.")
        else:
            warnings.append("No simulator registered for this domain yet.")

    tier, confidence = assign_tier(spec, failures, warnings)
    blueprint_allowed = (len(failures) == 0 and tier != "T4_SPECULATIVE")

    return {
        "project_id": spec.project_id,
        "name": spec.name,
        "tier": tier,
        "confidence": confidence,
        "blueprint_allowed": blueprint_allowed,
        "failures": failures,
        "warnings": warnings,
        "simulation": sim_result,
        "inputs": {
            "domain": spec.domain,
            "scale_m": spec.scale_m,
            "target_power_w": spec.target_power_w,
            "duty_cycle": spec.duty_cycle,
            "environment": spec.environment,
            "fabrication": spec.fabrication,
        }
    }
