from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    FAIL = "FAIL"


class ValidationCheck(BaseModel):
    name: str
    status: CheckStatus
    score: float = Field(ge=0.0, le=1.0)
    notes: List[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    tier: int
    tier_label: str
    completion: str
    overall_score: float
    checks: List[ValidationCheck]
    blockers: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)


class ScaleSpec(BaseModel):
    size_class: Optional[str] = None
    dimensions_cm: Optional[Dict[str, float]] = None
    mass_kg: Optional[float] = None


class EnergySpec(BaseModel):
    power_needed: Optional[bool] = None
    source: Optional[str] = None
    watts: Optional[float] = None


class MaterialSpec(BaseModel):
    material_family: Optional[str] = None
    candidates: List[str] = Field(default_factory=list)


class FabricationSpec(BaseModel):
    methods: List[str] = Field(default_factory=list)
    tolerance_level: Optional[str] = None


class PhysicsSpec(BaseModel):
    mechanism: Optional[str] = None
    test_method: Optional[str] = None
    success_metric: Optional[str] = None
    flags: List[str] = Field(default_factory=list)


class ProjectSpec(BaseModel):
    title: str
    domain: Optional[str] = None
    scale: ScaleSpec = Field(default_factory=ScaleSpec)
    energy: EnergySpec = Field(default_factory=EnergySpec)
    material: MaterialSpec = Field(default_factory=MaterialSpec)
    fabrication: FabricationSpec = Field(default_factory=FabricationSpec)
    physics: PhysicsSpec = Field(default_factory=PhysicsSpec)


SIZE_DEFAULTS_CM = {
    "micro": {"x": 2, "y": 2, "z": 2},
    "handheld": {"x": 25, "y": 15, "z": 8},
    "desktop": {"x": 60, "y": 40, "z": 30},
    "room": {"x": 200, "y": 200, "z": 200},
    "building": {"x": 1000, "y": 1000, "z": 3000},
}

FAB_SUGGESTIONS_BY_DOMAIN = {
    "materials": ["mold_cast", "compression_mold", "laser_cut_fixture"],
    "robotics": ["3d_print", "cnc", "laser_cut"],
    "bio": ["benchtop_assay", "microfluidics", "lab_prototype"],
    "energy": ["breadboard", "cnc", "3d_print"],
    "crypto": ["software_only", "hardware_hsm_mock", "tpm_integration"],
    None: ["3d_print", "laser_cut", "cnc"],
}

MATERIAL_SUGGESTIONS_BY_DOMAIN = {
    "materials": ["epoxy_composite", "aluminum_alloy", "ceramic_matrix"],
    "robotics": ["aluminum_6061", "carbon_fiber", "abs_or_petg"],
    "bio": ["pdms", "biocompatible_polymer", "glass"],
    "energy": ["copper", "aluminum", "high_temp_polymer"],
    "crypto": ["n/a_software", "secure_element", "tpm_module"],
    None: ["abs_or_petg", "aluminum_6061", "acrylic"],
}


def _field_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    if isinstance(value, dict) and len(value) == 0:
        return True
    return False


def _score_from_parts(parts: List[bool]) -> float:
    if not parts:
        return 0.0
    return sum(1.0 for p in parts if p) / float(len(parts))


def check_scale(p: ProjectSpec) -> Tuple[ValidationCheck, List[str]]:
    missing = []
    present_parts = []

    present_parts.append(not _field_missing(p.scale.size_class))
    if _field_missing(p.scale.size_class):
        missing.append("scale.size_class")

    dims_present = not _field_missing(p.scale.dimensions_cm)
    present_parts.append(dims_present)

    score = _score_from_parts(present_parts)
    if score == 1.0:
        status = CheckStatus.PASS
    elif score >= 0.5:
        status = CheckStatus.PARTIAL
    else:
        status = CheckStatus.MISSING

    notes = []
    if p.scale.size_class and _field_missing(p.scale.dimensions_cm):
        notes.append(f"Dimensions not set; suggest default for {p.scale.size_class}.")

    return ValidationCheck(name="Scale", status=status, score=score, notes=notes), missing


def check_energy(p: ProjectSpec) -> Tuple[ValidationCheck, List[str]]:
    missing = []
    present_parts = []

    present_parts.append(not _field_missing(p.energy.power_needed))
    if _field_missing(p.energy.power_needed):
        missing.append("energy.power_needed")

    present_parts.append(not _field_missing(p.energy.source))
    if _field_missing(p.energy.source):
        missing.append("energy.source")

    watts_required = (p.energy.power_needed is True)
    watts_present = not _field_missing(p.energy.watts)
    present_parts.append((not watts_required) or watts_present)
    if watts_required and not watts_present:
        missing.append("energy.watts")

    score = _score_from_parts(present_parts)
    if score == 1.0:
        status = CheckStatus.PASS
    elif score >= 0.5:
        status = CheckStatus.PARTIAL
    else:
        status = CheckStatus.MISSING

    notes = []
    if p.energy.power_needed is False and p.energy.source and p.energy.source != "none":
        notes.append("power_needed=False but source is set; consider source='none'.")

    return ValidationCheck(name="Energy", status=status, score=score, notes=notes), missing


