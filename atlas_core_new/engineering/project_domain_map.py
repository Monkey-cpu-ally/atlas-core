"""
Project-to-Domain Mapping — Links all 33 research projects to their correct lab domains.

Each project is mapped to a primary domain from the 8 available lab domains:
  botany_pod, bio_archive_flower, eco_robotics, medusa_transparent_mech,
  transparent_liquid_armor, crypto_security, bio_sim_human_performance,
  biocompatible_microdevice_sim
"""

from __future__ import annotations
from typing import Dict, Optional, List

PROJECT_DOMAIN_MAP: Dict[str, Dict[str, str]] = {
    "survival-botany": {
        "domain": "botany_pod",
        "rationale": "Plant survival systems — direct fit for botany pod capsule design.",
    },
    "permaculture": {
        "domain": "botany_pod",
        "rationale": "Permaculture systems overlap with automated botany pod monitoring.",
    },
    "plant-alchemy": {
        "domain": "botany_pod",
        "rationale": "Plant chemistry and transformation — botany pod with sensor overlay.",
    },
    "mythologies": {
        "domain": "bio_sim_human_performance",
        "rationale": "Mythology analysis as simulation/knowledge model — software domain.",
    },
    "comic-development": {
        "domain": "bio_sim_human_performance",
        "rationale": "Creative/narrative project — software simulation and modeling.",
    },
    "dna-storage": {
        "domain": "biocompatible_microdevice_sim",
        "rationale": "DNA as storage medium — biocompatible microdevice with lab fabrication.",
    },
    "ancient-architecture": {
        "domain": "eco_robotics",
        "rationale": "Structural engineering with environmental context — eco-robotics scale.",
    },
    "chimera-healing": {
        "domain": "biocompatible_microdevice_sim",
        "rationale": "Bio-healing systems — biocompatible microdevice simulation.",
    },
    "ancestral-code": {
        "domain": "crypto_security",
        "rationale": "Code/cipher systems rooted in ancestral patterns — crypto security domain.",
    },
    "apex-protocol": {
        "domain": "crypto_security",
        "rationale": "Protocol design with security layers — crypto security domain.",
    },
    "medusa-frame": {
        "domain": "medusa_transparent_mech",
        "rationale": "Transparent mechanical frame — direct fit for medusa transparent mech.",
        "design_notes": "Transparent plastic doc ock arms like Spider-Verse. NOT metal. Cable-driven actuation through clear polycarbonate/acrylic segments.",
        "overrides": {"prefer_transparent": True, "exclude_metal": True},
    },
    "splice-sanctuary": {
        "domain": "biocompatible_microdevice_sim",
        "rationale": "Bio-splicing sanctuary — biocompatible microdevice simulation.",
    },
    "bio-architecture": {
        "domain": "bio_archive_flower",
        "rationale": "Biological architecture — bio archive with preservation and structure.",
        "design_notes": "Metal flowers that store plant DNA/biology using transparent biopolymer capsule.",
        "overrides": {"prefer_transparent": True, "prefer_biopolymer": True},
    },
    "liquid-armor": {
        "domain": "transparent_liquid_armor",
        "rationale": "Liquid armor system — direct fit for transparent liquid armor domain.",
        "design_notes": "Transparent impact protection system. Polycarbonate + gel/STF + elastomer stack.",
        "overrides": {"prefer_transparent": True},
    },
    "density-matrix": {
        "domain": "transparent_liquid_armor",
        "rationale": "Material density research — overlaps with armor layering and material science.",
    },
    "hydra-core": {
        "domain": "eco_robotics",
        "rationale": "Power spine / core system — eco-robotics with power management focus.",
    },
    "green-robotics": {
        "domain": "eco_robotics",
        "rationale": "Environmental robotics — direct fit for eco-robotics domain.",
        "design_notes": "NOT green paint — environmental helper robots. Include power cell module interface.",
        "overrides": {"add_power_cell": True},
    },
    "insert-cell": {
        "domain": "biocompatible_microdevice_sim",
        "rationale": "Cell insertion tech — biocompatible microdevice domain.",
    },
    "resonance-engine": {
        "domain": "eco_robotics",
        "rationale": "Vibrational/resonance system — sensor and actuator focus maps to eco-robotics.",
    },
    "robotic-arms": {
        "domain": "medusa_transparent_mech",
        "rationale": "Robotic arm fabrication — medusa transparent mech with cable-driven actuation.",
    },
    "morphing-structures": {
        "domain": "medusa_transparent_mech",
        "rationale": "Shape-changing structures — transparent mechanical design principles.",
    },
    "solar-gem": {
        "domain": "eco_robotics",
        "rationale": "Solar energy harvesting — eco-robotics with power/sensor integration.",
    },
    "photon-sink": {
        "domain": "eco_robotics",
        "rationale": "Photonic energy capture — eco-robotics energy systems.",
    },
    "kinetic-forge": {
        "domain": "eco_robotics",
        "rationale": "Kinetic energy systems — eco-robotics with mechanical energy conversion.",
    },
    "element-synthesis": {
        "domain": "bio_archive_flower",
        "rationale": "Elemental composition work — bio archive with material preservation.",
    },
    "wave-rider": {
        "domain": "eco_robotics",
        "rationale": "Wave energy systems — eco-robotics with environmental energy harvesting.",
    },
    "quantum-encryption": {
        "domain": "crypto_security",
        "rationale": "Quantum-safe encryption — direct fit for crypto security domain.",
    },
    "nano-medic": {
        "domain": "biocompatible_microdevice_sim",
        "rationale": "Nano-scale medical device — biocompatible microdevice simulation.",
        "design_notes": "Biocompatible + externally programmable nanoswarm. Simulation only.",
        "overrides": {"simulation_only": True, "externally_programmable": True},
    },
    "grey-garden": {
        "domain": "botany_pod",
        "rationale": "Garden/ecosystem management — botany pod with environmental control.",
    },
    "atomic-architect": {
        "domain": "biocompatible_microdevice_sim",
        "rationale": "Atomic-scale design — microdevice simulation at smallest scales.",
    },
    "bio-nanotech": {
        "domain": "biocompatible_microdevice_sim",
        "rationale": "Bio-nano technology — direct fit for biocompatible microdevice.",
        "design_notes": "Biocompatible + externally programmable nanotech/swarm. Simulation only.",
        "overrides": {"simulation_only": True, "externally_programmable": True},
    },
}


def get_project_domain(project_id: str) -> Optional[str]:
    entry = PROJECT_DOMAIN_MAP.get(project_id)
    if entry:
        return entry["domain"]
    return None


def get_project_domain_info(project_id: str) -> Optional[Dict[str, str]]:
    return PROJECT_DOMAIN_MAP.get(project_id)


def get_all_mappings() -> Dict[str, Dict[str, str]]:
    return PROJECT_DOMAIN_MAP


def get_domain_projects(domain: str) -> List[str]:
    return [pid for pid, info in PROJECT_DOMAIN_MAP.items() if info["domain"] == domain]
