"""Environment models — Phase D2.

A `TwinEnvironment` represents a physical context where one or more
Digital Twins operate. It carries the ambient conditions (gravity,
temperature range, humidity, ambient light, atmospheric pressure) and
optional spatial bounds (axis-aligned bounding boxes for obstacles)
that simulations can reason about.

Environments are intentionally lightweight — they exist to let twin
simulations cross-check feasibility (e.g. "this drone needs ≥ 95 % O2
density: does the Mars Lab environment provide that?") without
mandating a full physics engine. When a real solver (OpenFOAM/FEniCS)
is plugged in, it can read the same environment doc.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timezone

from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EnvironmentCategory(str, Enum):
    INDOOR_LAB        = "indoor_lab"
    INDOOR_FACTORY    = "indoor_factory"
    INDOOR_HOME       = "indoor_home"
    OUTDOOR_TERRAIN   = "outdoor_terrain"
    OUTDOOR_URBAN     = "outdoor_urban"
    AQUATIC_SURFACE   = "aquatic_surface"
    AQUATIC_SUBMERGED = "aquatic_submerged"
    AERIAL_LOW        = "aerial_low"            # < 500 m AGL
    AERIAL_HIGH       = "aerial_high"           # commercial aviation alt
    ORBITAL           = "orbital"               # LEO/MEO/GEO
    LUNAR             = "lunar"
    MARTIAN           = "martian"
    DEEP_SPACE        = "deep_space"
    SIMULATED         = "simulated"             # purely virtual sandbox


class Obstacle(BaseModel):
    """Axis-aligned bounding box obstacle (metres). For collision /
    pathing simulations. Origin is the env's lower corner (0,0,0)."""
    name: str
    min_xyz: Tuple[float, float, float]
    max_xyz: Tuple[float, float, float]
    material: Optional[str] = None
    is_static: bool = True


class TwinEnvironment(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    category: EnvironmentCategory
    description: Optional[str] = None

    # Spatial bounds — twins outside these AABB are flagged.
    bounds_m: Tuple[float, float, float] = (10.0, 10.0, 3.0)
    obstacles: List[Obstacle] = Field(default_factory=list)

    # Ambient conditions (ranges)
    gravity_m_s2: float = 9.81
    temp_c_range: Tuple[float, float] = (15.0, 30.0)
    humidity_pct_range: Tuple[float, float] = (30.0, 70.0)
    pressure_kpa: float = 101.3
    ambient_lux_range: Tuple[float, float] = (300.0, 1000.0)
    wind_m_s_range: Tuple[float, float] = (0.0, 0.5)

    # Atmospheric mix — for life-support / combustion checks
    atmo_o2_pct: float = 20.9
    atmo_co2_ppm: float = 420.0

    # Bookkeeping
    twins_assigned: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    owner_agent: str = "ajani"
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)


class EnvironmentAssignmentResult(BaseModel):
    """Returned when a twin is bound to / unbound from an environment.
    Carries the compatibility check the registry runs before accepting."""
    ok: bool
    twin_id: str
    environment_id: str
    compatibility_issues: List[str] = Field(default_factory=list)
    bound_at: str = Field(default_factory=_now)
