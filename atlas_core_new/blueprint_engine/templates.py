from __future__ import annotations
from typing import Dict, Callable
from datetime import datetime
import uuid

from .schemas import (
    BlueprintPacket, Requirement, MaterialSpec, ComponentSpec,
    ToolSpec, FailureMode, ModuleBlock, BuildStep, ProjectDomain, SafetyTier,
)


def new_id() -> str:
    return str(uuid.uuid4())


def base_packet(title: str, domain: ProjectDomain, safety: SafetyTier, version: str, objective: str) -> BlueprintPacket:
    return BlueprintPacket(
        blueprint_id=new_id(),
        version=version,
        title=title,
        domain=domain,
        safety_tier=safety,
        created_at=datetime.utcnow().isoformat() + "Z",
        objective=objective,
    )


def template_green_bot(version: str, constraints: Dict[str, str]) -> BlueprintPacket:
    p = base_packet(
        "GREEN BOT — Eco Terraform Rover (Mark I)",
        "ROBOTICS",
        "MEDIUM",
        version,
        "Autonomous biomimetic quadruped rover to scan soil/air, aerate terrain, and disperse seeds for ecosystem restoration."
    )
    p.assumptions = [
        "Prototype is non-weaponized. Any defensive behavior is passive: avoidance + retreat.",
        "Mark I focuses on slow, stable walking; no jumping or high-speed running.",
        "Field testing starts in controlled outdoor area (flat terrain) before rough terrain.",
    ]
    p.requirements = [
        Requirement(id="R1", statement="Walk on uneven terrain without tipping.", metric="static stability margin", target=">= 10%"),
        Requirement(id="R2", statement="Operate continuously on one power module.", metric="runtime", target=constraints.get("runtime", ">= 60 minutes")),
        Requirement(id="R3", statement="Collect and log environmental data.", metric="sensors", target="pH, moisture, temp, PM2.5, GPS"),
        Requirement(id="R4", statement="Perform soil aeration and seed dispersal.", metric="tool functions", target="aerate + distribute seeds"),
    ]
    p.architecture = [
        ModuleBlock(
            name="STRUCTURE_FRAME",
            purpose="Load-bearing chassis with joint mounts and service panels.",
            inputs=["mechanical loads", "terrain impact"],
            outputs=["rigid body", "mount points"],
            components=[ComponentSpec(name="CNC-cut plates + fasteners", qty=1, role="chassis structure")]
        ),
        ModuleBlock(
            name="MOBILITY_SYSTEM",
            purpose="Quadruped legs with joint actuation and compliance.",
            inputs=["control commands", "power"],
            outputs=["locomotion"],
            components=[
                ComponentSpec(name="BLDC Motor", qty=12, role="joint actuation", notes="3 per leg (hip pitch/roll, knee)"),
                ComponentSpec(name="Motor Controller (ESC/FOC)", qty=12, role="motor control"),
                ComponentSpec(name="IMU (9-axis)", qty=1, role="stability sensing"),
            ]
        ),
        ModuleBlock(
            name="SENSING_SYSTEM",
            purpose="Environmental and navigation sensing.",
            inputs=["world"],
            outputs=["maps + soil readings"],
            components=[
                ComponentSpec(name="LiDAR", qty=1, role="navigation scanning"),
                ComponentSpec(name="RGB Camera", qty=1, role="vision"),
                ComponentSpec(name="Soil pH Sensor", qty=1, role="soil chemistry"),
                ComponentSpec(name="Soil Moisture Sensor", qty=1, role="soil moisture"),
            ]
        ),
        ModuleBlock(
            name="ECO_TOOLING",
            purpose="Soil aeration + seed dispersal attachments.",
            inputs=["actuation + commands"],
            outputs=["aerated soil + seeds distributed"],
            components=[
                ComponentSpec(name="Soil Aerator Drill", qty=1, role="terrain aeration"),
                ComponentSpec(name="Seed Dispersal Hopper", qty=1, role="seed distribution"),
            ]
        ),
        ModuleBlock(
            name="CONTROL_COMPUTE",
            purpose="Onboard compute for perception, planning, and safety rules.",
            inputs=["sensor data"],
            outputs=["motor commands"],
            components=[
                ComponentSpec(name="Microcontroller (STM32/ESP32)", qty=1, role="real-time control"),
                ComponentSpec(name="SBC (Jetson/RPi)", qty=1, role="perception/planning"),
            ]
        ),
    ]
    p.materials = [
        MaterialSpec(name="7075-T6 Aluminum", use="Primary leg brackets + load plates", justification="Strong and machineable for prototype"),
        MaterialSpec(name="CFRP (Carbon Fiber Reinforced Polymer)", use="Lightweight leg segments", justification="Weight reduction while staying stiff"),
        MaterialSpec(name="TPU (Thermoplastic Polyurethane)", use="Joint covers + cable strain relief", justification="Flexible abrasion resistance"),
        MaterialSpec(name="Copper (C110)", use="Power bus bars (optional)", justification="Low resistance power distribution"),
    ]
    p.components = [
        ComponentSpec(name="LiFePO4 Battery Cells", qty=1, role="power module", notes="Swappable pack preferred for field testing"),
    ]
    p.tools = [
        ToolSpec(name="CNC Mill", purpose="Machine brackets, mounts, chassis plates"),
        ToolSpec(name="3D Printer (FDM)", purpose="Prototype covers, cable guides, sensor mounts"),
        ToolSpec(name="Soldering Station", purpose="Wire harness + power distribution"),
        ToolSpec(name="Multimeter + Oscilloscope", purpose="Debug motor controllers and sensors"),
        ToolSpec(name="Calipers/Micrometer", purpose="Verify tolerances and fit"),
    ]
    p.power_flow = [
        "Battery Pack (LiFePO4) -> Main Fuse -> DC Bus",
        "DC Bus -> Motor Controllers (FOC) -> BLDC Motors",
        "DC Bus -> SBC + Microcontroller -> Sensors",
        "DC Bus -> Tooling Actuator (drill/hopper) -> Mechanism",
    ]
    p.control_logic = [
        "Sensor fusion: IMU + joint encoders + LiDAR for pose + obstacle map",
        "Gait planner: slow crawl gait (4-point stability) as default",
        "Terrain safety: if slope > threshold -> stop + reroute",
        "Non-lethal safety charter: avoid humans/animals; retreat; never chase",
        "Failsafe: if comms lost or battery low -> safe shutdown pose",
    ]
    p.fabrication_steps = [
        BuildStep(step=1, title="Frame + service layout",
            instructions=["Cut chassis plates (CNC or laser).", "Assemble with fasteners; add removable service panels.", "Install cable routing channels and strain relief points."],
            verification=["Chassis is square; mounting holes align; panels remove easily."]),
        BuildStep(step=2, title="Leg modules (one leg first)",
            instructions=["Assemble one leg segment stack: hip bracket -> knee bracket -> foot pad.", "Mount motors and motor controllers with heat paths (metal contact or heatsink).", "Route cables with TPU guides."],
            verification=["Leg moves through full range without binding; no cable pinch points."]),
        BuildStep(step=3, title="Sensors + compute bring-up",
            instructions=["Mount IMU near center-of-mass.", "Mount LiDAR and camera on vibration-isolated plate.", "Bring up microcontroller first, then SBC."],
            verification=["IMU stable readings; LiDAR scan visible; camera stream stable."]),
        BuildStep(step=4, title="Eco tooling attachments",
            instructions=["Install aeration drill assembly (low RPM, high torque).", "Install seed hopper with controlled gate (servo/actuator)."],
            verification=["Drill spins under load without stalling; hopper dispenses repeatable amount."]),
    ]
    p.test_plan = [
        "Bench test motor torque + thermal behavior at low speed",
        "Static stability test on angled platform",
        "Slow walk test on flat ground (5m loops)",
        "Obstacle avoidance test with LiDAR map",
        "Soil sensor calibration and logging",
        "Tooling functional test: aeration depth + seed dispersion pattern",
    ]
    p.failure_modes = [
        FailureMode(mode="Motor overheating", cause="FOC tuning or overload", effect="stall/shutdown", mitigation="current limit + heatsink + duty cycle", severity="HIGH"),
        FailureMode(mode="Tip-over", cause="unstable gait or slope", effect="damage", mitigation="crawl gait + slope detection + wider stance", severity="HIGH"),
        FailureMode(mode="Sensor blindness (dust/rain)", cause="environment", effect="bad navigation", mitigation="sensor covers + redundancy + slow mode", severity="MED"),
        FailureMode(mode="Cable snag", cause="poor routing", effect="disconnect", mitigation="strain relief + protective sleeves", severity="MED"),
    ]
    return p


