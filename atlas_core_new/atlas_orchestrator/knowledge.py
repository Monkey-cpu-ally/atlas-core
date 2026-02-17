"""Canonical Atlas vision, domain registry, and prototype metadata."""

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
    "Definitions",
    "Mathematical foundations (gradual introduction)",
    "Physical intuition",
    "Real-world application",
    "Prototype examples",
]


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

