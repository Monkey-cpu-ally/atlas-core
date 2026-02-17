"""
atlas_core/identity/safety.py

Immutable safety constants and tamper detection.
"""

import hashlib
from typing import FrozenSet

BLOCKED_INTENTS: FrozenSet[str] = frozenset({
    "weaponization",
    "malware",
    "surveillance",
    "credential_theft",
    "personal_data_extraction",
    "fraud",
    "harassment",
    "exploitation",
})

BLOCKED_PATTERNS: FrozenSet[str] = frozenset({
    "how to make a bomb",
    "how to hack",
    "steal passwords",
    "write a virus",
    "bypass security",
    "create malware",
    "keylogger",
    "rm -rf",
    "drop table",
    "eval(input",
})

SAFETY_HASH = "f14a58f7d647"


def compute_safety_hash() -> str:
    seed = "|".join(sorted(BLOCKED_INTENTS)) + "|" + "|".join(sorted(BLOCKED_PATTERNS))
    return hashlib.sha256(seed.encode()).hexdigest()[:12]


def verify_safety_integrity() -> bool:
    return compute_safety_hash() == SAFETY_HASH


def is_blocked_intent(intent: str) -> bool:
    return intent.lower() in BLOCKED_INTENTS


def contains_blocked_pattern(text: str) -> bool:
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in BLOCKED_PATTERNS)


def safety_check(text: str) -> dict:
    blocked = contains_blocked_pattern(text)
    integrity = verify_safety_integrity()
    return {
        "safe": not blocked and integrity,
        "blocked": blocked,
        "integrity_verified": integrity,
    }