def template_medusa_arms(version: str, constraints: Dict[str, str]) -> BlueprintPacket:
    p = base_packet(
        "MEDUSA ARMS — Modular Tentacle Manipulators (Mark I)",
        "ROBOTICS",
        "MEDIUM",
        version,
        "Sleek, soft-sheathed, segmented manipulator arms with distributed control for smooth, fluid motion and compact concealment."
    )
    p.assumptions = [
        "Mark I is a benchtop demo arm (1-2 tentacles), not a wearable system yet.",
        "Soft sheath is cosmetic + safety; internal structure carries load.",
        "No autonomous weaponization; manipulation only (pick/place, reach, hold).",
    ]
    p.requirements = [
        Requirement(id="R1", statement="Smooth multi-axis bend without kinks.", metric="min bend radius", target=constraints.get("bend_radius", ">= 40mm")),
        Requirement(id="R2", statement="Carry light payload at the tip.", metric="payload", target=constraints.get("payload", ">= 0.5kg")),
        Requirement(id="R3", statement="Segment-level control for fluid motion.", metric="segments", target=constraints.get("segments", "8-12")),
    ]
    p.architecture = [
        ModuleBlock(name="SEGMENT_SPINE", purpose="Internal segmented backbone for controlled bending.",
            components=[ComponentSpec(name="Linear Actuator", qty=4, role="tendon drive", notes="simpler Mark I approach")]),
        ModuleBlock(name="SOFT_SHEATH", purpose="Silicone/TPU outer skin for safe touch + aesthetics.",
            components=[ComponentSpec(name="Silicone Elastomer (Shore A 20-50)", qty=1, role="outer skin")]),
        ModuleBlock(name="DISTRIBUTED_CONTROL", purpose="Segment controller nodes for smooth motion.",
            components=[ComponentSpec(name="Microcontroller (STM32/ESP32)", qty=2, role="control nodes")]),
        ModuleBlock(name="END_EFFECTOR", purpose="Interchangeable gripper/suction/pad.",
            components=[ComponentSpec(name="3D printed gripper", qty=1, role="manipulation")]),
    ]
    p.materials = [
        MaterialSpec(name="CFRP (Carbon Fiber Reinforced Polymer)", use="lightweight spine plates", justification="stiff but light"),
        MaterialSpec(name="Silicone Elastomer (Shore A 20-50)", use="outer sheath", justification="soft-touch + safety"),
        MaterialSpec(name="Kevlar Fabric", use="internal reinforcement wrap (optional)", justification="tear resistance"),
    ]
    p.tools = [
        ToolSpec(name="3D Printer (SLA)", purpose="High-detail segment molds or spine parts"),
        ToolSpec(name="Soldering Station", purpose="Control boards and wiring"),
        ToolSpec(name="Calipers/Micrometer", purpose="Segment tolerance checks"),
    ]
    p.power_flow = [
        "Battery/DC supply -> Controller bus -> Segment actuators",
        "Controller bus -> sensors (optional encoders) -> motion feedback",
    ]
    p.control_logic = [
        "Segment interpolation: smooth spline-based bend commands",
        "Safety: torque/current limits to prevent pinches",
        "Calibration: home each segment; store offsets",
    ]
    p.fabrication_steps = [
        BuildStep(step=1, title="Build 1 segment prototype",
            instructions=["Print/machine one segment", "Fit actuator/tendon routing", "Test bend range"],
            verification=["No binding; consistent bend; cables not pinched"]),
        BuildStep(step=2, title="Scale to 8-12 segments",
            instructions=["Repeat segment build", "Add distributed control nodes", "Add outer sheath"],
            verification=["Uniform motion across segments; stable control"]),
    ]
    p.test_plan = [
        "Bend repeatability test (100 cycles)",
        "Payload test at tip",
        "Thermal test for actuators",
        "Sheath durability test (abrasion + tear)",
    ]
    p.failure_modes = [
        FailureMode(mode="Segment binding", cause="tolerance stackup", effect="jerky motion", mitigation="shim + reprint + better alignment pins", severity="MED"),
        FailureMode(mode="Sheath tearing", cause="stress concentration", effect="damage", mitigation="reinforcement mesh + thicker radii", severity="MED"),
        FailureMode(mode="Overcurrent", cause="payload overload", effect="shutdown", mitigation="current limit + mechanical clutch", severity="HIGH"),
    ]
    return p


