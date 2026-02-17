"""
atlas_core/core/versioning.py

Version tracking for Atlas Core.
"""

from dataclasses import dataclass
from pathlib import Path

VERSION_FILE = Path(__file__).parent.parent / "vault" / "version.txt"


@dataclass
class VersionInfo:
    current: str


def get_version() -> VersionInfo:
    if not VERSION_FILE.exists():
        VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        VERSION_FILE.write_text("0.1.0")
    return VersionInfo(current=VERSION_FILE.read_text().strip())


def set_version(v: str) -> None:
    VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    VERSION_FILE.write_text(v.strip())
