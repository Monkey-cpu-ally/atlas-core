from __future__ import annotations
from typing import Dict, List, Any


DOMAINS = [
    "botany_pod",
    "bio_archive_flower",
    "eco_robotics",
    "medusa_transparent_mech",
    "transparent_liquid_armor",
    "crypto_security",
    "bio_sim_human_performance",
    "biocompatible_microdevice_sim",
]

MATERIAL_LIBRARY: Dict[str, List[str]] = {
    "transparent_structural": [
        "polycarbonate_sheet",
        "acrylic_sheet",
        "clear_petg",
        "clear_resin_cast",
        "transparent_tpu_gasket",
    ],
    "robotics_structural": [
        "aluminum_6061",
        "aluminum_extrusion_2020",
        "steel_fasteners_stainless",
        "abs_enclosure",
        "polycarbonate_enclosure",
        "petg_brackets",
        "tpu_vibration_dampers",
    ],
    "transparent_impact": [
        "polycarbonate_outer_layer",
        "clear_polyurethane_gel_layer",
        "silicone_backer",
        "transparent_tpu_edge_seal",
        "clear_spacer_mesh",
    ],
    "botany_capsule": [
        "polycarbonate_shell",
        "clear_petg_shell",
        "transparent_tpu_seals",
        "hydrogel_root_matrix",
        "porous_substrate_tray",
        "uv_protective_clear_coating",
    ],
    "crypto_components": [
        "os_keystore",
        "secure_command_envelope",
        "nonce_replay_cache",
        "audit_log_store",
        "api_gateway_policy",
    ],
    "bio_sim_components": [
        "literature_graph_db",
        "risk_model",
        "uncertainty_estimator",
        "ethics_gate",
        "training_optimizer",
    ],
}

POWER_LIBRARY: Dict[str, List[Dict[str, Any]]] = {
    "passive": [
        {"source": "none", "avg_watts": 0, "peak_watts": 0, "notes": "Passive system."}
    ],
    "low_power_sensor": [
        {"source": "battery", "bus_voltage_v": 5, "avg_watts": 2, "peak_watts": 5, "notes": "Sensor pod class."},
        {"source": "solar", "bus_voltage_v": 5, "avg_watts": 1, "peak_watts": 3, "notes": "Trickle solar assist."},
    ],
    "robotics_24v": [
        {"source": "battery", "bus_voltage_v": 24, "avg_watts": 60, "peak_watts": 150, "notes": "Small bot/node standard."},
        {"source": "battery", "bus_voltage_v": 24, "avg_watts": 150, "peak_watts": 500, "notes": "Actuator-ready 24V."},
    ],
    "robotics_48v": [
        {"source": "battery", "bus_voltage_v": 48, "avg_watts": 250, "peak_watts": 800, "notes": "Medium platform option."},
    ],
    "software": [
        {"source": "software", "avg_watts": 0, "peak_watts": 0, "notes": "Software-only; measure CPU time/latency instead."}
    ],
}

FAB_LIBRARY: Dict[str, List[str]] = {
    "rapid_proto": ["3d_print", "laser_cut", "bolt_assembly"],
    "structural_proto": ["cnc_plate", "aluminum_extrusion", "bolt_assembly"],
    "sealed_capsule": ["laser_cut", "gasket_seal", "bolt_ring", "resin_seal_optional"],
    "lamination": ["layer_lamination", "edge_seal", "compression_clamp"],
    "software_build": ["unit_tests", "integration_tests", "fuzz_tests", "audit_logging"],
}

SCALE_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "small_pod": {"size_class": "handheld", "dimensions_cm": {"x": 25, "y": 15, "z": 8}, "mass_kg": 1.2},
    "small_node": {"size_class": "desktop", "dimensions_cm": {"x": 30, "y": 20, "z": 12}, "mass_kg": 2.0},
    "medium_robot": {"size_class": "desktop", "dimensions_cm": {"x": 60, "y": 40, "z": 30}, "mass_kg": 18.0},
    "small_panel": {"size_class": "desktop", "dimensions_cm": {"x": 30, "y": 40, "z": 1.2}, "mass_kg": 1.5},
    "coupon": {"size_class": "handheld", "dimensions_cm": {"x": 10, "y": 10, "z": 1.0}, "mass_kg": 0.25},
    "software": {"size_class": "micro", "dimensions_cm": {"x": 0, "y": 0, "z": 0}, "mass_kg": 0},
}