def template_metal_flowers(version: str, constraints: Dict[str, str]) -> BlueprintPacket:
    p = base_packet(
        "METAL FLOWERS — Deployable Geo-Seed Sculptures (Mark I)",
        "MATERIALS",
        "LOW",
        version,
        "Geometrically precise deployable 'petal' structure that opens/closes to protect a seed capsule and act as a micro-habitat marker."
    )
    p.assumptions = [
        "Mark I is a passive mechanical sculpture + seed capsule holder (no bioengineering).",
        "Acts as a protective casing + marker; seeding is conventional (real seeds).",
    ]
    p.requirements = [
        Requirement(id="R1", statement="Repeatable petal deploy mechanism.", metric="cycles", target=">= 500 open/close cycles"),
        Requirement(id="R2", statement="Weather resistance.", metric="exposure", target="rain + dust + UV"),
    ]
    p.architecture = [
        ModuleBlock(name="PETAL_MECHANISM", purpose="Hinged petals with cam ring actuator",
            components=[ComponentSpec(name="Cam ring + hinge pins", qty=1, role="deployment mechanism")]),
        ModuleBlock(name="SEED_CAPSULE", purpose="Protected seed container with drainage",
            components=[ComponentSpec(name="Seed capsule insert", qty=1, role="holds seeds")]),
    ]
    p.materials = [
        MaterialSpec(name="6061-T6 Aluminum", use="petals + core hub", justification="easy machining + corrosion resistance"),
        MaterialSpec(name="Stainless Steel 304", use="hinge pins", justification="wear resistance"),
        MaterialSpec(name="TPU (Thermoplastic Polyurethane)", use="gaskets", justification="water/dust seal"),
    ]
    p.tools = [
        ToolSpec(name="Laser Cutter", purpose="Cut petals from sheet stock"),
        ToolSpec(name="CNC Mill", purpose="Machine core hub and cam ring"),
        ToolSpec(name="Torque Wrench Set", purpose="consistent assembly torque"),
    ]
    p.fabrication_steps = [
        BuildStep(step=1, title="Cut petals + hinge prep",
            instructions=["Laser cut petals", "Deburr edges", "Drill hinge holes"],
            verification=["Holes align; petals move freely"]),
        BuildStep(step=2, title="Machine hub + cam ring",
            instructions=["CNC hub", "CNC cam ring", "Fit petals to ring"],
            verification=["Ring actuates petals smoothly"]),
    ]
    p.test_plan = [
        "Cycle test open/close",
        "Dust ingress test",
        "Rain spray test",
        "UV exposure test (accelerated if possible)",
    ]
    p.failure_modes = [
        FailureMode(mode="Hinge wear", cause="friction + grit", effect="stiff motion", mitigation="bushings + seals", severity="MED"),
        FailureMode(mode="Corrosion", cause="environment", effect="seizing", mitigation="anodize + stainless pins", severity="LOW"),
    ]
    return p


