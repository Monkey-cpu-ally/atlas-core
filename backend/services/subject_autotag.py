"""Subject auto-tagger — deterministic keyword → subject-slug matcher.

Used by the intake / worldwatch / transcript ingestion pipelines to add
`subject:<slug>` tags automatically at write-time. Not an LLM call —
just a curated keyword map against the 22 canonical subjects so we
don't pay LLM cost on every ingest.

Returns the *union* of matched subject tags (a document can belong to
several subjects, e.g. "solid-state battery" → energy_systems +
materials_science + chemistry).
"""
from __future__ import annotations

import re
from typing import List, Sequence

# --- Keyword rules ---------------------------------------------------------
# Small, high-signal phrases only. False-positive rate matters more here
# than recall (an untagged doc is harmless; a mistagged one pollutes the
# subject-faceted queries).
_RULES: dict = {
    "aerospace_engineering": [
        r"\baerospace\b", r"\bpropulsion\b", r"\brocket\b", r"\bspacecraft\b",
        r"\bthrust vector\b", r"\baeroelastic\b", r"\bturbofan\b", r"\bhypersonic\b",
        r"\bnasa\b", r"\bspacex\b", r"\bblue origin\b",
    ],
    "agriculture": [
        r"\bagricultur", r"\bcrop\b", r"\bcrops\b", r"\bhydroponic", r"\bsoil\b",
        r"\birrigation\b", r"\bplant health\b", r"\bfertili[sz]er\b", r"\bagritech\b",
        r"\bprecision farm", r"\bharvest\b",
    ],
    "architecture": [
        r"\barchitectur", r"\burban plan", r"\bfa[cç]ade\b", r"\bbuilding envelope\b",
        r"\bpassive house\b", r"\bstructural design\b", r"\brefurbish", r"\bhousing\b",
    ],
    "artificial_intelligence": [
        r"\bmachine learning\b", r"\bneural network", r"\bdeep learning\b",
        r"\btransformer\b", r"\bllm\b", r"\bagent framework\b", r"\breinforcement learning\b",
        r"\bfoundation model\b", r"\bfine[- ]tun", r"\brag\b",
    ],
    "biology": [
        r"\bcell biology\b", r"\bgene(?:tic|s|ome)?\b", r"\becology\b", r"\bneuron\b",
        r"\bprotein\b", r"\bmicrobiol", r"\bevolutionary\b", r"\bmitochondri",
    ],
    "business": [
        r"\bsupply chain\b", r"\blean\b", r"\brevenue\b", r"\bmarket fit\b",
        r"\bventure\b", r"\bstartup\b", r"\bfunding round\b",
    ],
    "chemistry": [
        r"\belectrolyte\b", r"\bcatalys", r"\breaction rate\b", r"\bcarbonate\b",
        r"\borganic chemistry\b", r"\binorganic\b", r"\bmolecul", r"\bpolymer",
        r"\bsulfide\b", r"\bhydrolysis\b",
    ],
    "computer_science": [
        r"\balgorithm\b", r"\bdata structure\b", r"\bcompiler\b", r"\bdistributed system",
        r"\bkubernetes\b", r"\bdatabase engine\b", r"\bconcurrency\b",
    ],
    "creative_writing": [
        r"\bnarrative arc\b", r"\bcharacter arc\b", r"\bworldbuilding\b",
        r"\bprose\b", r"\bscreenplay\b",
    ],
    "earth_climate": [
        r"\bclimate\b", r"\bgeology\b", r"\btectonic\b", r"\batmospher",
        r"\bocean current", r"\bcarbon cycle\b", r"\bsea level\b", r"\bgreenhouse gas\b",
    ],
    "electrical_engineering": [
        r"\bcircuit\b", r"\bpcb\b", r"\bfpga\b", r"\bpower electronics\b",
        r"\bmicrocontroller\b", r"\besp32\b", r"\brf\b", r"\bantenna\b",
    ],
    "energy_systems": [
        r"\bbattery\b", r"\bcell chemistry\b", r"\bsolid[- ]state batter",
        r"\bphotovoltaic\b", r"\bfuel cell\b", r"\bwh/kg\b", r"\bwatt[- ]hour",
        r"\bgrid storage\b", r"\benergy density\b",
    ],
    "game_design": [
        r"\bgame loop\b", r"\blevel design\b", r"\bgame engine\b", r"\bunity\b",
        r"\bunreal engine\b", r"\bgame mechanic",
    ],
    "history_philosophy": [
        r"\bepistemolog", r"\bphilosoph", r"\bscientific method\b", r"\bethics of\b",
        r"\bhistory of science\b",
    ],
    "mathematics": [
        r"\btopolog", r"\btensor\b", r"\bdifferential equation\b", r"\bmanifold\b",
        r"\bprobability distribution\b", r"\bmatrix\b", r"\beigenvalue\b",
    ],
    "materials_science": [
        r"\bpolymer\b", r"\bcomposite\b", r"\bcrystalline\b", r"\bceramic\b",
        r"\banode\b", r"\bcathode\b", r"\bmetallurg",
    ],
    "mechanical_engineering": [
        r"\bcnc\b", r"\bmachining\b", r"\bcad\b", r"\bfea\b", r"\bthermal management\b",
        r"\btorque\b", r"\bgear\b", r"\bbearing\b", r"\bfatigue\b",
    ],
    "medicine_health": [
        r"\bclinical trial\b", r"\bdiagnos", r"\bphysiolog", r"\bpublic health\b",
        r"\bvaccin", r"\bepidemiol",
    ],
    "physics": [
        r"\bquantum\b", r"\brelativity\b", r"\bparticle physics\b", r"\bmagnetic field\b",
        r"\bthermodynamic", r"\bcondensed matter\b",
    ],
    "psychology_cognition": [
        r"\bcognit", r"\bperception\b", r"\bbehaviou?ral\b", r"\bneuroscience\b",
        r"\bdecision[- ]making\b",
    ],
    "robotics": [
        r"\brobot\b", r"\brobotic", r"\bslam\b", r"\bmanipulator\b", r"\bactuator\b",
        r"\bhumanoid\b", r"\brover\b", r"\bdrone\b", r"\bautonomous vehicle",
    ],
    "sustainability": [
        r"\bcarbon captur", r"\brecycling\b", r"\bcircular economy\b", r"\blife[- ]cycle assess",
        r"\brenewable energy\b", r"\bnet[- ]zero\b",
    ],
}

# Pre-compile
_COMPILED = {
    slug: [re.compile(p, re.IGNORECASE) for p in patterns]
    for slug, patterns in _RULES.items()
}


def tag_content(text: str, extra_tags: Sequence[str] = ()) -> List[str]:
    """Return subject tags (`subject:<slug>`) that match the given text.
    Order is deterministic (subject order in _RULES) so tests are stable.
    """
    if not text:
        return list(extra_tags)
    matched: List[str] = []
    for slug, regexes in _COMPILED.items():
        if any(rx.search(text) for rx in regexes):
            matched.append(f"subject:{slug}")
    for t in extra_tags:
        if t not in matched:
            matched.append(t)
    return matched


def matched_subject_slugs(text: str) -> List[str]:
    """Just the slugs (no `subject:` prefix), for use in structured fields."""
    return [t.split(":", 1)[1] for t in tag_content(text) if t.startswith("subject:")]
