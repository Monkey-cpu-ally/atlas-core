"""Reference twin specs — Phase D5 (Green Robot) + D6 (Power Cell).

Builds two reference Digital Twins on first boot, with realistic state
(components, dependencies, energy profile, dimensions) and a thermal
configuration so the new THERMAL ODE engine has something to chew on.

Idempotent — already-present twins are skipped.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from models.twin_models import (
    Component,
    Dependency,
    DigitalTwin,
    Dimensions,
    EnergyProfile,
    SensorInput,
    TwinCategory,
    TwinOutput,
    TwinStatus,
    TwinState,
)
from services import memory_bank as mb

logger = logging.getLogger("atlas.reference_twins")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _twins():     return _db()["digital_twins"]
def _blueprints(): return _db()["blueprints"]


# ===========================================================================
# D5 — Green Robot · AGRI-ROVER-01
# ===========================================================================
def _build_agri_rover() -> DigitalTwin:
    components: List[Component] = [
        Component(id="frame",        name="Frame · 6061 aluminium chassis 60×40 cm",
                  quantity=1, cost_per_unit=85.0, mass_kg=2.4,
                  lead_time_days=3, material="aluminium_6061"),
        Component(id="drive_motors", name="Brushless DC drive motor (×4)",
                  quantity=4, cost_per_unit=42.0, mass_kg=0.35,
                  lead_time_days=7),
        Component(id="motor_drivers", name="ESC 30 A motor driver (×4)",
                  quantity=4, cost_per_unit=18.0, mass_kg=0.06,
                  lead_time_days=5),
        Component(id="wheels",       name="40 mm foam-rubber wheel (×4)",
                  quantity=4, cost_per_unit=8.0,  mass_kg=0.12,
                  lead_time_days=4, material="foam_rubber"),
        Component(id="esp32",        name="ESP32-S3 main controller",
                  quantity=1, cost_per_unit=14.0, mass_kg=0.02,
                  lead_time_days=3),
        Component(id="battery",      name="ATLAS-CELL-V1 power pack (4S2P)",
                  quantity=1, cost_per_unit=120.0, mass_kg=0.55,
                  lead_time_days=10, twin_ref="ATLAS-CELL-V1"),
        Component(id="solar_panel",  name="5 W flexible solar panel",
                  quantity=1, cost_per_unit=22.0, mass_kg=0.10,
                  lead_time_days=7),
        Component(id="bms",          name="4S BMS + balancer",
                  quantity=1, cost_per_unit=12.0, mass_kg=0.04,
                  lead_time_days=5),
        Component(id="nir_sensor",   name="NIR mini-spectrometer (AS7263)",
                  quantity=1, cost_per_unit=35.0, mass_kg=0.02,
                  lead_time_days=14,
                  notes="Used for leaf-health + soil-moisture scans."),
        Component(id="cam",          name="OV2640 wide-angle camera",
                  quantity=1, cost_per_unit=9.0,  mass_kg=0.01,
                  lead_time_days=3),
        Component(id="water_pump",   name="12 V mini peristaltic pump",
                  quantity=1, cost_per_unit=18.0, mass_kg=0.15,
                  lead_time_days=5),
        Component(id="water_tank",   name="1 L food-grade tank",
                  quantity=1, cost_per_unit=6.0,  mass_kg=0.10,
                  lead_time_days=2),
        Component(id="nozzle",       name="3D-printed nozzle + flow valve",
                  quantity=1, cost_per_unit=4.0,  mass_kg=0.05,
                  lead_time_days=2),
        Component(id="harness",      name="Wiring harness + connectors",
                  quantity=1, cost_per_unit=11.0, mass_kg=0.10,
                  lead_time_days=2),
    ]

    deps = [
        Dependency(from_component="drive_motors", to_component="motor_drivers", kind="powered_by"),
        Dependency(from_component="motor_drivers", to_component="esp32", kind="controlled_by"),
        Dependency(from_component="motor_drivers", to_component="battery", kind="powered_by"),
        Dependency(from_component="esp32", to_component="battery", kind="powered_by"),
        Dependency(from_component="esp32", to_component="bms", kind="monitored_by"),
        Dependency(from_component="solar_panel", to_component="bms", kind="charges"),
        Dependency(from_component="solar_panel", to_component="battery", kind="charges"),
        Dependency(from_component="nir_sensor", to_component="esp32", kind="read_by"),
        Dependency(from_component="cam", to_component="esp32", kind="read_by"),
        Dependency(from_component="water_pump", to_component="esp32", kind="controlled_by"),
        Dependency(from_component="water_pump", to_component="battery", kind="powered_by"),
        Dependency(from_component="nozzle", to_component="water_pump", kind="connected_to"),
        Dependency(from_component="nozzle", to_component="water_tank", kind="connected_to"),
        Dependency(from_component="harness", to_component="frame", kind="mounted_on"),
        Dependency(from_component="wheels", to_component="drive_motors", kind="mounted_on"),
        Dependency(from_component="drive_motors", to_component="frame", kind="mounted_on"),
    ]

    state = TwinState(
        status=TwinStatus.SPEC,
        components=components,
        materials=["aluminium_6061", "abs_plastic", "foam_rubber",
                   "lithium_iron_phosphate", "monocrystalline_silicon"],
        dimensions=Dimensions(length_m=0.60, width_m=0.40, height_m=0.25, mass_kg=4.6),
        energy=EnergyProfile(
            peak_w=120.0, average_w=24.0, daily_wh=200.0,
            source="battery+solar",
        ),
        dependencies=deps,
        sensor_inputs=[
            SensorInput(name="NIR 6-band reflectance", kind="optical",
                        unit="counts", min_value=0.0, max_value=65535.0),
            SensorInput(name="Leaf RGB image", kind="optical",
                        unit="pixels"),
            SensorInput(name="Capacitive soil-moisture", kind="moisture",
                        unit="pct", min_value=0.0, max_value=100.0),
            SensorInput(name="Pack voltage", kind="voltage",
                        unit="V", min_value=10.0, max_value=17.0),
        ],
        outputs=[
            TwinOutput(name="4-wheel PWM duty", kind="motion",
                       unit="0-255", description="Per-wheel motor command."),
            TwinOutput(name="Water pump duty", kind="motion",
                       unit="0-1", description="0=off, 1=on at 100% flow."),
            TwinOutput(name="NIR + image leaf-health score", kind="data",
                       unit="0-1", description="From on-board model."),
        ],
        integrations={
            "deployment_environment": "outdoor_terrain",
            "needs": {
                "gravity_m_s2": 9.81,
                "min_o2_pct": 18.0,
                "temp_c_range": [-5.0, 40.0],
            },
            "footprint_m": [0.60, 0.40, 0.25],
        },
    )

    return DigitalTwin(
        name="AGRI-ROVER-01",
        category=TwinCategory.ROBOT,
        owner_agent="ajani",
        description=(
            "Reference Green Robot · autonomous garden/farm rover. Uses the "
            "ATLAS NIR scanner + RGB camera to identify plant stress, then "
            "drives over and dispenses water from the on-board reservoir. "
            "Solar-trickle charged. Talks to the ATLAS backend through an "
            "ESP32-S3 node using the existing Phase 7 robot stack."
        ),
        tags=["green_robot", "agri", "rover", "reference", "d5"],
        state=state,
    )


# ===========================================================================
# D6 — Power Cell · ATLAS-CELL-V1 (Li-ion) + ATLAS-CELL-SS-V1 (Solid-state)
# ===========================================================================
def _build_power_cell_liion() -> DigitalTwin:
    components: List[Component] = [
        Component(id="anode",   name="Graphite anode foil",
                  quantity=1, cost_per_unit=2.40, mass_kg=0.012,
                  lead_time_days=10, material="graphite"),
        Component(id="cathode", name="LFP (LiFePO₄) cathode",
                  quantity=1, cost_per_unit=4.80, mass_kg=0.016,
                  lead_time_days=14, material="lithium_iron_phosphate"),
        Component(id="separator", name="Polyolefin separator 16 µm",
                  quantity=1, cost_per_unit=0.50, mass_kg=0.001,
                  lead_time_days=7, material="polyolefin"),
        Component(id="electrolyte", name="LiPF6 in EC/DMC electrolyte",
                  quantity=1, cost_per_unit=1.20, mass_kg=0.006,
                  lead_time_days=5),
        Component(id="can",     name="Steel cylindrical can 18650",
                  quantity=1, cost_per_unit=0.30, mass_kg=0.008,
                  lead_time_days=3, material="stainless_steel"),
        Component(id="terminal", name="Nickel-plated terminal cap",
                  quantity=2, cost_per_unit=0.10, mass_kg=0.001,
                  lead_time_days=2),
        Component(id="vent",    name="Pressure-relief vent disc",
                  quantity=1, cost_per_unit=0.20, mass_kg=0.001,
                  lead_time_days=3),
    ]
    deps = [
        Dependency(from_component="electrolyte", to_component="separator", kind="impregnates"),
        Dependency(from_component="separator", to_component="anode", kind="between"),
        Dependency(from_component="separator", to_component="cathode", kind="between"),
        Dependency(from_component="anode", to_component="can", kind="contained_in"),
        Dependency(from_component="cathode", to_component="can", kind="contained_in"),
        Dependency(from_component="vent", to_component="can", kind="mounted_on"),
        Dependency(from_component="terminal", to_component="can", kind="mounted_on"),
    ]

    state = TwinState(
        status=TwinStatus.SPEC,
        components=components,
        materials=["graphite", "lithium_iron_phosphate", "polyolefin",
                   "carbonate_solvent", "stainless_steel"],
        dimensions=Dimensions(length_m=0.065, width_m=0.018, height_m=0.018, mass_kg=0.046),
        energy=EnergyProfile(
            peak_w=32.0, average_w=6.4, daily_wh=9.6,
            source="electrochemical",
        ),
        dependencies=deps,
        sensor_inputs=[
            SensorInput(name="Cell voltage", kind="voltage",
                        unit="V", min_value=2.5, max_value=3.65),
            SensorInput(name="Cell surface temperature", kind="temperature",
                        unit="C", min_value=-20.0, max_value=120.0),
        ],
        outputs=[],
        integrations={
            "thermal": {                       # consumed by _sim_thermal
                "chemistry": "li_ion",
                "I_amps": 3.0,
                "R_int_ohm": 0.04,
                "m_kg": 0.046,
                "Cp_j_kg_k": 900.0,
                "h_w_m2_k": 15.0,
                "A_m2": 0.0042,
                "T_amb_c": 25.0,
                "T_init_c": 25.0,
                "thermal_runaway_threshold_c": 80.0,
                "duration_s": 1800,
            },
            "needs": {
                "temp_c_range": [-20.0, 60.0],
            },
        },
    )

    return DigitalTwin(
        name="ATLAS-CELL-V1",
        category=TwinCategory.POWER_SYSTEM,
        owner_agent="minerva",
        description=(
            "Reference Li-ion (LFP) 18650 power cell. 3 Ah · 3.2 V. "
            "Used as the building block of AGRI-ROVER-01's 4S2P pack. "
            "THERMAL sim modelled by lumped-mass ODE in twin_simulator."
        ),
        tags=["power_cell", "li_ion", "lfp", "reference", "d6"],
        state=state,
    )


def _build_power_cell_solid_state() -> DigitalTwin:
    """Solid-state variant — same form factor, different chemistry."""
    components: List[Component] = [
        Component(id="anode",   name="Lithium-metal anode",
                  quantity=1, cost_per_unit=8.0, mass_kg=0.008,
                  lead_time_days=30, material="lithium_metal"),
        Component(id="cathode", name="NMC cathode (Ni-rich)",
                  quantity=1, cost_per_unit=6.5, mass_kg=0.018,
                  lead_time_days=21, material="nickel_manganese_cobalt"),
        Component(id="electrolyte", name="Sulfide solid electrolyte (Li₆PS₅Cl)",
                  quantity=1, cost_per_unit=12.0, mass_kg=0.005,
                  lead_time_days=45,
                  notes="Ionic conductivity ~10⁻³ S/cm at 25 °C."),
        Component(id="cell_stack", name="Bipolar cell-stack housing",
                  quantity=1, cost_per_unit=2.5, mass_kg=0.012,
                  lead_time_days=10),
        Component(id="terminals", name="Tabs + terminal pair",
                  quantity=2, cost_per_unit=0.30, mass_kg=0.001,
                  lead_time_days=3),
    ]
    deps = [
        Dependency(from_component="electrolyte", to_component="anode", kind="between"),
        Dependency(from_component="electrolyte", to_component="cathode", kind="between"),
        Dependency(from_component="anode", to_component="cell_stack", kind="contained_in"),
        Dependency(from_component="cathode", to_component="cell_stack", kind="contained_in"),
        Dependency(from_component="terminals", to_component="cell_stack", kind="mounted_on"),
    ]

    state = TwinState(
        status=TwinStatus.SPEC,
        components=components,
        materials=["lithium_metal", "nickel_manganese_cobalt",
                   "sulfide_solid_electrolyte", "stainless_steel"],
        dimensions=Dimensions(length_m=0.065, width_m=0.018, height_m=0.018, mass_kg=0.044),
        energy=EnergyProfile(
            peak_w=55.5, average_w=11.0, daily_wh=14.8,
            source="electrochemical",
        ),
        dependencies=deps,
        sensor_inputs=[
            SensorInput(name="Cell voltage", kind="voltage",
                        unit="V", min_value=2.8, max_value=4.3),
            SensorInput(name="Cell surface temperature", kind="temperature",
                        unit="C", min_value=-20.0, max_value=150.0),
        ],
        outputs=[],
        integrations={
            "thermal": {
                "chemistry": "solid_state",
                "I_amps": 3.0,
                "R_int_ohm": 0.025,
                "m_kg": 0.044,
                "Cp_j_kg_k": 850.0,
                "h_w_m2_k": 15.0,
                "A_m2": 0.0042,
                "T_amb_c": 25.0,
                "T_init_c": 25.0,
                "thermal_runaway_threshold_c": 100.0,
                "duration_s": 1800,
            },
            "needs": {
                "temp_c_range": [-30.0, 80.0],
            },
        },
    )

    return DigitalTwin(
        name="ATLAS-CELL-SS-V1",
        category=TwinCategory.POWER_SYSTEM,
        owner_agent="minerva",
        description=(
            "Reference solid-state Li-metal power cell. Higher energy "
            "density (14.8 Wh vs 9.6 Wh same form factor) and ~25 % less "
            "internal resistance than the LFP V1 — but supply chain is "
            "still 45-day lead time. Runs the THERMAL ODE engine with "
            "chemistry='solid_state' and a 100 °C runaway threshold."
        ),
        tags=["power_cell", "solid_state", "lithium_metal", "reference", "d6"],
        state=state,
    )


# ===========================================================================
# Seeding
# ===========================================================================
SEED_BUILDERS = [_build_agri_rover, _build_power_cell_liion, _build_power_cell_solid_state]


async def seed_if_needed() -> Dict[str, Any]:
    inserted_twins: List[str] = []
    inserted_blueprints: List[str] = []
    for build in SEED_BUILDERS:
        twin = build()
        if await _twins().find_one({"name": twin.name}):
            continue
        await _twins().insert_one(twin.model_dump().copy())
        inserted_twins.append(twin.name)

        # Also emit a project-blueprint stub
        bp = {
            "id": twin.id + "-bp",
            "title": f"{twin.name} reference blueprint",
            "summary": (twin.description or "")[:400],
            "agent": twin.owner_agent,
            "kind": "reference_twin",
            "twin_id": twin.id,
            "components": [c.model_dump() for c in twin.state.components],
            "tags": twin.tags + ["reference_blueprint"],
            "status": "ready",
            "created_at": twin.created_at,
        }
        await _blueprints().insert_one(bp)
        inserted_blueprints.append(bp["title"])

        try:
            await mb.auto_store(
                f"REFERENCE TWIN seeded · {twin.name} ({twin.category.value})\n"
                f"{(twin.description or '')[:400]}",
                persona=twin.owner_agent, category="project",
                source_type="reference_twin", source_id=twin.id,
                tags=twin.tags + ["reference"],
            )
        except Exception as exc:    # noqa: BLE001
            logger.warning("MB write for %s failed: %s", twin.name, exc)
    return {
        "inserted_twins": inserted_twins,
        "inserted_blueprints": inserted_blueprints,
    }