def check_material(p: ProjectSpec) -> Tuple[ValidationCheck, List[str]]:
    missing = []
    present_parts = []

    present_parts.append(not _field_missing(p.material.material_family))
    if _field_missing(p.material.material_family):
        missing.append("material.material_family")

    candidates_present = (len(p.material.candidates) >= 2)
    present_parts.append(candidates_present)
    if not candidates_present:
        missing.append("material.candidates (need 2+)")

    score = _score_from_parts(present_parts)
    if score == 1.0:
        status = CheckStatus.PASS
    elif score >= 0.5:
        status = CheckStatus.PARTIAL
    else:
        status = CheckStatus.MISSING

    notes = []
    if len(p.material.candidates) == 1:
        notes.append("Only 1 candidate material listed; add at least one alternative.")

    return ValidationCheck(name="Material", status=status, score=score, notes=notes), missing


def check_fabrication(p: ProjectSpec) -> Tuple[ValidationCheck, List[str]]:
    missing = []
    present_parts = []

    methods_present = (len(p.fabrication.methods) >= 1)
    present_parts.append(methods_present)
    if not methods_present:
        missing.append("fabrication.methods")

    present_parts.append(not _field_missing(p.fabrication.tolerance_level))
    if _field_missing(p.fabrication.tolerance_level):
        missing.append("fabrication.tolerance_level")

    score = _score_from_parts(present_parts)
    if score == 1.0:
        status = CheckStatus.PASS
    elif score >= 0.5:
        status = CheckStatus.PARTIAL
    else:
        status = CheckStatus.MISSING

    notes = []
    if methods_present and _field_missing(p.fabrication.tolerance_level):
        notes.append("Tolerance not specified; 'normal' is a good default for early prototypes.")

    return ValidationCheck(name="Fabrication", status=status, score=score, notes=notes), missing


def check_physics(p: ProjectSpec) -> Tuple[ValidationCheck, List[str], List[str]]:
    missing = []
    blockers = []
    present_parts = []

    present_parts.append(not _field_missing(p.physics.mechanism))
    if _field_missing(p.physics.mechanism):
        missing.append("physics.mechanism")

    present_parts.append(not _field_missing(p.physics.test_method))
    if _field_missing(p.physics.test_method):
        missing.append("physics.test_method")

    present_parts.append(not _field_missing(p.physics.success_metric))
    if _field_missing(p.physics.success_metric):
        missing.append("physics.success_metric")

    contradiction_flags = {"thermo_violation", "causality_violation", "perpetual_motion"}
    if any(f in contradiction_flags for f in (p.physics.flags or [])):
        blockers.append("Physics contradiction flagged (e.g., thermo/causality/perpetual motion).")
        return (
            ValidationCheck(name="Physics", status=CheckStatus.FAIL, score=0.0,
                            notes=["Resolve contradiction flags before build."]),
            missing,
            blockers
        )

    score = _score_from_parts(present_parts)
    if score == 1.0:
        status = CheckStatus.PASS
    elif score >= 0.34:
        status = CheckStatus.PARTIAL
    else:
        status = CheckStatus.MISSING

    notes = []
    if status != CheckStatus.PASS:
        notes.append("Physics needs a measurable mechanism + test + metric (no vibes-only).")

    return ValidationCheck(name="Physics", status=status, score=score, notes=notes), missing, blockers


