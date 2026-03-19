"""
atlas_core_new/research/hephaestus_engine.py

Hephaestus-lite Experimental Engine
Discovery Pipeline: Idea → Model → Simulate → Fail → Adjust → Repeat

Workflow:
  1. Ajani proposes theory (idea phase)
  2. Hermes builds model + runs simulation
  3. System identifies top 5 failure modes
  4. Minerva evaluates risk + ethics
  5. Hermes iterates parameters
  6. Log results, repeat
"""

import uuid

PIPELINE_PHASES = [
    "idea",
    "literature",
    "model",
    "simulate",
    "fail_analysis",
    "adjust",
    "prototype_concept"
]

PHASE_LABELS = {
    "idea": "Idea Generation",
    "literature": "Literature & Constraints",
    "model": "Mathematical Modeling",
    "simulate": "Digital Simulation",
    "fail_analysis": "Failure Mapping",
    "adjust": "Optimization & Adjustment",
    "prototype_concept": "Prototype Concept"
}

PHASE_PERSONA = {
    "idea": "ajani",
    "literature": "ajani",
    "model": "hermes",
    "simulate": "hermes",
    "fail_analysis": "hermes",
    "adjust": "minerva",
    "prototype_concept": "ajani"
}

PHASE_DESCRIPTIONS = {
    "idea": "Ajani proposes a theoretical hypothesis grounded in real science. Cross-domain intersections are explored.",
    "literature": "Survey existing research, identify physics constraints, material limits, and known failure patterns.",
    "model": "Hermes constructs a mathematical model with equations, parameters, and boundary conditions.",
    "simulate": "Run structured simulation with constraint-bounded parameters. Stress test under edge conditions.",
    "fail_analysis": "Identify top 5 failure modes with severity, evidence, and mitigation paths.",
    "adjust": "Minerva evaluates ethics/risk. Hermes adjusts parameters based on failure data. Iterate.",
    "prototype_concept": "Consolidate validated parameters into a prototype specification with bill of materials."
}

INNOVATION_LEVELS = {
    1: {"label": "creative_remix", "name": "Creative Remix", "desc": "Recombining existing ideas in a new way"},
    2: {"label": "optimization", "name": "Optimization Improvement", "desc": "Making something existing work better"},
    3: {"label": "new_config", "name": "New Configuration", "desc": "Novel arrangement of known technology"},
    4: {"label": "new_method", "name": "New Material/Method", "desc": "Discovery of new physical approach"},
    5: {"label": "paradigm_shift", "name": "Paradigm Shift", "desc": "Fundamental change in how we understand the domain"}
}

SCIENTIFIC_DOMAINS = [
    "advanced_chemistry",
    "aerospace_engineering",
    "quantum_mechanics",
    "bio_architecture",
    "robotics",
    "energy_systems",
    "materials_science",
    "computing",
    "bioelectric_medicine",
    "ecology",
    "nanotechnology",
    "photonics",
    "fluid_dynamics",
    "thermodynamics",
    "genetics"
]

DOMAIN_LABELS = {
    "advanced_chemistry": "Advanced Chemistry",
    "aerospace_engineering": "Aerospace Engineering",
    "quantum_mechanics": "Quantum Mechanics",
    "bio_architecture": "Bio-Architecture",
    "robotics": "Robotics",
    "energy_systems": "Energy Systems",
    "materials_science": "Materials Science",
    "computing": "Computing",
    "bioelectric_medicine": "Bioelectric Medicine",
    "ecology": "Ecology",
    "nanotechnology": "Nanotechnology",
    "photonics": "Photonics",
    "fluid_dynamics": "Fluid Dynamics",
    "thermodynamics": "Thermodynamics",
    "genetics": "Genetics"
}

