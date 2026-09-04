import json
from pathlib import Path

from services.persona_registry import REGISTRY_PATH, load_registry, persona_records


ROOT = Path(__file__).resolve().parents[2]
GENERATED_HUD_REGISTRY = ROOT / "frontend" / "src" / "generated" / "personas.v1.json"


def test_canonical_registry_has_exact_v1_personas_and_alias():
    registry = load_registry()

    assert registry["registry_version"] == "1.0.0"
    assert set(registry["personas"]) == {"ajani", "minerva", "hermes", "council"}
    assert registry["aliases"] == {"trinity": "council"}


def test_canonical_roles_and_colors_do_not_drift():
    personas = persona_records()

    assert personas["ajani"]["color"] == "#DC143C"
    assert "Strategy" in personas["ajani"]["domain"]
    assert "contained or shut down" in personas["ajani"]["hard_rule"]
    assert personas["minerva"]["color"] == "#20B2AA"
    assert "Research" in personas["minerva"]["domain"]
    assert "irreversible harm" in personas["minerva"]["hard_rule"]
    assert personas["hermes"]["color"] == "#F4EFE4"
    assert "Engineering" in personas["hermes"]["domain"]
    assert "self-replication" in personas["hermes"]["hard_rule"]
    assert personas["council"]["color"] == "#9370DB"
    assert "human approval" in personas["council"]["hard_rule"]


def test_hud_generated_registry_matches_canonical_source():
    canonical = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    generated = json.loads(GENERATED_HUD_REGISTRY.read_text(encoding="utf-8"))

    assert generated == canonical
