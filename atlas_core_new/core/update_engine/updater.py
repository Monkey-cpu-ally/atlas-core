"""
atlas_core/core/update_engine/updater.py

Safe self-update skeleton.
"""

from dataclasses import dataclass


@dataclass
class UpdateStatus:
    ok: bool
    message: str
    current_version: str
    available_version: str | None = None


class Updater:
    """
    SAFE self-update skeleton.
    Real self-updates must verify signatures and avoid arbitrary code execution.
    """
    def __init__(self, current_version: str, update_url: str, public_key_pem: str):
        self.current_version = current_version
        self.update_url = update_url
        self.public_key_pem = public_key_pem

    def check(self):
        if not self.update_url:
            return UpdateStatus(True, "No update URL configured.", self.current_version).__dict__
        return UpdateStatus(True, "Update check stub (wire to release feed).", self.current_version, None).__dict__

    def apply(self):
        return {"ok": False, "message": "Update apply is stubbed for safety. Implement staged + signed updates."}