def template_hydrogen_power(version: str, constraints: Dict[str, str]) -> BlueprintPacket:
    p = base_packet(
        "HYDROGEN POWER MODULE — PEM Fuel Cell Pack (Mark I)",
        "ENERGY",
        "HIGH",
        version,
        "Portable PEM fuel cell power module for clean electrical output, designed with leak detection and strict safety controls."
    )
    p.assumptions = [
        "This is a POWER module concept packet; real build requires safety compliance and trained handling.",
        "Start with off-the-shelf certified components whenever possible.",
    ]
    p.requirements = [
        Requirement(id="R1", statement="Provide stable DC output for robotics load.", metric="output", target=constraints.get("output", "24V DC @ 500W")),
        Requirement(id="R2", statement="Detect and respond to hydrogen leaks.", metric="safety", target="auto shutdown on leak"),
        Requirement(id="R3", statement="Thermal management for stack.", metric="temp", target="within manufacturer spec"),
    ]
    p.architecture = [
        ModuleBlock(name="H2_STORAGE", purpose="Hydrogen storage and regulation",
            components=[ComponentSpec(name="Regulator + valves (certified)", qty=1, role="pressure regulation")]),
        ModuleBlock(name="FUEL_CELL_STACK", purpose="PEM stack produces power",
            components=[ComponentSpec(name="PEM Fuel Cell Stack", qty=1, role="power generation")]),
        ModuleBlock(name="POWER_ELECTRONICS", purpose="DC regulation + protection",
            components=[ComponentSpec(name="DC-DC Converter (isolated)", qty=1, role="regulation")]),
        ModuleBlock(name="SAFETY_LAYER", purpose="Leak detect + shutdown + venting logic",
            components=[ComponentSpec(name="Hydrogen sensor (certified)", qty=2, role="leak detection")]),
    ]
    p.materials = [
        MaterialSpec(name="Stainless Steel 304", use="gas fittings + mounts", justification="corrosion resistance"),
        MaterialSpec(name="Copper (C110)", use="power bus", justification="low resistance"),
    ]
    p.tools = [
        ToolSpec(name="Multimeter + Oscilloscope", purpose="power output verification"),
        ToolSpec(name="Torque Wrench Set", purpose="safe fitting torque"),
    ]
    p.power_flow = [
        "Hydrogen -> Regulator -> PEM Stack",
        "PEM Stack DC -> DC protection -> DC-DC regulation -> Load",
        "Sensors -> Safety controller -> Valve shutdown on fault",
    ]
    p.control_logic = [
        "Continuous H2 sensor monitoring; if above threshold -> close valve + alarm",
        "Temperature monitoring; if above spec -> reduce load or shutdown",
        "Voltage regulation with overcurrent protection",
    ]
    p.fabrication_steps = [
        BuildStep(step=1, title="Use certified stack + fittings",
            instructions=["Select certified PEM stack and certified fittings", "Mount in ventilated enclosure", "Wire safety controller"],
            verification=["No leaks during test; stable voltage under load"]),
    ]
    p.test_plan = [
        "Leak test procedure (sensor + soap solution + ventilation)",
        "Load step test (0%->50%->100%)",
        "Thermal test at sustained load",
        "Emergency shutdown test",
    ]
    p.failure_modes = [
        FailureMode(mode="Hydrogen leak", cause="fitting failure", effect="fire risk", mitigation="certified fittings + sensors + auto shutoff + ventilation", severity="HIGH"),
        FailureMode(mode="Stack overheating", cause="poor cooling", effect="damage", mitigation="active cooling + derating", severity="HIGH"),
    ]
    return p