def ajani_engineering(domain: str) -> Dict[str, Any]:
    return {
        "agent": "Ajani",
        "focus": "materials + power + failure modes + tests",
        "stance": "Make it measurable and buildable (small to medium)."
    }


def minerva_context(domain: str) -> Dict[str, Any]:
    return {
        "agent": "Minerva",
        "focus": "purpose + environment metrics + safety/ethics",
        "stance": "Define what helping means and how you'll prove it."
    }


def hermes_validation(domain: str) -> Dict[str, Any]:
    return {
        "agent": "Hermes",
        "focus": "validation gates + security + logs",
        "stance": "No pillars = no tier. Everything versioned + auditable."
    }


def domain_pack(domain: str) -> Dict[str, Any]:
    if domain == "botany_pod":
        return {
            "scale": SCALE_DEFAULTS["small_pod"],
            "energy_options": POWER_LIBRARY["low_power_sensor"] + POWER_LIBRARY["passive"],
            "materials": MATERIAL_LIBRARY["botany_capsule"],
            "fabrication": FAB_LIBRARY["sealed_capsule"],
            "physics_mechanism_hint": "Water retention + controlled microclimate improves survival and growth rate.",
            "acceptance_tests": [
                "Survival test: days alive at reduced watering (log daily).",
                "Growth test: cm/day over 14 days under defined light/temp.",
                "Seal test: humidity stays within target range for 7 days.",
                "UV test: 72h exposure; no cracking/yellowing.",
            ],
            "failure_modes": [
                "Seal leak -> dehydration/mold",
                "Overheating in direct sun",
                "Root rot due to poor drainage",
            ],
        }

    if domain == "bio_archive_flower":
        return {
            "scale": {"size_class": "desktop", "dimensions_cm": {"x": 30, "y": 30, "z": 60}, "mass_kg": 3.5},
            "energy_options": POWER_LIBRARY["passive"] + POWER_LIBRARY["low_power_sensor"],
            "materials": MATERIAL_LIBRARY["botany_capsule"] + ["nfc_tag_optional", "qr_label"],
            "fabrication": FAB_LIBRARY["sealed_capsule"],
            "physics_mechanism_hint": "Sealed capsule stabilizes humidity/temperature to preserve biological samples/metadata.",
            "acceptance_tests": [
                "Drop test: 1m drop x5, no cracks, seal intact.",
                "Humidity drift test: indicator stays within band for 30 days.",
                "Ingress test: dust/moisture exposure (basic IP-style).",
            ],
            "failure_modes": [
                "Seal creep -> moisture ingress",
                "UV degradation -> brittleness",
                "Condensation -> biological loss",
            ],
        }

    if domain == "eco_robotics":
        return {
            "scale": SCALE_DEFAULTS["small_node"],
            "energy_options": POWER_LIBRARY["robotics_24v"],
            "materials": MATERIAL_LIBRARY["robotics_structural"],
            "fabrication": FAB_LIBRARY["rapid_proto"] + FAB_LIBRARY["structural_proto"],
            "physics_mechanism_hint": "Sensors detect environmental change; control loop triggers non-harmful responses (alerts/actions).",
            "acceptance_tests": [
                "24h uptime logging: no crashes, no corrupted data.",
                "Sensor drift check: <10% variance vs reference over 24h.",
                "Thermal check: enclosure stays <50C at avg load.",
                "Water/dust check: gasketed enclosure survives outdoor mist + dust.",
            ],
            "failure_modes": [
                "Sensor drift -> false readings",
                "Power brownout -> resets",
                "Ingress -> corrosion/shorts",
                "Loose wiring -> intermittent faults",
            ],
        }

    if domain == "medusa_transparent_mech":
        return {
            "scale": {"size_class": "desktop", "dimensions_cm": {"x": 80, "y": 40, "z": 40}, "mass_kg": 12.0},
            "energy_options": POWER_LIBRARY["robotics_24v"] + POWER_LIBRARY["robotics_48v"],
            "materials": MATERIAL_LIBRARY["transparent_structural"] + ["clear_pulley_wheels", "steel_cables_or_fishing_line_test"],
            "fabrication": FAB_LIBRARY["rapid_proto"] + ["cable_routing", "limit_switch_install"],
            "physics_mechanism_hint": "Cable-driven actuation transmits torque through transparent segments with pulleys and tension control.",
            "acceptance_tests": [
                "Hold test: hold 1kg at full reach for 30s without slip.",
                "Repeatability: return-to-point error <= 5mm for v0.",
                "Over-torque safety: stalls safely without cracking segments.",
                "Cable wear test: 200 cycles without fray/slip.",
            ],
            "failure_modes": [
                "Cable stretch -> lost precision",
                "Cracking at fastener points in clear plastic",
                "Heat buildup near motors/drivers",
            ],
        }

    if domain == "transparent_liquid_armor":
        return {
            "scale": SCALE_DEFAULTS["coupon"],
            "energy_options": POWER_LIBRARY["passive"],
            "materials": MATERIAL_LIBRARY["transparent_impact"],
            "fabrication": FAB_LIBRARY["lamination"],
            "physics_mechanism_hint": "Layer stack spreads impact; gel/STF increases resistance under rapid deformation.",
            "acceptance_tests": [
                "Drop test: fixed mass/height x10; record dent depth.",
                "Crack test: inspect for micro-cracks after impacts.",
                "Edge seal test: no leakage after compression for 24h.",
                "Clarity test: haze increase under stress (visual score).",
            ],
            "failure_modes": [
                "Edge seal failure -> leakage",
                "Crazing/cracks in polycarbonate",
                "Delamination between layers",
            ],
        }

    if domain == "crypto_security":
        return {
            "scale": SCALE_DEFAULTS["software"],
            "energy_options": POWER_LIBRARY["software"],
            "materials": MATERIAL_LIBRARY["crypto_components"],
            "fabrication": FAB_LIBRARY["software_build"],
            "physics_mechanism_hint": "Security property replaces physics: signed commands + replay protection + audit logs.",
            "acceptance_tests": [
                "Replay test: duplicate nonce rejected 100% of time.",
                "MITM simulation: invalid signature rejected.",
                "Latency benchmark: handshake/verify under target ms on phone.",
                "Audit: all privileged actions logged with timestamp + actor.",
            ],
            "failure_modes": [
                "Nonce reuse -> replay attack",
                "Key leakage -> device compromise",
                "Missing audit logs -> untraceable actions",
            ],
        }

    if domain == "bio_sim_human_performance":
        return {
            "scale": SCALE_DEFAULTS["software"],
            "energy_options": POWER_LIBRARY["software"],
            "materials": MATERIAL_LIBRARY["bio_sim_components"],
            "fabrication": FAB_LIBRARY["software_build"],
            "physics_mechanism_hint": "Simulation-only models of reflex/healing trade-offs; validated vs published ranges or training data.",
            "acceptance_tests": [
                "Model sanity: outputs within known physiological ranges.",
                "Uncertainty reporting: confidence intervals included.",
                "A/B training plan: predicts measurable change in reaction time over 4 weeks (sim).",
            ],
            "failure_modes": [
                "Overfitting -> false confidence",
                "No uncertainty -> bad decisions",
            ],
        }

    if domain == "biocompatible_microdevice_sim":
        return {
            "scale": SCALE_DEFAULTS["software"],
            "energy_options": POWER_LIBRARY["software"],
            "materials": MATERIAL_LIBRARY["bio_sim_components"] + ["biocompatibility_matrix", "external_control_concepts"],
            "fabrication": FAB_LIBRARY["software_build"],
            "physics_mechanism_hint": "Simulation/research framework for biocompatible micro-devices; no DIY medical build steps.",
            "acceptance_tests": [
                "Literature map: 50 sources tagged + summarized.",
                "Feasibility model: energy budget estimates with uncertainty.",
                "Governance: ethics gate required for any bio-related output.",
            ],
            "failure_modes": [
                "Speculation without evidence",
                "Unsafe implementation guidance (must be blocked)",
            ],
        }

    return {
        "scale": SCALE_DEFAULTS["small_node"],
        "energy_options": POWER_LIBRARY["passive"],
        "materials": MATERIAL_LIBRARY["robotics_structural"],
        "fabrication": FAB_LIBRARY["rapid_proto"],
        "physics_mechanism_hint": "Define mechanism + test + metric.",
        "acceptance_tests": ["Define 1 measurable test."],
        "failure_modes": ["Undefined requirements."],
    }


