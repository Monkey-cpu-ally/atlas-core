"""
atlas_core/pipeline/bot_files.py

Bot folder and spec file management.
"""

import json
from pathlib import Path
from ..bots.profiles import PROFILES

BOTS_DIR = Path("atlas_core_new/bots/instances")


def bot_folder(bot_name: str) -> Path:
    return BOTS_DIR / bot_name.lower().replace("-", "_")


def load_spec(bot_name: str) -> dict:
    path = bot_folder(bot_name) / "spec.json"
    return json.loads(path.read_text()) if path.exists() else {}


def ensure_bot_files(bot_name: str) -> None:
    if bot_name not in PROFILES:
        raise ValueError(f"Bot type not registered: {bot_name}")

    folder = bot_folder(bot_name)
    folder.mkdir(parents=True, exist_ok=True)

    spec_path = folder / "spec.json"
    if not spec_path.exists():
        profile = PROFILES[bot_name]
        spec = {
            "name": bot_name,
            "version": "1.0",
            "generation": "Gen-1",
            "domain": profile.domain.value,
            "class": profile.bot_class.value,
            "sensors": profile.default_sensors,
            "mission": "TBD",
            "environment": "TBD",
            "safety_rules": [
                "no wildlife interaction",
                "no sharp tools",
                "stop if lifted",
                "local-first",
                "human approval for deployment"
            ],
            "allowed_actions": sorted(list(profile.allowed_actions))
        }
        spec_path.write_text(json.dumps(spec, indent=2))

    history = folder / "history.log"
    if not history.exists():
        history.write_text("[INIT] Blueprint registered\n")


def append_history(bot_name: str, entry: str) -> None:
    folder = bot_folder(bot_name)
    history = folder / "history.log"
    if history.exists():
        with open(history, "a") as f:
            f.write(f"{entry}\n")


def update_spec(bot_name: str, updates: dict) -> dict:
    spec = load_spec(bot_name)
    spec.update(updates)
    path = bot_folder(bot_name) / "spec.json"
    path.write_text(json.dumps(spec, indent=2))
    return spec
