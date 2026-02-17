from dataclasses import dataclass
from typing import Any, Dict, List, Literal

Tier = Literal["T1_BUILDABLE_NOW", "T2_RESEARCH_GRADE", "T3_FRONTIER", "T4_SPECULATIVE"]
Confidence = Literal["LOW", "MEDIUM", "HIGH"]

@dataclass
class ProjectSpec:
    project_id: str
    name: str
    domain: str
    scale_m: float
    target_power_w: float
    duty_cycle: float
    environment: str
    materials: List[str]
    fabrication: List[str]
    assumptions: Dict[str, Any]

def from_dict(d: Dict[str, Any]) -> ProjectSpec:
    required = ["project_id","name","domain","scale_m","target_power_w","duty_cycle","environment","materials","fabrication"]
    missing = [k for k in required if k not in d]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    return ProjectSpec(
        project_id=str(d["project_id"]),
        name=str(d["name"]),
        domain=str(d["domain"]),
        scale_m=float(d["scale_m"]),
        target_power_w=float(d["target_power_w"]),
        duty_cycle=float(d["duty_cycle"]),
        environment=str(d["environment"]),
        materials=list(d["materials"]),
        fabrication=list(d["fabrication"]),
        assumptions=dict(d.get("assumptions", {})),
    )