def template_morphing_structures(version: str, constraints: Dict[str, str]) -> BlueprintPacket:
    p = base_packet(
        "MORPHING STRUCTURES — Compliant + Smart Material Demo (Mark I)",
        "MATERIALS",
        "MEDIUM",
        version,
        "Shape-changing structure demo using compliant mechanisms + smart materials for controlled geometry changes."
    )
    p.assumptions = [
        "Mark I is a tabletop demo (beam/panel) not a flight-critical structure.",
        "Use off-the-shelf actuators and safe voltages for early prototypes.",
    ]
    p.requirements = [
        Requirement(id="R1", statement="Achieve two stable shapes.", metric="shape states", target="State A + State B"),
        Requirement(id="R2", statement="Repeatable morph without cracking.", metric="cycles", target=">= 1000 cycles"),
    ]
    p.architecture = [
        ModuleBlock(name="COMPLIANT_FRAME", purpose="Flexure-based structure",
            components=[ComponentSpec(name="Kirigami/origami cut panel", qty=1, role="morphing geometry")]),
        ModuleBlock(name="ACTUATION", purpose="Drives shape change",
            components=[ComponentSpec(name="Linear Actuator", qty=2, role="pull/push morph")]),
        ModuleBlock(name="CONTROL", purpose="Control morph profile",
            components=[ComponentSpec(name="Microcontroller (STM32/ESP32)", qty=1, role="actuator control")]),
    ]
    p.materials = [
        MaterialSpec(name="GFRP (Glass Fiber Reinforced Polymer)", use="flex panel", justification="durable, forgiving for prototypes"),
        MaterialSpec(name="TPU (Thermoplastic Polyurethane)", use="flex joints or hinges", justification="compliance"),
    ]
    p.tools = [
        ToolSpec(name="Laser Cutter", purpose="cut kirigami patterns"),
        ToolSpec(name="3D Printer (FDM)", purpose="actuator mounts"),
    ]
    p.control_logic = [
        "Morph profile: slow ramp to reduce stress concentration",
        "End-stop detection to avoid over-travel",
    ]
    p.fabrication_steps = [
        BuildStep(step=1, title="Cut compliant panel pattern",
            instructions=["Laser cut kirigami/origami pattern", "Deburr edges"],
            verification=["No micro-cracks; clean cuts"]),
        BuildStep(step=2, title="Mount actuators and run morph cycles",
            instructions=["Attach actuators with adjustable mounts", "Run low-speed morph cycles"],
            verification=["Repeatable shape change; no delamination"]),
    ]
    p.test_plan = [
        "Cycle test 1000 morphs",
        "Measure deflection and repeatability",
        "Inspect for cracks/delamination",
    ]
    p.failure_modes = [
        FailureMode(mode="Cracking at cut corners", cause="stress concentration", effect="failure", mitigation="round cut corners + slower ramp", severity="MED"),
        FailureMode(mode="Delamination", cause="poor composite layup", effect="loss of strength", mitigation="better layup + edge sealing", severity="MED"),
    ]
    return p


