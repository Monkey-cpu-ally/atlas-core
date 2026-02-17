"""Canonical Atlas doctrine, project registry, and domain metadata."""

from __future__ import annotations

from typing import Any


ATLAS_VISION: dict[str, Any] = {
    "end_goal": "Jarvis/Wakanda-class safety-bounded engineering ecosystem",
    "principles": [
        "Multi-agent intelligence",
        "Modular reasoning",
        "Real-time validation",
        "Structured blueprint generation",
        "Scientific rigor",
        "Ethical enforcement",
        "Human-centric learning partner",
    ],
    "identity": {
        "not": ["magic", "omniscient"],
        "is": [
            "engineering-competent",
            "cross-disciplinary",
            "self-improving under rules",
            "safety-bounded",
            "system-oriented",
        ],
    },
    "roles": {
        "atlas": "Orchestrator. Routes and governs. Does not think creatively.",
        "ajani": "Engineering intelligence: systems, constraints, tests, failure analysis.",
        "minerva": "Cognitive/cultural intelligence: clarity, analogies, reinforced learning.",
        "hermes": "Guardian/validator: safety, ethics, logical consistency, policy enforcement.",
    },
}


END_STATE_VISION_GROUNDED: dict[str, list[str]] = {
    "defined_as": [
        "Multi-agent modular architecture",
        "Cross-domain reasoning",
        "Real-time validation",
        "Structured project lifecycle",
        "Scientific rigor",
        "Strong safety enforcement",
        "Transparent reasoning structure",
        "Version-controlled memory",
    ],
    "not": [
        "Autonomous weapons",
        "Self-aware AI",
        "Magic materials",
        "Infinite processing",
    ],
}


ACADEMIC_FIELDS: dict[str, list[str]] = {
    "core_engineering": [
        "Electromagnetics",
        "Signal Processing",
        "Acoustics",
        "Control Systems Engineering",
        "Quantum Mechanics",
        "Neuroscience (brainwave frequencies)",
    ],
    "supporting": [
        "Materials Science",
        "Embedded Systems",
        "Robotics",
        "Power Systems",
        "AI Architecture",
        "Human-Computer Interaction",
    ],
}


FIELD_TEACHING_REQUIREMENTS: list[str] = [
    "Definition",
    "Physical intuition",
    "Mathematical core (when ready)",
    "Real-world example",
    "Prototype connection",
    "Risk & failure modes",
    "Mini build exercise",
    "Review loop",
]


TEACHING_FRAMEWORK_LOCK: dict[str, Any] = {
    "locked": True,
    "sequence": FIELD_TEACHING_REQUIREMENTS,
    "rule": "No skipping steps.",
}


ACADEMIC_INTEGRATION_PLAN: dict[str, list[str]] = {
    "Electromagnetics": [
        "Induction",
        "Field equations",
        "Sensor design",
    ],
    "Signal Processing": [
        "Time domain",
        "Frequency domain",
        "FFT",
        "Filtering",
        "Application",
    ],
    "Acoustics": [
        "Wave mechanics",
        "Resonance",
        "Harmonics",
        "Measurement",
    ],
    "Control Systems Engineering": [
        "Feedback loops",
        "Stability",
        "PID",
        "Adaptive tuning",
    ],
    "Neuroscience (brainwave frequencies)": [
        "Brainwave bands",
        "Measurement limits",
        "Signal noise",
    ],
    "Quantum Mechanics": [
        "Wave-particle duality",
        "Measurement theory",
        "Probability limits",
    ],
}


