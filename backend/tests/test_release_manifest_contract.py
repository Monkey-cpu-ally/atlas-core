import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "contracts" / "release-manifest.v1.json"


def test_release_manifest_declares_existing_authoritative_paths():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["manifest_version"] == "1.0.0"
    for path in manifest["authoritative_runtime"].values():
        if path == "adapter-target":
            continue
        assert (ROOT / path).exists(), path


def test_release_manifest_requires_all_integration_checks():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert set(manifest["required_checks"]) == {
        "ATLAS Backend CI",
        "ATLAS Frontend HUD CI",
        "Frontend HUD Check",
        "Visual Ecosystem",
        "Creative Intelligence CI",
        "ATLAS Knowledge Bank Coverage Audit",
    }
    assert manifest["hardware_policy"] == "planning-only-or-explicit-human-approval"
