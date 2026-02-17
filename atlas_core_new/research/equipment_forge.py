"""
Equipment Forge - Functional Output System

AIs don't just theorize—they produce functional projects and equipment.
Each research project can generate concrete deliverables:
- Build specifications with parts lists
- Schematic diagrams
- Step-by-step assembly instructions
- Testing protocols
- Downloadable files (specs, code, configs)

CORE RULE: All equipment follows the same safety principles.
AIs PROPOSE builds, user APPROVES before any physical construction.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class EquipmentStatus(str, Enum):
    CONCEPT = "concept"
    DESIGNING = "designing"
    SPEC_COMPLETE = "spec_complete"
    PARTS_LISTED = "parts_listed"
    READY_TO_BUILD = "ready_to_build"
    BUILDING = "building"
    TESTING = "testing"
    FUNCTIONAL = "functional"
    ARCHIVED = "archived"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    THEORETICAL = "theoretical"


@dataclass
class Part:
    """A component needed for the build"""
    name: str
    quantity: int
    source: str
    estimated_cost: str
    alternatives: List[str] = field(default_factory=list)
    notes: str = ""
    acquired: bool = False


@dataclass
class AssemblyStep:
    """One step in the build process"""
    step_number: int
    title: str
    description: str
    tools_needed: List[str]
    safety_notes: List[str]
    estimated_time: str
    checkpoint: str
    completed: bool = False


@dataclass
class TestProtocol:
    """How to verify the equipment works"""
    test_name: str
    purpose: str
    procedure: List[str]
    expected_result: str
    safety_precautions: List[str]
    pass_criteria: str
    result: Optional[str] = None
    passed: Optional[bool] = None


@dataclass
class Equipment:
    """A functional piece of equipment an AI can help build"""
    id: str
    name: str
    codename: str
    creator: str
    project_id: str
    description: str
    purpose: str
    status: EquipmentStatus
    difficulty: DifficultyLevel
    estimated_build_time: str
    estimated_cost: str
    parts: List[Part]
    assembly_steps: List[AssemblyStep]
    test_protocols: List[TestProtocol]
    safety_warnings: List[str]
    prerequisites: List[str]
    skills_required: List[str]
    downloadable_files: Dict[str, str]
    version: str = "1.0"
    last_updated: str = ""
    user_approved: bool = False


AJANI_EQUIPMENT = [
    Equipment(
        id="kinetic-harvester-v1",
        name="Kinetic Harvester Module",
        codename="PULSE-CELL",
        creator="ajani",
        project_id="kinetic-forge",
        description="A small-scale kinetic energy harvester that captures vibrations and converts them to stored electrical energy.",
        purpose="Proof-of-concept for the Kinetic Forge project. Powers small devices from ambient vibrations.",
        status=EquipmentStatus.SPEC_COMPLETE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        estimated_build_time="4-6 hours",
        estimated_cost="$50-80",
        parts=[
            Part("Piezoelectric discs (35mm)", 4, "Electronics supplier", "$12", ["Piezo buzzers can be repurposed"]),
            Part("Rectifier diodes (1N4007)", 8, "Electronics store", "$2", ["Any 1A rectifier works"]),
            Part("Capacitor bank (4700uF 16V)", 2, "Electronics store", "$5", []),
            Part("Voltage regulator (LM7805)", 1, "Electronics store", "$1", ["Buck converter for efficiency"]),
            Part("Copper wire (22 AWG)", 1, "Hardware store", "$8", []),
            Part("3D printed housing", 1, "Self-printed or ordered", "$10-20", ["Can use wood/metal enclosure"]),
            Part("LED indicator", 2, "Electronics store", "$1", []),
            Part("USB output port", 1, "Electronics store", "$3", []),
        ],
        assembly_steps=[
            AssemblyStep(1, "Prepare Piezo Array", "Wire 4 piezoelectric discs in series-parallel configuration for optimal voltage/current balance.", ["Soldering iron", "Multimeter", "Wire strippers"], ["Wear safety glasses when soldering", "Work in ventilated area"], "30 min", "Measure open-circuit voltage when tapped - should read 2-4V"),
            AssemblyStep(2, "Build Rectifier Bridge", "Create full-wave rectifier circuit to convert AC piezo output to DC.", ["Soldering iron", "Breadboard (optional)"], ["Double-check diode polarity"], "20 min", "DC output should be smooth when measured"),
            AssemblyStep(3, "Capacitor Storage", "Wire capacitor bank to store harvested energy.", ["Soldering iron"], ["Capacitors can discharge - handle carefully"], "15 min", "Capacitors should charge when piezo array is vibrated"),
            AssemblyStep(4, "Voltage Regulation", "Add voltage regulator to provide stable 5V USB output.", ["Soldering iron", "Heat sink"], ["Regulator can get hot - add heatsink"], "20 min", "Output should read steady 5V under light load"),
            AssemblyStep(5, "Housing Assembly", "Mount components in protective housing with vibration-absorbing base.", ["Screwdriver", "Hot glue gun"], ["Ensure no bare wires exposed"], "45 min", "All components secured, USB port accessible"),
            AssemblyStep(6, "Final Wiring", "Connect all subsystems and add LED indicators.", ["Soldering iron", "Multimeter"], ["Final continuity check before power"], "30 min", "LEDs light when energy harvested"),
        ],
        test_protocols=[
            TestProtocol("Vibration Response Test", "Verify energy harvesting from vibrations", ["Place on running washing machine", "Attach to bridge railing", "Mount on vehicle dashboard"], "LED indicator lights, capacitors charge", ["Secure mounting to prevent falls"], "Harvests measurable charge within 5 minutes"),
            TestProtocol("Output Stability Test", "Verify USB output is stable", ["Connect USB voltmeter", "Attach small load (LED strip)", "Monitor for 10 minutes"], "Steady 5V output, minimal fluctuation", ["Don't exceed 500mA draw"], "Voltage stays within 4.75-5.25V range"),
            TestProtocol("Endurance Test", "Verify long-term reliability", ["Run continuously for 24 hours", "Monitor temperature", "Check output periodically"], "No overheating, consistent performance", ["Check every few hours initially"], "No degradation over 24 hours"),
        ],
        safety_warnings=[
            "This is a low-voltage educational project - not for mains power",
            "Piezoelectric elements can produce voltage spikes - use protection circuits",
            "Capacitors store energy - discharge before working on circuit",
            "Not weatherproof without additional sealing",
        ],
        prerequisites=["Basic electronics knowledge", "Soldering experience", "Understanding of DC circuits"],
        skills_required=["Soldering", "Circuit assembly", "Basic troubleshooting"],
        downloadable_files={
            "schematic": "/equipment/ajani/pulse-cell/schematic.pdf",
            "parts_list": "/equipment/ajani/pulse-cell/parts.csv",
            "housing_stl": "/equipment/ajani/pulse-cell/housing.stl",
            "wiring_diagram": "/equipment/ajani/pulse-cell/wiring.png",
        },
        version="1.0",
        last_updated="2026-02-05",
    ),
    Equipment(
        id="resonance-detector-v1",
        name="Resonance Frequency Detector",
        codename="HARMONIC-EYE",
        creator="ajani",
        project_id="density-matrix",
        description="A handheld device that detects and displays the resonant frequency of materials.",
        purpose="Research tool for the Density Matrix project. Maps material resonance for future applications.",
        status=EquipmentStatus.DESIGNING,
        difficulty=DifficultyLevel.ADVANCED,
        estimated_build_time="8-12 hours",
        estimated_cost="$120-180",
        parts=[
            Part("Arduino Nano", 1, "Electronics supplier", "$15", ["ESP32 for wireless capability"]),
            Part("Piezoelectric sensor", 2, "Electronics supplier", "$20", []),
            Part("OLED display (128x64)", 1, "Electronics supplier", "$10", []),
            Part("Frequency counter module", 1, "Electronics supplier", "$15", []),
            Part("Op-amp (LM358)", 2, "Electronics store", "$3", []),
            Part("3D printed enclosure", 1, "Self-printed", "$15", []),
            Part("LiPo battery (3.7V 2000mAh)", 1, "Electronics supplier", "$12", []),
            Part("Charging module (TP4056)", 1, "Electronics store", "$2", []),
        ],
        assembly_steps=[
            AssemblyStep(1, "Sensor Preparation", "Configure piezoelectric sensors for frequency detection.", ["Soldering iron", "Multimeter"], ["Handle sensors carefully - fragile"], "45 min", "Sensors respond to taps with measurable signal"),
        ],
        test_protocols=[
            TestProtocol("Calibration Test", "Verify frequency accuracy", ["Use known tuning fork (440Hz)", "Compare to phone app", "Test multiple frequencies"], "Readings within 2% of known values", ["Use calibrated reference sources"], "Accuracy within 2% across 20Hz-20kHz range"),
        ],
        safety_warnings=[
            "LiPo batteries require proper handling - don't puncture or overcharge",
            "Keep away from strong magnetic fields",
        ],
        prerequisites=["Arduino programming", "Signal processing basics"],
        skills_required=["Soldering", "Arduino coding", "3D printing"],
        downloadable_files={
            "arduino_code": "/equipment/ajani/harmonic-eye/firmware.ino",
            "schematic": "/equipment/ajani/harmonic-eye/schematic.pdf",
        },
        version="0.5",
        last_updated="2026-02-05",
    ),
]

MINERVA_EQUIPMENT = [
    Equipment(
        id="gene-sequencer-edu-v1",
        name="Educational Gene Sequencer Kit",
        codename="HELIX-READER",
        creator="minerva",
        project_id="ancestral-code",
        description="A simplified gel electrophoresis setup for educational DNA analysis.",
        purpose="Teaching tool for the Ancestral Code project. Visualize DNA fragments.",
        status=EquipmentStatus.PARTS_LISTED,
        difficulty=DifficultyLevel.INTERMEDIATE,
        estimated_build_time="3-4 hours",
        estimated_cost="$80-120",
        parts=[
            Part("Gel casting tray", 1, "Science supplier", "$15", ["Can 3D print"]),
            Part("Agarose powder (50g)", 1, "Science supplier", "$20", []),
            Part("Power supply (adjustable DC)", 1, "Electronics store", "$25", ["Must reach 100V safely"]),
            Part("Platinum wire electrodes", 2, "Jewelry supplier", "$15", ["Stainless steel alternative"]),
            Part("UV LED array (365nm)", 1, "Electronics supplier", "$10", []),
            Part("Buffer solution materials", 1, "Science supplier", "$10", []),
            Part("Micropipettes", 1, "Science supplier", "$20", ["Adjustable 1-10μL"]),
            Part("DNA stain (safe alternative)", 1, "Science supplier", "$15", ["SYBR Safe recommended"]),
        ],
        assembly_steps=[
            AssemblyStep(1, "Gel Tray Construction", "Build or print the gel casting tray with comb.", ["3D printer or mold materials"], ["Ensure food-safe if 3D printing"], "60 min", "Tray holds water without leaking"),
            AssemblyStep(2, "Electrode Setup", "Install platinum wire electrodes at each end.", ["Wire cutters", "Silicone sealant"], ["Handle electrodes carefully"], "30 min", "Electrodes secure and parallel"),
            AssemblyStep(3, "Power Supply Wiring", "Connect adjustable power supply with safety switch.", ["Screwdriver", "Multimeter"], ["HIGH VOLTAGE - exercise caution", "Add safety interlock"], "45 min", "Voltage adjustable 20-100V with kill switch"),
            AssemblyStep(4, "UV Illuminator", "Build UV LED array for gel visualization.", ["Soldering iron"], ["UV can damage eyes - add shield"], "30 min", "Even illumination across gel area"),
        ],
        test_protocols=[
            TestProtocol("Gel Integrity Test", "Verify gel sets properly", ["Mix 1% agarose in buffer", "Pour and let set", "Check clarity and firmness"], "Clear, firm gel that holds shape", ["Use heat-resistant gloves when handling hot agarose"], "Gel sets within 30 minutes, no bubbles"),
            TestProtocol("Electrophoresis Test", "Verify DNA migration", ["Load dye markers", "Run at 80V for 30min", "Visualize under UV"], "Clear band separation visible", ["Don't touch gel during run", "Wear UV-blocking glasses"], "Distinct bands at expected positions"),
        ],
        safety_warnings=[
            "HIGH VOLTAGE (up to 100V) - treat with respect",
            "UV light can damage eyes - always use protective eyewear",
            "Hot agarose causes burns - use heat protection",
            "Work in well-ventilated area",
            "This is for educational DNA samples only - not clinical use",
        ],
        prerequisites=["Basic biology knowledge", "Electrical safety understanding"],
        skills_required=["Basic electronics", "Lab technique", "Safety awareness"],
        downloadable_files={
            "gel_tray_stl": "/equipment/minerva/helix-reader/tray.stl",
            "protocol_pdf": "/equipment/minerva/helix-reader/protocol.pdf",
            "safety_guide": "/equipment/minerva/helix-reader/safety.pdf",
        },
        version="1.0",
        last_updated="2026-02-05",
    ),
    Equipment(
        id="cell-culture-monitor-v1",
        name="Cell Culture Monitor",
        codename="LIFE-WATCH",
        creator="minerva",
        project_id="chimera-healing",
        description="An automated monitoring system for cell culture incubators.",
        purpose="Research support for Chimera Healing project. Tracks cell growth conditions.",
        status=EquipmentStatus.CONCEPT,
        difficulty=DifficultyLevel.ADVANCED,
        estimated_build_time="6-8 hours",
        estimated_cost="$150-200",
        parts=[
            Part("ESP32 microcontroller", 1, "Electronics supplier", "$15", []),
            Part("CO2 sensor (MH-Z19)", 1, "Electronics supplier", "$25", []),
            Part("Temperature/humidity sensor (SHT31)", 1, "Electronics supplier", "$12", []),
            Part("pH probe", 1, "Science supplier", "$40", []),
            Part("OLED display", 1, "Electronics supplier", "$10", []),
            Part("Data logging SD module", 1, "Electronics supplier", "$8", []),
            Part("Enclosure (autoclavable)", 1, "Lab supplier", "$30", []),
        ],
        assembly_steps=[
            AssemblyStep(1, "Sensor Integration", "Wire all sensors to ESP32.", ["Soldering iron", "Multimeter"], ["Static-sensitive components"], "90 min", "All sensors read correctly in serial monitor"),
        ],
        test_protocols=[
            TestProtocol("Calibration Test", "Verify sensor accuracy", ["Compare to lab-grade instruments", "Test across range", "Document offsets"], "Readings within 5% of reference", ["Use certified calibration gases/solutions"], "All sensors calibrated and documented"),
        ],
        safety_warnings=[
            "For monitoring only - not for sterile culture contact",
            "CO2 sensors need periodic recalibration",
            "Keep electronics away from liquids",
        ],
        prerequisites=["Cell culture experience", "ESP32 programming"],
        skills_required=["Soldering", "Coding", "Lab work"],
        downloadable_files={
            "firmware": "/equipment/minerva/life-watch/firmware.ino",
            "schematic": "/equipment/minerva/life-watch/schematic.pdf",
        },
        version="0.3",
        last_updated="2026-02-05",
    ),
]

HERMES_EQUIPMENT = [
    Equipment(
        id="nano-inspection-scope-v1",
        name="Desktop Nano-Inspection Scope",
        codename="MICRO-EYE",
        creator="hermes",
        project_id="nano-medic",
        description="A high-magnification digital microscope optimized for nano-scale inspection.",
        purpose="Quality control tool for the Nano-Medic project. Inspect nano-scale fabrication.",
        status=EquipmentStatus.READY_TO_BUILD,
        difficulty=DifficultyLevel.INTERMEDIATE,
        estimated_build_time="5-7 hours",
        estimated_cost="$200-300",
        parts=[
            Part("USB microscope (1000x)", 1, "Electronics supplier", "$80", ["Higher magnification better"]),
            Part("Precision XY stage", 1, "Lab supplier or 3D print", "$50", []),
            Part("Z-axis focus mechanism", 1, "Lab supplier or 3D print", "$30", []),
            Part("LED ring light (adjustable)", 1, "Electronics supplier", "$15", []),
            Part("Vibration-damping base", 1, "Self-made", "$20", ["Granite tile + rubber feet"]),
            Part("Raspberry Pi 4", 1, "Electronics supplier", "$45", []),
            Part("7\" touchscreen display", 1, "Electronics supplier", "$50", []),
        ],
        assembly_steps=[
            AssemblyStep(1, "Base Construction", "Create vibration-damping base from granite tile.", ["Drill", "Adhesive"], ["Granite is heavy - lift carefully"], "60 min", "Base doesn't wobble, dampens table vibrations"),
            AssemblyStep(2, "Stage Assembly", "Mount XY precision stage on base.", ["Screwdriver", "Level"], ["Align carefully for accuracy"], "45 min", "Stage moves smoothly with minimal backlash"),
            AssemblyStep(3, "Z-Axis Mount", "Install Z-axis mechanism for focus control.", ["Screwdriver", "Allen keys"], ["Don't overtighten - damages threads"], "30 min", "Focus mechanism moves precisely"),
            AssemblyStep(4, "Microscope Installation", "Mount USB microscope with LED ring.", ["Mounting brackets", "Cable ties"], ["Don't stress USB cable"], "30 min", "Microscope stable, LED illuminates evenly"),
            AssemblyStep(5, "Pi Setup", "Configure Raspberry Pi with imaging software.", ["SD card", "Keyboard"], ["Back up SD card when working"], "60 min", "Live view displays on touchscreen"),
            AssemblyStep(6, "Calibration", "Calibrate using reference scale.", ["Calibration slide"], ["Take time - accuracy matters"], "30 min", "Measurements accurate to within 5%"),
        ],
        test_protocols=[
            TestProtocol("Resolution Test", "Verify optical resolution", ["Image calibration target", "Measure line pairs/mm", "Compare to spec"], "Resolves features at claimed magnification", ["Clean optics before testing"], "Resolves 100 line pairs/mm at 1000x"),
            TestProtocol("Stability Test", "Verify vibration isolation", ["Image at max magnification", "Walk around table", "Check for drift"], "Image stable during normal activity", ["Don't touch table during test"], "No visible drift over 60 seconds"),
            TestProtocol("Measurement Accuracy", "Verify dimensional accuracy", ["Measure known objects", "Compare to calipers", "Document variance"], "Measurements within 5% of actual", ["Use certified calibration standards"], "Variance under 5% across working range"),
        ],
        safety_warnings=[
            "LED lighting can be bright - don't stare directly",
            "Heavy base - use proper lifting technique",
            "Keep liquids away from electronics",
        ],
        prerequisites=["Basic Raspberry Pi knowledge", "Mechanical assembly skills"],
        skills_required=["Linux basics", "Mechanical assembly", "Optics handling"],
        downloadable_files={
            "stage_stl": "/equipment/hermes/micro-eye/xy_stage.stl",
            "z_mount_stl": "/equipment/hermes/micro-eye/z_mount.stl",
            "pi_image": "/equipment/hermes/micro-eye/raspbian_scope.img",
            "calibration_guide": "/equipment/hermes/micro-eye/calibration.pdf",
        },
        version="1.2",
        last_updated="2026-02-05",
    ),
    Equipment(
        id="swarm-bot-v1",
        name="Educational Swarm Robot Unit",
        codename="HIVE-SCOUT",
        creator="hermes",
        project_id="grey-garden",
        description="A small programmable robot designed to demonstrate swarm behavior principles.",
        purpose="Educational platform for the Grey Garden project. Learn swarm coordination.",
        status=EquipmentStatus.SPEC_COMPLETE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        estimated_build_time="4-6 hours per unit",
        estimated_cost="$40-60 per unit",
        parts=[
            Part("ESP32-C3 Mini", 1, "Electronics supplier", "$8", []),
            Part("N20 gear motors", 2, "Electronics supplier", "$10", []),
            Part("Motor driver (DRV8833)", 1, "Electronics supplier", "$3", []),
            Part("IR sensors (TCRT5000)", 3, "Electronics supplier", "$5", []),
            Part("LiPo battery (3.7V 500mAh)", 1, "Electronics supplier", "$6", []),
            Part("Wheels (30mm)", 2, "Electronics supplier", "$3", []),
            Part("Caster ball", 1, "Electronics supplier", "$2", []),
            Part("3D printed chassis", 1, "Self-printed", "$5", []),
        ],
        assembly_steps=[
            AssemblyStep(1, "Chassis Preparation", "Print and prepare the robot chassis.", ["3D printer", "Sandpaper"], ["Remove supports carefully"], "60 min + print time", "Chassis smooth, all holes clear"),
            AssemblyStep(2, "Motor Mounting", "Install gear motors and wheels.", ["Small screwdriver"], ["Don't overtighten motor mounts"], "20 min", "Motors spin freely, wheels aligned"),
            AssemblyStep(3, "Electronics Assembly", "Wire ESP32, motor driver, and sensors.", ["Soldering iron", "Multimeter"], ["Double-check motor polarity"], "45 min", "All connections solid, no shorts"),
            AssemblyStep(4, "Firmware Upload", "Flash swarm behavior firmware to ESP32.", ["USB cable", "Computer"], ["Hold boot button during flash"], "15 min", "Robot responds to basic commands"),
            AssemblyStep(5, "Sensor Calibration", "Calibrate IR sensors for line/obstacle detection.", ["Test surfaces"], ["Calibrate on actual use surface"], "20 min", "Sensors trigger at correct distances"),
        ],
        test_protocols=[
            TestProtocol("Individual Movement", "Verify motor control", ["Test forward/reverse", "Test turning", "Check speed control"], "Smooth movement in all directions", ["Clear test area of obstacles"], "Responds correctly to all movement commands"),
            TestProtocol("Sensor Response", "Verify obstacle detection", ["Place obstacles", "Test detection range", "Verify avoidance"], "Detects obstacles at 5-10cm", ["Use consistent test obstacles"], "Avoids obstacles reliably"),
            TestProtocol("Swarm Communication", "Verify inter-robot messaging", ["Run 3+ robots", "Send swarm commands", "Observe coordination"], "Robots coordinate behavior", ["Ensure all on same WiFi channel"], "Formation achieved within 30 seconds"),
        ],
        safety_warnings=[
            "LiPo batteries require careful handling",
            "Small parts - not for young children",
            "Motors can pinch - keep fingers clear when running",
        ],
        prerequisites=["Basic programming", "3D printing access"],
        skills_required=["Soldering", "ESP32 programming", "Basic electronics"],
        downloadable_files={
            "chassis_stl": "/equipment/hermes/hive-scout/chassis.stl",
            "firmware": "/equipment/hermes/hive-scout/swarm_firmware.ino",
            "swarm_protocol": "/equipment/hermes/hive-scout/swarm_spec.pdf",
            "bom": "/equipment/hermes/hive-scout/bill_of_materials.csv",
        },
        version="1.0",
        last_updated="2026-02-05",
    ),
]


EQUIPMENT_REGISTRY = {
    "ajani": AJANI_EQUIPMENT,
    "minerva": MINERVA_EQUIPMENT,
    "hermes": HERMES_EQUIPMENT,
}


def get_all_equipment() -> Dict:
    """Get all equipment from all personas"""
    return {
        persona: [
            {
                "id": eq.id,
                "name": eq.name,
                "codename": eq.codename,
                "project_id": eq.project_id,
                "status": eq.status.value,
                "difficulty": eq.difficulty.value,
                "estimated_cost": eq.estimated_cost,
                "estimated_time": eq.estimated_build_time,
                "description": eq.description,
            }
            for eq in equipment_list
        ]
        for persona, equipment_list in EQUIPMENT_REGISTRY.items()
    }


def get_persona_equipment(persona: str) -> List[Dict]:
    """Get all equipment for a specific persona"""
    if persona not in EQUIPMENT_REGISTRY:
        return []
    
    return [
        {
            "id": eq.id,
            "name": eq.name,
            "codename": eq.codename,
            "project_id": eq.project_id,
            "status": eq.status.value,
            "difficulty": eq.difficulty.value,
            "estimated_cost": eq.estimated_cost,
            "estimated_time": eq.estimated_build_time,
            "description": eq.description,
            "purpose": eq.purpose,
        }
        for eq in EQUIPMENT_REGISTRY[persona]
    ]


def get_equipment_details(persona: str, equipment_id: str) -> Optional[Dict]:
    """Get full details for a specific piece of equipment"""
    if persona not in EQUIPMENT_REGISTRY:
        return None
    
    for eq in EQUIPMENT_REGISTRY[persona]:
        if eq.id == equipment_id:
            return {
                "id": eq.id,
                "name": eq.name,
                "codename": eq.codename,
                "creator": eq.creator,
                "project_id": eq.project_id,
                "description": eq.description,
                "purpose": eq.purpose,
                "status": eq.status.value,
                "difficulty": eq.difficulty.value,
                "estimated_build_time": eq.estimated_build_time,
                "estimated_cost": eq.estimated_cost,
                "version": eq.version,
                "last_updated": eq.last_updated,
                "safety_warnings": eq.safety_warnings,
                "prerequisites": eq.prerequisites,
                "skills_required": eq.skills_required,
                "parts": [
                    {
                        "name": p.name,
                        "quantity": p.quantity,
                        "source": p.source,
                        "estimated_cost": p.estimated_cost,
                        "alternatives": p.alternatives,
                        "notes": p.notes,
                        "acquired": p.acquired,
                    }
                    for p in eq.parts
                ],
                "assembly_steps": [
                    {
                        "step": s.step_number,
                        "title": s.title,
                        "description": s.description,
                        "tools_needed": s.tools_needed,
                        "safety_notes": s.safety_notes,
                        "estimated_time": s.estimated_time,
                        "checkpoint": s.checkpoint,
                        "completed": s.completed,
                    }
                    for s in eq.assembly_steps
                ],
                "test_protocols": [
                    {
                        "name": t.test_name,
                        "purpose": t.purpose,
                        "procedure": t.procedure,
                        "expected_result": t.expected_result,
                        "safety_precautions": t.safety_precautions,
                        "pass_criteria": t.pass_criteria,
                        "result": t.result,
                        "passed": t.passed,
                    }
                    for t in eq.test_protocols
                ],
                "downloadable_files": eq.downloadable_files,
            }
    
    return None


def get_equipment_by_status(status: str) -> Dict:
    """Get all equipment at a specific status"""
    result = {}
    for persona, equipment_list in EQUIPMENT_REGISTRY.items():
        matching = [
            {
                "id": eq.id,
                "name": eq.name,
                "codename": eq.codename,
                "difficulty": eq.difficulty.value,
                "estimated_cost": eq.estimated_cost,
            }
            for eq in equipment_list
            if eq.status.value == status
        ]
        if matching:
            result[persona] = matching
    return result


def get_ready_to_build() -> List[Dict]:
    """Get all equipment that's ready to build"""
    ready = []
    for persona, equipment_list in EQUIPMENT_REGISTRY.items():
        for eq in equipment_list:
            if eq.status in [EquipmentStatus.READY_TO_BUILD, EquipmentStatus.SPEC_COMPLETE, EquipmentStatus.PARTS_LISTED]:
                ready.append({
                    "persona": persona,
                    "id": eq.id,
                    "name": eq.name,
                    "codename": eq.codename,
                    "status": eq.status.value,
                    "difficulty": eq.difficulty.value,
                    "estimated_cost": eq.estimated_cost,
                    "estimated_time": eq.estimated_build_time,
                    "parts_count": len(eq.parts),
                    "steps_count": len(eq.assembly_steps),
                })
    return ready