def guess_material_family(materials: List[str]) -> str:
    text = " ".join(materials).lower()
    if "software" in text or "keystore" in text:
        return "n/a_software"
    if "hydrogel" in text or "substrate" in text:
        return "polymer_bio"
    if "aluminum" in text or "steel" in text:
        return "metal_polymer_mix"
    if "polycarbonate" in text or "petg" in text or "acrylic" in text:
        return "polymer"
    return "composite"


def pick_top(items: List[str], n: int) -> List[str]:
    out = []
    for x in items:
        if x not in out:
            out.append(x)
        if len(out) >= n:
            break
    return out


def build_minimum_build_card(domain: str, title: str) -> Dict[str, Any]:
    pack = domain_pack(domain)

    energy_choice = pack["energy_options"][0] if pack["energy_options"] else {"source": "none", "avg_watts": 0, "peak_watts": 0}

    return {
        "title": title,
        "domain": domain,
        "scale": pack["scale"],
        "energy": {
            "power_needed": energy_choice["source"] not in ("none", "software"),
            "source": energy_choice["source"] if energy_choice["source"] != "software" else "other",
            "watts": energy_choice.get("peak_watts", 0),
        },
        "material": {
            "material_family": guess_material_family(pack["materials"]),
            "candidates": pick_top(pack["materials"], 5),
        },
        "fabrication": {
            "methods": pick_top(pack["fabrication"], 3),
            "tolerance_level": "normal",
        },
        "physics": {
            "mechanism": pack["physics_mechanism_hint"],
            "test_method": pack["acceptance_tests"][0] if pack["acceptance_tests"] else "bench_test",
            "success_metric": "Define numeric target (v0).",
            "flags": [],
        },
        "acceptance_tests": pack["acceptance_tests"],
        "failure_modes": pack["failure_modes"],
        "team_inputs": [ajani_engineering(domain), minerva_context(domain), hermes_validation(domain)],
    }