def generate_recommendations(p: ProjectSpec, missing_fields: List[str], checks: List[ValidationCheck]) -> List[str]:
    recs: List[str] = []

    if "scale.size_class" in missing_fields:
        recs.append("Scale: Pick size_class = micro | handheld | desktop | room | building (default suggestion: handheld).")
    if _field_missing(p.scale.dimensions_cm) and not _field_missing(p.scale.size_class):
        default_dims = SIZE_DEFAULTS_CM.get(p.scale.size_class, SIZE_DEFAULTS_CM["handheld"])
        recs.append(f"Scale: Set dimensions_cm (suggested default for {p.scale.size_class}: {default_dims}).")

    if "energy.power_needed" in missing_fields:
        recs.append("Energy: Set power_needed = True/False. If unsure, start False for passive prototypes.")
    if "energy.source" in missing_fields:
        recs.append("Energy: Set source = none | battery | wall | solar | other.")
    if "energy.watts" in missing_fields:
        recs.append("Energy: Add watts (rough estimate ok). Example: 5W small sensor, 30W compute, 200W actuator.")

    if "material.material_family" in missing_fields:
        sugg = MATERIAL_SUGGESTIONS_BY_DOMAIN.get(p.domain, MATERIAL_SUGGESTIONS_BY_DOMAIN[None])
        recs.append(f"Material: Choose material_family and add candidates. Suggestions: {', '.join(sugg)}.")
    if "material.candidates (need 2+)" in missing_fields:
        sugg = MATERIAL_SUGGESTIONS_BY_DOMAIN.get(p.domain, MATERIAL_SUGGESTIONS_BY_DOMAIN[None])
        recs.append(f"Material: Add at least 2 candidate materials (e.g., {sugg[0]} + {sugg[1]}).")

    if "fabrication.methods" in missing_fields:
        sugg = FAB_SUGGESTIONS_BY_DOMAIN.get(p.domain, FAB_SUGGESTIONS_BY_DOMAIN[None])
        recs.append(f"Fabrication: Pick at least 1 method (suggestions: {', '.join(sugg)}).")
    if "fabrication.tolerance_level" in missing_fields:
        recs.append("Fabrication: Set tolerance_level = loose | normal | tight (default: normal).")

    if "physics.mechanism" in missing_fields:
        recs.append("Physics: Write 1-2 sentences: what mechanism makes it work? (cause -> effect).")
    if "physics.test_method" in missing_fields:
        recs.append("Physics: Choose a test method (bench test, simulation, field test, assay, etc.).")
    if "physics.success_metric" in missing_fields:
        recs.append("Physics: Define a success metric (number + unit + threshold). Example: >20% filtration, <5C rise, <200ms response.")

    if any(c.status == CheckStatus.FAIL for c in checks):
        recs.insert(0, "Fix Physics contradictions first (flags like thermo_violation/perpetual_motion block build).")

    if not missing_fields and all(c.status in (CheckStatus.PASS, CheckStatus.PARTIAL) for c in checks):
        recs.append("Next step: Run a smallest-possible prototype test and log results (1 metric, 1 variable changed at a time).")

    return recs


def choose_tier(checks: List[ValidationCheck]) -> Tuple[int, str]:
    if any(c.status == CheckStatus.FAIL for c in checks):
        return 4, "Speculative / Blocked (contradiction flagged)"

    overall = sum(c.score for c in checks) / float(len(checks))
    if overall >= 0.8:
        return 3, "Engineering Track"
    if overall >= 0.6:
        return 2, "Prototype Ready"
    return 1, "Conceptual Sandbox"


def validate_project(p: ProjectSpec) -> ValidationReport:
    checks: List[ValidationCheck] = []
    missing_fields: List[str] = []
    blockers: List[str] = []

    c, m = check_scale(p); checks.append(c); missing_fields += m
    c, m = check_energy(p); checks.append(c); missing_fields += m
    c, m = check_material(p); checks.append(c); missing_fields += m
    c, m = check_fabrication(p); checks.append(c); missing_fields += m
    c, m, b = check_physics(p); checks.append(c); missing_fields += m; blockers += b

    overall_score = sum(c.score for c in checks) / float(len(checks))

    complete_count = sum(1 for c in checks if c.status in (CheckStatus.PASS, CheckStatus.PARTIAL))
    completion = f"{complete_count}/5 complete"

    tier, label = choose_tier(checks)
    recs = generate_recommendations(p, missing_fields, checks)

    return ValidationReport(
        tier=tier,
        tier_label=label,
        completion=completion,
        overall_score=round(overall_score, 3),
        checks=checks,
        blockers=blockers,
        recommendations=recs,
        missing_fields=sorted(set(missing_fields))
    )


def autofill_minimums(p: ProjectSpec) -> ProjectSpec:
    if _field_missing(p.scale.size_class):
        p.scale.size_class = "handheld"
    if _field_missing(p.scale.dimensions_cm):
        p.scale.dimensions_cm = SIZE_DEFAULTS_CM.get(p.scale.size_class, SIZE_DEFAULTS_CM["handheld"])

    if _field_missing(p.energy.power_needed):
        p.energy.power_needed = False
    if _field_missing(p.energy.source):
        p.energy.source = "none" if p.energy.power_needed is False else "battery"

    if _field_missing(p.fabrication.tolerance_level):
        p.fabrication.tolerance_level = "normal"
    if _field_missing(p.fabrication.methods):
        p.fabrication.methods = [FAB_SUGGESTIONS_BY_DOMAIN.get(p.domain, ["3d_print"])[0]]

    if _field_missing(p.material.material_family):
        p.material.material_family = "polymer"
    if len(p.material.candidates) < 2:
        sugg = MATERIAL_SUGGESTIONS_BY_DOMAIN.get(p.domain, MATERIAL_SUGGESTIONS_BY_DOMAIN[None])
        for s in sugg:
            if s not in p.material.candidates:
                p.material.candidates.append(s)
            if len(p.material.candidates) >= 2:
                break

    return p
