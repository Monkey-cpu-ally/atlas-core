"""Canonical reference-intelligence boundary shared by Creative Studio executors."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


def string_tuple(value, field: str, *, reject_duplicates: bool = True) -> tuple[str, ...]:
    if value is None: return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be a list of strings")
    result=[]; seen=set()
    for item in value:
        if not isinstance(item,str) or not item.strip(): raise ValueError(f"{field} must contain non-empty strings")
        clean=item.strip(); key=clean.casefold()
        if key in seen:
            if reject_duplicates: raise ValueError(f"duplicate values are not allowed in {field}")
            continue
        seen.add(key); result.append(clean)
    return tuple(result)


@dataclass(frozen=True)
class ReferenceContext:
    query:str=""
    project_identity:str=""
    project_constraints:tuple[str,...]=()
    diversity_dimensions:tuple[str,...]=()
    reference_ids:tuple[str,...]=()
    principles:tuple[str,...]=()
    study_targets:tuple[str,...]=()
    limitations:tuple[str,...]=()
    provenance:tuple[str,...]=()

    @classmethod
    def from_mapping(cls,payload):
        if payload in (None,{}): return None
        if not isinstance(payload,Mapping): raise ValueError("reference_context must be an object")
        identity=payload.get("project_identity",""); query=payload.get("query","")
        if not isinstance(identity,str) or not isinstance(query,str): raise ValueError("reference context identity and query must be strings")
        contract=payload.get("contract",{})
        if not isinstance(contract,Mapping): raise ValueError("reference context contract must be an object")
        required={"principle_only":"reference context must enforce principle-only use","project_identity_overrides_reference_influence":"reference context must preserve project identity authority"}
        for key,message in required.items():
            if contract.get(key) is not True: raise ValueError(message)
        constraints=string_tuple(payload.get("project_constraints",()),"project_constraints")
        if constraints:
            if contract.get("project_constraints_preserved") is not True: raise ValueError("reference context must preserve project constraints")
            if contract.get("constraints_are_not_inspiration") is not True: raise ValueError("reference context constraints must not be inspiration")
        provenance=string_tuple(payload.get("provenance",()),"provenance")
        reference_ids=string_tuple(payload.get("reference_ids",()),"reference_ids")
        if reference_ids and not provenance: raise ValueError("reference context with references requires provenance")
        return cls(query.strip(),identity.strip(),constraints,string_tuple(payload.get("diversity_dimensions",()),"diversity_dimensions"),reference_ids,string_tuple(payload.get("principles",()),"principles"),string_tuple(payload.get("study_targets",()),"study_targets"),string_tuple(payload.get("limitations",()),"limitations"),provenance)
