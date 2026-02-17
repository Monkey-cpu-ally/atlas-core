from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import uuid


def new_id(prefix: str = "item") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class Part:
    part_id: str
    name: str
    roles: List[str]
    description: str
    mass_kg: float = 0.0
    power_w: float = 0.0
    service_access: str = "reachable"
    notes: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.part_id,
            "name": self.name,
            "roles": self.roles,
            "mass_kg": self.mass_kg,
            "power_w": self.power_w,
        }


@dataclass
class Joint:
    joint_id: str
    name: str
    dof: int
    joint_family: str
    compliance: str
    range_deg: Tuple[float, float]
    description: str
    notes: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.joint_id,
            "name": self.name,
            "family": self.joint_family,
            "dof": self.dof,
            "compliance": self.compliance,
            "range": self.range_deg,
        }


@dataclass
class OrganPack:
    pack_id: str
    name: str
    roles: List[str]
    description: str
    capacity: Dict[str, Any]
    mass_kg: float = 0.0
    notes: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.pack_id,
            "name": self.name,
            "roles": self.roles,
            "capacity": self.capacity,
            "mass_kg": self.mass_kg,
        }


@dataclass
class Assembly:
    assembly_id: str
    name: str
    parts: List[Part] = field(default_factory=list)
    joints: List[Joint] = field(default_factory=list)
    organs: List[OrganPack] = field(default_factory=list)

    def total_mass_kg(self) -> float:
        return (
            sum(p.mass_kg for p in self.parts)
            + sum(o.mass_kg for o in self.organs)
        )

    def total_power_w(self) -> float:
        return sum(p.power_w for p in self.parts)

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.assembly_id,
            "name": self.name,
            "parts": len(self.parts),
            "joints": len(self.joints),
            "organs": len(self.organs),
            "total_mass_kg": round(self.total_mass_kg(), 2),
            "total_power_w": round(self.total_power_w(), 2),
        }
