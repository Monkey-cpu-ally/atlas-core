from __future__ import annotations
from typing import Dict, Any, Tuple, List
import re


DOMAIN_RULES = [
    ("botany_pod", [
        "plant pod", "rapid grow", "seed pod", "hydrogel", "root matrix", "survive", "drought",
        "soil pod", "microclimate", "mycorrh", "substrate", "seedling"
    ]),
    ("bio_archive_flower", [
        "metal flower", "flower capsule", "seed vault", "dna storage", "archive", "capsule",
        "preserve", "viability", "nfc", "qr", "specimen"
    ]),
    ("eco_robotics", [
        "green bot", "eco bot", "environment", "sensor node", "air quality", "water quality",
        "turbidity", "co2", "pm2.5", "crawler", "drone", "robot", "gaia", "poseidon", "aether"
    ]),
    ("medusa_transparent_mech", [
        "medusa", "doc ock", "octopus arms", "tentacles", "transparent arms", "spider verse",
        "cable driven", "pulley", "actuator", "arm rig"
    ]),
    ("transparent_liquid_armor", [
        "liquid armor", "transparent armor", "shear thick", "stf", "gel armor",
        "impact panel", "polycarbonate", "clear gel", "panel", "coupon test"
    ]),
    ("crypto_security", [
        "hermes", "encryption", "quantum", "keys", "signed", "signature", "handshake",
        "pqc", "post-quantum", "mitm", "replay", "nonce", "audit log"
    ]),
    ("bio_sim_human_performance", [
        "human enhancement", "reflex", "healing", "performance", "reaction time",
        "training optimizer", "recovery"
    ]),
    ("biocompatible_microdevice_sim", [
        "nanotech", "swarm", "biocompatible", "in body", "programmable", "inductive",
        "bioelectric", "kinetic energy", "microdevice", "microrobot"
    ]),
]

PRIORITY_KEYWORDS: Dict[str, int] = {
    "medusa": 6,
    "doc ock": 6,
    "spider verse": 6,
    "liquid armor": 5,
    "transparent armor": 5,
    "nanotech": 4,
    "biocompatible": 4,
    "plant pod": 4,
    "seed vault": 4,
    "metal flower": 4,
}

SIMULATION_HINTS = ["simulation", "sim-only", "model", "theory", "research framework"]

NEGATION_PATTERNS = [
    (r"\bnot\s+metal\b", "Material exclusion: no metal components."),
    (r"\bnot\s+(?:green|red|blue|black|white)\b", None),
    (r"\bno\s+metal\b", "Material exclusion: no metal components."),
    (r"\bno\s+wires?\b", "Constraint: wireless/no-wire design preferred."),
    (r"\bno\s+battery\b", "Energy constraint: passive/harvested power preferred."),
]


def normalize(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^a-z0-9\s\-\+/]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def score_domain(text: str, keywords: List[str]) -> int:
    score = 0
    for kw in keywords:
        if kw in text:
            bonus = PRIORITY_KEYWORDS.get(kw, 2)
            score += bonus
    return score


def detect_domain(user_text: str) -> Tuple[str, Dict[str, Any]]:
    t = normalize(user_text)

    best_domain = "eco_robotics"
    best_score = -1
    scores: Dict[str, int] = {}
    ranked: List[Dict[str, Any]] = []

    for domain, kws in DOMAIN_RULES:
        s = score_domain(t, kws)
        scores[domain] = s
        if s > 0:
            ranked.append({"domain": domain, "score": s})
        if s > best_score:
            best_score = s
            best_domain = domain

    if best_score <= 0:
        best_domain = "eco_robotics"

    ranked.sort(key=lambda x: x["score"], reverse=True)
    secondary = [r["domain"] for r in ranked[1:4] if r["score"] > 0]

    is_sim = any(h in t for h in SIMULATION_HINTS)
    if is_sim and best_domain in ("bio_sim_human_performance", "biocompatible_microdevice_sim"):
        pass
    elif is_sim:
        for r in ranked:
            if r["domain"] in ("bio_sim_human_performance", "biocompatible_microdevice_sim"):
                if r["score"] > 0:
                    secondary = [s for s in secondary if s != r["domain"]]
                    secondary.insert(0, r["domain"])
                break

    meta = {
        "domain_scores": scores,
        "matched_domain": best_domain,
        "secondary_domains": secondary,
        "simulation_requested": is_sim,
        "multi_domain": len(ranked) > 1,
    }
    return best_domain, meta


def extract_title(user_text: str) -> str:
    lines = [ln.strip() for ln in user_text.splitlines() if ln.strip()]
    if lines:
        first = lines[0]
        clean = re.sub(r"[.:;,!?]+$", "", first).strip()
        return (clean[:80] + "\u2026") if len(clean) > 80 else clean
    t = normalize(user_text)
    return (t[:60] + "\u2026") if len(t) > 60 else (t or "Untitled Project")


