"""Project-authoritative visual direction built from safe Art Study craft knowledge."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Tuple
from creative_intelligence.technique_profile import TechniqueProfile

WORK_KINDS=("static","animation","video")
@dataclass(frozen=True)
class VisualDirectionSpec:
    project_identity:str; project_constraints:Tuple[str,...]; craft_principles:Tuple[str,...]; construction_steps:Tuple[str,...]; studied_dimensions:Tuple[str,...]; provenance:Tuple[str,...]; work_kind:str="static"; principles_only:bool=True; direct_imitation_forbidden:bool=True; project_identity_authoritative:bool=True

def build_visual_direction(profile:TechniqueProfile,*,project_identity:str,project_constraints:Tuple[str,...]|list[str],work_kind:str="static")->VisualDirectionSpec:
    if not isinstance(profile,TechniqueProfile): raise ValueError("validated TechniqueProfile is required")
    if not profile.principles_only or not profile.direct_imitation_forbidden: raise ValueError("unsafe technique profile cannot influence visual direction")
    if not isinstance(project_identity,str) or not project_identity.strip(): raise ValueError("project_identity is required")
    if not isinstance(project_constraints,(tuple,list)): raise ValueError("project_constraints must be a list")
    kind=str(work_kind).strip().casefold()
    if kind not in WORK_KINDS: raise ValueError(f"work_kind must be one of: {', '.join(WORK_KINDS)}")
    constraints=tuple(item.strip() for item in project_constraints if isinstance(item,str) and item.strip())
    return VisualDirectionSpec(project_identity=project_identity.strip(),project_constraints=constraints,craft_principles=profile.principles,construction_steps=profile.construction_steps,studied_dimensions=profile.dimensions,provenance=profile.provenance,work_kind=kind)

def generation_context(spec:VisualDirectionSpec)->Mapping[str,object]:
    if not isinstance(spec,VisualDirectionSpec): raise ValueError("VisualDirectionSpec is required")
    return {"project_identity":spec.project_identity,"project_constraints":list(spec.project_constraints),"work_kind":spec.work_kind,"transferable_craft_principles":list(spec.craft_principles),"construction_steps":list(spec.construction_steps),"studied_dimensions":list(spec.studied_dimensions),"provenance":list(spec.provenance),"principles_only":True,"direct_imitation_forbidden":True,"project_identity_authoritative":True}