DOMAIN_INTERSECTIONS = {
    ("robotics", "ecology"): {
        "name": "Green Adaptive Machines",
        "potential": "Bio-inspired robots that integrate with natural ecosystems",
        "constraints": ["must not harm local wildlife", "energy from renewable sources only", "biodegradable components preferred"]
    },
    ("advanced_chemistry", "computing"): {
        "name": "Computational Materials Discovery",
        "potential": "AI-driven prediction of new material properties before synthesis",
        "constraints": ["must be synthesizable with current technology", "toxicity limits", "cost per gram targets"]
    },
    ("bio_architecture", "computing"): {
        "name": "Neural Architecture Systems",
        "potential": "Computing paradigms inspired by biological neural structures",
        "constraints": ["power consumption limits", "heat dissipation", "signal propagation speed"]
    },
    ("quantum_mechanics", "materials_science"): {
        "name": "Quantum Material Engineering",
        "potential": "Materials with engineered quantum properties for energy/computing",
        "constraints": ["operating temperature requirements", "coherence time", "fabrication complexity"]
    },
    ("energy_systems", "nanotechnology"): {
        "name": "Nano-Energy Harvesting",
        "potential": "Energy capture and storage at nanoscale for ubiquitous power",
        "constraints": ["efficiency thresholds", "degradation rates", "manufacturing scalability"]
    },
    ("aerospace_engineering", "materials_science"): {
        "name": "Extreme Environment Materials",
        "potential": "Materials surviving reentry, deep space radiation, extreme temperatures",
        "constraints": ["weight-to-strength ratios", "thermal cycling tolerance", "radiation resistance"]
    },
    ("genetics", "computing"): {
        "name": "DNA Data Storage",
        "potential": "Using biological substrates for ultra-dense information storage",
        "constraints": ["read/write speed", "error rates", "stability over time", "cost per megabyte"]
    },
    ("photonics", "computing"): {
        "name": "Optical Computing",
        "potential": "Light-based processors for massively parallel computation",
        "constraints": ["integration density", "switching speed", "power efficiency", "thermal management"]
    },
    ("bioelectric_medicine", "nanotechnology"): {
        "name": "Targeted Bioelectric Therapy",
        "potential": "Nano-scale devices that modulate cellular electrical signals for healing",
        "constraints": ["biocompatibility", "immune response", "precision targeting", "power delivery"]
    },
    ("thermodynamics", "energy_systems"): {
        "name": "Entropy Engineering",
        "potential": "Maximizing energy efficiency by engineered thermal management",
        "constraints": ["second law limits", "material thermal conductivity", "system complexity"]
    },
    ("robotics", "bioelectric_medicine"): {
        "name": "Surgical Micro-Robotics",
        "potential": "Autonomous micro-robots for minimally invasive surgery and tissue repair",
        "constraints": ["size limits", "navigation accuracy", "biocompatibility", "power source"]
    },
    ("fluid_dynamics", "aerospace_engineering"): {
        "name": "Hypersonic Flow Control",
        "potential": "Active control of airflow at extreme speeds for next-gen flight",
        "constraints": ["thermal protection", "control surface response time", "energy budget"]
    }
}

DEFAULT_CONSTRAINT_TEMPLATES = {
    "robotics": {
        "physics_laws": ["Newton's laws of motion", "Conservation of energy", "Friction and wear models"],
        "materials_available": ["Aluminum alloys", "Carbon fiber", "Servo motors", "Li-Ion batteries", "PCBs"],
        "manufacturing_tools": ["3D printer (FDM/SLA)", "CNC mill", "Laser cutter", "Soldering station"],
        "energy_requirements": {"min_watts": 5, "max_watts": 500, "battery_wh": 50},
        "safety_profile": ["Emergency stop required", "No exposed pinch points", "Current limiting on motors"],
        "failure_envelope": ["Motor burnout at >2x rated current", "Structural failure at >10G impact", "Water ingress above IP65"]
    },
    "energy_systems": {
        "physics_laws": ["Thermodynamics (1st and 2nd law)", "Ohm's law", "Faraday's law of electrolysis"],
        "materials_available": ["PEM membranes", "Platinum catalysts", "Graphite electrodes", "Steel pressure vessels"],
        "manufacturing_tools": ["Hydraulic press", "Welding equipment", "Gas chromatograph", "Multimeter"],
        "energy_requirements": {"target_efficiency": 0.6, "operating_temp_c": [20, 80], "pressure_bar": [1, 350]},
        "safety_profile": ["Hydrogen leak detection mandatory", "Pressure relief valves", "Ventilation requirements"],
        "failure_envelope": ["Membrane degradation above 90C", "Catalyst poisoning from CO", "Pressure vessel fatigue"]
    },
    "advanced_chemistry": {
        "physics_laws": ["Conservation of mass", "Le Chatelier's principle", "Gibbs free energy"],
        "materials_available": ["Standard lab reagents", "Analytical instruments", "Fume hoods"],
        "manufacturing_tools": ["Rotary evaporator", "Spectrophotometer", "pH meter", "Centrifuge"],
        "energy_requirements": {"reaction_temp_range": [-78, 300], "pressure_range_atm": [0.01, 100]},
        "safety_profile": ["SDS sheets required", "PPE mandatory", "Waste disposal protocol"],
        "failure_envelope": ["Runaway exothermic reactions", "Toxic byproduct formation", "Solvent incompatibility"]
    },
    "materials_science": {
        "physics_laws": ["Crystal structure theory", "Phase diagrams", "Stress-strain relationships"],
        "materials_available": ["Metal alloys", "Polymers", "Ceramics", "Composites", "Nanomaterials"],
        "manufacturing_tools": ["Furnace", "Tensile tester", "SEM/TEM microscope", "X-ray diffractometer"],
        "energy_requirements": {"sintering_temp": [800, 2000], "cooling_rate_critical": True},
        "safety_profile": ["High temperature handling", "Dust inhalation prevention", "Radiation shielding for XRD"],
        "failure_envelope": ["Grain boundary fracture", "Creep at elevated temperature", "Fatigue crack propagation"]
    }
}