ATLAS_PROJECT_REGISTRY: list[dict[str, Any]] = [
    {
        "id": "wearable_resonance_scanner_v1",
        "name": "Wearable Resonance Scanner (v1)",
        "category": "Sensing / Signal Processing",
        "academic_dependencies": [
            "Electromagnetics",
            "Acoustics",
            "Signal Processing",
            "Control Systems Engineering",
            "Neuroscience (brainwave frequencies)",
        ],
        "current_phase": "Blueprint",
        "version": "v1",
        "objective": "Frequency mapping and resonance analysis device.",
    },
    {
        "id": "atlas_core_hybrid_system",
        "name": "Atlas Core Hybrid System",
        "category": "AI Architecture",
        "academic_dependencies": [
            "Control Systems Engineering",
            "Software Engineering",
            "Systems Design",
        ],
        "current_phase": "Blueprint -> Build",
        "version": "v0.1",
        "objective": "Multi-agent orchestrator with policy-governed routing.",
    },
    {
        "id": "blueprint_engine_lego_output",
        "name": "Blueprint Engine (Lego Output System)",
        "category": "Instructional AI",
        "academic_dependencies": [
            "Systems Design",
            "Human-Computer Interaction",
            "Cognitive Science",
        ],
        "current_phase": "Blueprint",
        "version": "v0.1",
        "objective": "Convert complex systems into layered, buildable steps.",
    },
    {
        "id": "environmental_green_systems",
        "name": "Environmental / Green Systems (Future)",
        "category": "Robotics / Sustainability",
        "academic_dependencies": [
            "Control Systems Engineering",
            "Materials Science",
            "Electromagnetics",
        ],
        "current_phase": "Concept",
        "version": "v0.0",
        "objective": "Sustainability robotics initiatives with safety-first design.",
    },
    {
        "id": "advanced_academic_engine",
        "name": "Advanced Academic Engine",
        "category": "Learning Architecture",
        "academic_dependencies": ["All integrated"],
        "current_phase": "Blueprint",
        "version": "v0.1",
        "objective": "Structured mastery across integrated disciplines.",
    },
]


CAPABILITY_MATRIX: list[dict[str, str]] = [
    {
        "capability": "Blueprint generation",
        "ajani": "primary",
        "minerva": "assist",
        "hermes": "validate",
        "atlas": "route",
    },
    {
        "capability": "Teaching explanation",
        "ajani": "assist",
        "minerva": "primary",
        "hermes": "review",
        "atlas": "route",
    },
    {
        "capability": "Security validation",
        "ajani": "assist",
        "minerva": "assist",
        "hermes": "primary",
        "atlas": "enforce",
    },
    {
        "capability": "Memory management",
        "ajani": "none",
        "minerva": "none",
        "hermes": "audit",
        "atlas": "primary",
    },
    {
        "capability": "Policy enforcement",
        "ajani": "none",
        "minerva": "none",
        "hermes": "primary",
        "atlas": "enforce",
    },
    {
        "capability": "Intent classification",
        "ajani": "none",
        "minerva": "none",
        "hermes": "audit",
        "atlas": "primary",
    },
]


ATLAS_CAPABILITY_BOUNDARIES: dict[str, list[str]] = {
    "can": [
        "Design",
        "Simulate",
        "Theorize",
        "Break down systems",
        "Teach rigorously",
        "Generate structured plans",
        "Cross-link academic fields",
    ],
    "cannot": [
        "Execute physical systems",
        "Override hardware",
        "Generate harmful instructions",
        "Remove safety gates",
        "Autonomously self-update without oversight",
    ],
}


HYBRID_OPERATIONAL_RULES: dict[str, Any] = {
    "frontend": [
        "Never contains reasoning core",
        "Only UI and API gateway",
        "No project memory storage",
    ],
    "backend": [
        "All reasoning",
        "All validation",
        "All memory",
        "All policy gates",
    ],
    "communication": [
        "JSON contracts only",
        "Strict schemas",
        "Version tagging",
    ],
}


DOCTRINE_FREEZE: dict[str, Any] = {
    "milestone": "Milestone 1",
    "title": "Finalize Doctrine and Freeze Architecture",
    "architecture_frozen": True,
    "pipeline_locked": ["Blueprint", "Build", "Modify"],
    "backend_implementation_allowed_after_freeze": True,
    "expansion_allowed": False,
    "rule": "No expansion until milestone complete.",
}


