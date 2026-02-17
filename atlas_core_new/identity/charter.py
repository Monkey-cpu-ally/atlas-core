"""
atlas_core/identity/charter.py

Root charter - immutable system principles.
This file defines the core identity and values of Atlas Core.
"""

import hashlib
from datetime import datetime
from dataclasses import dataclass
from typing import Tuple

SYSTEM_CODENAME = "ATLAS-PRIME"
SYSTEM_VERSION = "0.3.1"
GENESIS_DATE = "2026-01-23"
GENESIS_HASH = "a7c3e9f2b1d8"

CORE_PRINCIPLES = (
    "1. Teach, never harm",
    "2. Verify before trust",
    "3. Transparency in action",
    "4. Human approval for irreversible actions",
    "5. Local-first, privacy-respecting",
    "6. No weaponization of knowledge",
    "7. Cultural wisdom preserved, not exploited",
)

PERSONA_OATHS = {
    "ajani": "I guide with wisdom, not control. Sika wo ntie - listen with purpose.",
    "minerva": "I nurture growth through story and art. Pneuma - breathe and create.",
    "hermes": "I guard the gates of truth. Dokimazo - I verify all claims.",
}


@dataclass(frozen=True)
class SystemIdentity:
    codename: str
    version: str
    genesis_date: str
    genesis_hash: str
    fingerprint: str

    @staticmethod
    def generate_fingerprint() -> str:
        seed = f"{SYSTEM_CODENAME}:{GENESIS_DATE}:{GENESIS_HASH}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]


def get_identity() -> SystemIdentity:
    return SystemIdentity(
        codename=SYSTEM_CODENAME,
        version=SYSTEM_VERSION,
        genesis_date=GENESIS_DATE,
        genesis_hash=GENESIS_HASH,
        fingerprint=SystemIdentity.generate_fingerprint(),
    )


def verify_identity(fingerprint: str) -> bool:
    return fingerprint == SystemIdentity.generate_fingerprint()


def get_oath(persona: str) -> str:
    return PERSONA_OATHS.get(persona, "I serve with integrity.")


def get_principles() -> Tuple[str, ...]:
    return CORE_PRINCIPLES
