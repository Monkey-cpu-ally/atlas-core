"""
Tri-Core Agent Logic for the Design Engine.

Each persona contributes a different lens to engineering projects:
- Ajani: structural engineering, measurable variables, physics-first thinking
- Minerva: ethics, experiment design, safety, testability
- Hermes: validation, risk control, security gates
"""


def ajani_engineer(description: str) -> dict:
    return {
        "persona": "ajani",
        "focus": "Engineering structure & measurable variables",
        "suggestion": f"Extract measurable variables from: {description}",
        "checklist": [
            "Identify primary physical quantities (force, energy, temperature, etc.)",
            "Define success metrics with numeric thresholds",
            "Map dependencies between subsystems",
            "Establish test points for each critical path"
        ]
    }


def minerva_ethics(description: str) -> dict:
    return {
        "persona": "minerva",
        "focus": "Ethics, experiment design & safety",
        "suggestion": "Ensure safety, testability, and non-harmful scope.",
        "checklist": [
            "Verify no harmful biological or chemical pathways",
            "Confirm experiment is reproducible and falsifiable",
            "Check for dual-use concerns",
            "Ensure accessibility of materials and methods"
        ]
    }


def hermes_security(description: str) -> dict:
    return {
        "persona": "hermes",
        "focus": "Validation, risk control & security gates",
        "suggestion": "Block unsafe biological or weaponized pathways.",
        "checklist": [
            "Screen for restricted materials or processes",
            "Validate energy budget stays within safe bounds",
            "Check fabrication feasibility with available tools",
            "Confirm no regulatory violations in target domain"
        ]
    }