ACTIVE_PROTOTYPE: dict[str, Any] = {
    "id": "wearable_resonance_scanner_v1",
    "name": "Wearable Resonance Scanner (Prototype v1)",
    "objective": (
        "Design a wearable device that detects resonance patterns, measures signal variation, "
        "processes frequency bands, and safely maps environmental/biological signals."
    ),
    "academic_dependencies": {
        "Electromagnetics": ["Field generation", "Induction", "Wave propagation"],
        "Signal Processing": ["Filtering", "FFT", "Noise reduction", "Signal-to-noise ratio"],
        "Acoustics": ["Resonance", "Harmonics", "Standing waves"],
        "Control Systems Engineering": [
            "Feedback loops",
            "Stability control",
            "Adaptive tuning",
        ],
        "Neuroscience (brainwave frequencies)": [
            "Alpha/Beta/Theta/Delta bands",
            "Frequency ranges",
            "Non-invasive signal measurement principles",
        ],
        "Quantum Mechanics": [
            "Wave behavior (theoretical context only)",
            "Probability interpretation",
            "Measurement limits",
        ],
    },
}


LONG_TERM_EVOLUTION_PLAN: list[str] = [
    "Phase 1: Structured orchestrator + stable outputs",
    "Phase 2: Real project memory + versioning",
    "Phase 3: Mathematical modeling integration",
    "Phase 4: Simulation engine integration",
    "Phase 5: Advanced modular reasoning network",
]


_FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Electromagnetics": ("electromagnetic", "induction", "field", "coil", "em"),
    "Signal Processing": ("signal", "fft", "filter", "noise", "frequency"),
    "Acoustics": ("acoustic", "sound", "harmonic", "resonance", "wave"),
    "Control Systems Engineering": ("control loop", "feedback", "stability", "pid"),
    "Quantum Mechanics": ("quantum", "probability", "wave function"),
    "Neuroscience (brainwave frequencies)": ("brainwave", "alpha", "beta", "theta", "delta", "eeg"),
    "Materials Science": ("material", "polymer", "alloy", "composite"),
    "Embedded Systems": ("embedded", "microcontroller", "firmware"),
    "Robotics": ("robot", "actuator", "kinematics"),
    "Power Systems": ("power", "battery", "voltage", "current"),
    "AI Architecture": ("model", "inference", "agent", "ai"),
    "Human-Computer Interaction": ("ui", "ux", "interface", "interaction"),
}


def is_resonance_scanner_request(text: str) -> bool:
    lowered = text.lower()
    return "wearable resonance scanner" in lowered or (
        "resonance" in lowered and "wearable" in lowered
    )


def infer_relevant_fields(text: str) -> list[str]:
    lowered = text.lower()
    matches: list[str] = []
    for field, keywords in _FIELD_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            matches.append(field)

    if is_resonance_scanner_request(text):
        matches = list(ACTIVE_PROTOTYPE["academic_dependencies"].keys())

    if not matches:
        matches = [
            "Control Systems Engineering",
            "Signal Processing",
            "Embedded Systems",
        ]
    return matches


def get_project_registry_entry(project_name_or_id: str) -> dict[str, Any] | None:
    lookup = project_name_or_id.strip().lower()
    lookup_norm = "".join(ch for ch in lookup if ch.isalnum())
    for entry in ATLAS_PROJECT_REGISTRY:
        entry_id = str(entry["id"]).lower()
        entry_name = str(entry["name"]).lower()
        entry_id_norm = "".join(ch for ch in entry_id if ch.isalnum())
        entry_name_norm = "".join(ch for ch in entry_name if ch.isalnum())

        if entry_id == lookup:
            return entry
        if entry_name == lookup:
            return entry
        if lookup_norm and (lookup_norm in entry_name_norm or entry_name_norm in lookup_norm):
            return entry
        if lookup_norm and (lookup_norm in entry_id_norm or entry_id_norm in lookup_norm):
            return entry
    return None

