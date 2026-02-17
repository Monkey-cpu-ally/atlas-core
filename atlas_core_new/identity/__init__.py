"""System identity and charter."""

from .charter import (
    SYSTEM_CODENAME,
    SYSTEM_VERSION,
    GENESIS_DATE,
    CORE_PRINCIPLES,
    PERSONA_OATHS,
    SystemIdentity,
    get_identity,
    verify_identity,
    get_oath,
    get_principles,
)
from .signatures import (
    AJANI_SIGNATURES,
    MINERVA_SIGNATURES,
    HERMES_SIGNATURES,
    get_signature,
    get_greeting,
    get_closing,
    wrap_response,
)
from .safety import (
    BLOCKED_INTENTS,
    BLOCKED_PATTERNS,
    verify_safety_integrity,
    is_blocked_intent,
    contains_blocked_pattern,
    safety_check,
)

__all__ = [
    "SYSTEM_CODENAME",
    "SYSTEM_VERSION",
    "GENESIS_DATE",
    "CORE_PRINCIPLES",
    "PERSONA_OATHS",
    "SystemIdentity",
    "get_identity",
    "verify_identity",
    "get_oath",
    "get_principles",
    "AJANI_SIGNATURES",
    "MINERVA_SIGNATURES",
    "HERMES_SIGNATURES",
    "get_signature",
    "get_greeting",
    "get_closing",
    "wrap_response",
    "BLOCKED_INTENTS",
    "BLOCKED_PATTERNS",
    "verify_safety_integrity",
    "is_blocked_intent",
    "contains_blocked_pattern",
    "safety_check",
]