def infer_scale_hint(user_text: str) -> str:
    t = normalize(user_text)
    if any(x in t for x in ["micro", "tiny", "wearable", "handheld", "pocket"]):
        return "small"
    if any(x in t for x in ["room", "lab", "workshop", "medium", "arm rig"]):
        return "medium"
    if "small" in t and "medium" in t:
        return "small_to_medium"
    if "small" in t:
        return "small"
    return "small_to_medium"


def detect_negations(user_text: str) -> List[str]:
    t = user_text.lower()
    notes = []
    for pattern, note in NEGATION_PATTERNS:
        match = re.search(pattern, t)
        if match:
            if note:
                notes.append(note)
            else:
                matched_text = match.group(0)
                color_match = re.search(r"\b(green|red|blue|black|white)\b", matched_text)
                if color_match:
                    color = color_match.group(1)
                    notes.append(f"Brand constraint: '{color}' refers to function/concept, not literal color.")
    return notes


def detect_material_exclusions(user_text: str) -> List[str]:
    t = user_text.lower()
    excluded = []
    if re.search(r"\bnot\s+metal\b|\bno\s+metal\b|\bplastic\b.{0,20}\bnot\s+metal\b", t):
        excluded.append("metal")
    if re.search(r"\bnot\s+wood\b|\bno\s+wood\b", t):
        excluded.append("wood")
    return excluded


def attach_user_constraints(card: Dict[str, Any], user_text: str) -> Dict[str, Any]:
    t = normalize(user_text)
    notes: List[str] = []

    if "transparent" in t or "clear" in t:
        notes.append("Aesthetic/material constraint: transparent/clear components preferred.")
    notes.extend(detect_negations(user_text))
    if "small" in t or "medium" in t:
        notes.append("Scale constraint: start small-to-medium prototypes.")
    if "power cell" in t:
        notes.append("Integration: consider power cell module interface (removable).")
    if "liquid armor" in t:
        notes.append("Armor constraint: transparent impact stack (polycarbonate + gel/STF + elastomer).")
    if "plug" in t and ("module" in t or "robotics" in t):
        notes.append("Integration: modular plug-in interface for cross-module compatibility.")

    if card.get("domain") in ("bio_sim_human_performance", "biocompatible_microdevice_sim"):
        notes.append("Safety: simulation-only outputs (no real-world medical build instructions).")

    excluded_materials = detect_material_exclusions(user_text)
    if excluded_materials:
        mats = card.get("material", {}).get("candidates", [])
        metal_terms = ["aluminum", "steel", "iron", "copper", "titanium", "brass"]
        if "metal" in excluded_materials:
            mats = [m for m in mats if not any(mt in m.lower() for mt in metal_terms)]
            card["material"]["candidates"] = mats
            notes.append("Material exclusion applied: removed metal candidates.")

    scale_hint = infer_scale_hint(user_text)
    card["intake_notes"] = notes
    card["intake_scale_hint"] = scale_hint

    scale_map = {"small": "handheld", "medium": "desktop", "small_to_medium": "handheld"}
    if scale_hint in scale_map and card.get("scale", {}).get("size_class") in ("micro", None):
        card["scale"]["size_class"] = scale_map[scale_hint]

    return card


def detect_overrides(user_text: str) -> Dict[str, Any]:
    t = user_text.lower()
    overrides: Dict[str, Any] = {
        "prefer_transparent": ("transparent" in t or "clear" in t),
        "scale_bias": infer_scale_hint(user_text),
    }
    if re.search(r"\bnot\s+metal\b|\bno\s+metal\b", t):
        overrides["exclude_metal"] = True
    if "power cell" in t or "power module" in t:
        overrides["add_power_cell"] = True
    if any(h in t for h in SIMULATION_HINTS) or "simulation only" in t or "sim only" in t:
        overrides["simulation_only"] = True
    if "biopolymer" in t:
        overrides["prefer_biopolymer"] = True
    if "externally programmable" in t or "external program" in t:
        overrides["externally_programmable"] = True
    return overrides


def split_into_projects(raw_text: str) -> List[str]:
    blocks: List[str] = []
    lines = raw_text.strip().splitlines()
    current: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                blocks.append("\n".join(current))
                current = []
            continue

        is_header = bool(re.match(
            r"^(?:[-*\u2022]\s|(?:\d+[\.\)]\s)|(?:[A-Z][a-z]+\s(?:project|system|module|bot|armor|flower|enhancement)):)",
            stripped
        ))

        if is_header and current:
            joined = "\n".join(current)
            if len(joined.strip()) > 10:
                blocks.append(joined)
            current = [stripped]
        else:
            current.append(stripped)

    if current:
        joined = "\n".join(current)
        if len(joined.strip()) > 10:
            blocks.append(joined)

    if not blocks and raw_text.strip():
        chunks = re.split(r"\n{2,}", raw_text.strip())
        blocks = [c.strip() for c in chunks if len(c.strip()) > 10]

    if not blocks and raw_text.strip():
        blocks = [raw_text.strip()]

    return blocks