def generate_run_id():
    return f"exp-{uuid.uuid4().hex[:12]}"


def get_domain_intersection(domain_a, domain_b):
    key = (domain_a, domain_b)
    rev_key = (domain_b, domain_a)
    return DOMAIN_INTERSECTIONS.get(key) or DOMAIN_INTERSECTIONS.get(rev_key)


def get_all_intersections_for_domain(domain):
    results = []
    for (a, b), info in DOMAIN_INTERSECTIONS.items():
        if a == domain or b == domain:
            other = b if a == domain else a
            results.append({
                "partner_domain": other,
                "partner_label": DOMAIN_LABELS.get(other, other),
                **info
            })
    return results


def get_default_constraints(domain):
    return DEFAULT_CONSTRAINT_TEMPLATES.get(domain, {
        "physics_laws": ["To be determined based on domain analysis"],
        "materials_available": ["Standard laboratory equipment"],
        "manufacturing_tools": ["Basic workshop tools"],
        "energy_requirements": {},
        "safety_profile": ["Standard safety protocols apply"],
        "failure_envelope": ["To be mapped during simulation phase"]
    })


def score_innovation_level(run_data):
    score = 1
    if run_data.get("domain_secondary"):
        score = max(score, 2)
    iteration_count = run_data.get("iteration_count", 0)
    if iteration_count >= 10:
        score = max(score, 2)
    if iteration_count >= 50:
        score = max(score, 3)
    fm_count = run_data.get("failure_modes_count", 0)
    if fm_count >= 5 and run_data.get("resolved_count", 0) >= 3:
        score = max(score, 3)
    phase = run_data.get("phase", "idea")
    if phase in ("adjust", "prototype_concept"):
        score = max(score, 3)
    if run_data.get("novel_mechanism"):
        score = max(score, 4)
    return score


def get_pipeline_status(phase):
    idx = PIPELINE_PHASES.index(phase) if phase in PIPELINE_PHASES else 0
    total = len(PIPELINE_PHASES)
    return {
        "current_phase": phase,
        "current_label": PHASE_LABELS.get(phase, phase),
        "phase_index": idx,
        "total_phases": total,
        "progress_pct": round((idx / (total - 1)) * 100) if total > 1 else 0,
        "persona_lead": PHASE_PERSONA.get(phase, "ajani"),
        "description": PHASE_DESCRIPTIONS.get(phase, ""),
        "phases": [
            {
                "id": p,
                "label": PHASE_LABELS[p],
                "persona": PHASE_PERSONA[p],
                "completed": PIPELINE_PHASES.index(p) < idx,
                "current": p == phase,
                "description": PHASE_DESCRIPTIONS[p]
            }
            for p in PIPELINE_PHASES
        ]
    }


def next_phase(current_phase):
    if current_phase not in PIPELINE_PHASES:
        return PIPELINE_PHASES[0]
    idx = PIPELINE_PHASES.index(current_phase)
    if idx >= len(PIPELINE_PHASES) - 1:
        return current_phase
    return PIPELINE_PHASES[idx + 1]
