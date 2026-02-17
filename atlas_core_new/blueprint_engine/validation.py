from __future__ import annotations
from typing import List
from .schemas import BlueprintPacket

FORBIDDEN_TERMS = [
    "dark alloy", "unobtainium", "99% efficiency",
    "instant regeneration", "molecular healing", "superhuman",
]

def validate_packet(packet: BlueprintPacket) -> List[str]:
    issues = []

    joined_text = " ".join([
        packet.title, packet.objective,
        " ".join(packet.assumptions),
        " ".join(packet.power_flow),
        " ".join(packet.control_logic),
        " ".join([m.name + " " + m.use + " " + m.justification for m in packet.materials]),
    ]).lower()

    for term in FORBIDDEN_TERMS:
        if term in joined_text:
            issues.append(f"Blocked term detected: '{term}' — replace with measurable, real spec or mark SIM-ONLY.")

    if packet.domain == "BIOMED_SIM_ONLY":
        issues.append("BIO SAFETY: Simulation-only. No wet-lab, no human enhancement instructions.")

    if not packet.requirements:
        issues.append("Missing requirements list.")
    if not packet.architecture:
        issues.append("Missing architecture modules.")
    if not packet.materials:
        issues.append("Missing materials specs.")
    if not packet.fabrication_steps:
        issues.append("Missing fabrication steps.")
    if not packet.failure_modes:
        issues.append("Missing failure modes.")

    return issues