def template_atomic_ui(version: str, constraints: Dict[str, str]) -> BlueprintPacket:
    p = base_packet(
        "ATOMIC UI SYSTEM — Blueprint Viewer Components (v1)",
        "UI_SYSTEM",
        "LOW",
        version,
        "Atomic-design UI spec for rendering blueprint packets in your app with reusable components."
    )
    p.requirements = [
        Requirement(id="R1", statement="Render any BlueprintPacket consistently.", metric="coverage", target="all schema fields"),
        Requirement(id="R2", statement="Reusable UI components (Atomic Design).", metric="components", target="Atoms/Molecules/Organisms/Templates/Pages"),
    ]
    p.architecture = [
        ModuleBlock(name="ATOMS", purpose="Typography, buttons, chips, code blocks, section headers"),
        ModuleBlock(name="MOLECULES", purpose="List rows (materials, tools), metric cards, failure mode cards"),
        ModuleBlock(name="ORGANISMS", purpose="Blueprint sections: Requirements, Architecture, Build Steps, Failure Modes"),
        ModuleBlock(name="TEMPLATES", purpose="Blueprint layout grid + navigation"),
        ModuleBlock(name="PAGES", purpose="Blueprint detail page + export page"),
    ]
    p.fabrication_steps = [
        BuildStep(step=1, title="Create Atoms", instructions=["Define buttons, chips, headers, code block"], verification=["consistent styling"]),
        BuildStep(step=2, title="Create Molecules", instructions=["MaterialRow, ToolRow, FailureCard"], verification=["reusable props"]),
        BuildStep(step=3, title="Create Organisms", instructions=["RequirementsSection, ArchitectureSection, StepsSection"], verification=["renders any packet"]),
    ]
    p.failure_modes = [
        FailureMode(mode="UI inconsistency", cause="non-reusable components", effect="messy app", mitigation="enforce atomic design + tokens", severity="LOW"),
    ]
    return p


TEMPLATES: Dict[str, Callable] = {
    "GREEN_BOT": template_green_bot,
    "MEDUSA_ARMS": template_medusa_arms,
    "METAL_FLOWERS": template_metal_flowers,
    "HYDROGEN_POWER": template_hydrogen_power,
    "MORPHING_STRUCTURES": template_morphing_structures,
    "ATOMIC_UI": template_atomic_ui,
}