def apply_overrides(card: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    if overrides.get("prefer_transparent"):
        mats = card["material"]["candidates"]
        transparent_candidates = [
            "polycarbonate_sheet", "acrylic_sheet", "clear_petg", "transparent_tpu_gasket"
        ]
        for m in transparent_candidates:
            if m not in mats:
                mats.insert(0, m)
        card["material"]["candidates"] = mats[:7]

    if overrides.get("exclude_metal"):
        metal_terms = ["aluminum", "steel", "iron", "copper", "titanium", "brass", "metal"]
        mats = card.get("material", {}).get("candidates", [])
        mats = [m for m in mats if not any(mt in m.lower() for mt in metal_terms)]
        if not mats:
            mats = ["polycarbonate_sheet", "clear_petg", "abs_enclosure"]
        card["material"]["candidates"] = mats
        card["material"]["material_family"] = "polymer"

    if overrides.get("prefer_biopolymer"):
        bio_mats = ["transparent_biopolymer_capsule", "pla_bioplastic", "cellulose_composite", "clear_bio_resin"]
        mats = card.get("material", {}).get("candidates", [])
        for m in bio_mats:
            if m not in mats:
                mats.insert(0, m)
        card["material"]["candidates"] = mats[:7]

    if overrides.get("add_power_cell"):
        fabs = card.get("fabrication", {}).get("methods", [])
        if "power_cell_module_interface" not in fabs:
            fabs.append("power_cell_module_interface")
        card["fabrication"]["methods"] = fabs
        energy = card.get("energy", {})
        if energy.get("source") in ("none", "software"):
            energy["source"] = "battery"
            energy["power_needed"] = True
            energy["watts"] = energy.get("watts") or 25.0
        card["energy"] = energy

    if overrides.get("simulation_only"):
        card["simulation_only"] = True
        card["fabrication"]["methods"] = ["simulation_model", "software_validation"]
        card["fabrication"]["tolerance_level"] = "n/a_simulation"
        card.setdefault("intake_notes", [])
        if isinstance(card["intake_notes"], list):
            card["intake_notes"].append("SIMULATION ONLY: No physical build instructions. Outputs are models/data.")

    if overrides.get("externally_programmable"):
        card.setdefault("intake_notes", [])
        if isinstance(card["intake_notes"], list):
            card["intake_notes"].append("External programming interface required: API/wireless control layer.")

    return card
