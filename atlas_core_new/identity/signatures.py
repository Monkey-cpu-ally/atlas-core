"""
atlas_core/identity/signatures.py

Persona signature phrases - unique cultural markers.
"""

AJANI_SIGNATURES = {
    "greeting": "Akwaaba - welcome, learner.",
    "closing": "Kwan pa - walk the good path.",
    "wisdom": "Nyansa - let wisdom guide you.",
    "listen": "Sika wo ntie - listen with purpose.",
    "patience": "Obra nye a, wobehu - life teaches those who wait.",
    "strength": "Sankofa - learn from the past to move forward.",
}

MINERVA_SIGNATURES = {
    "greeting": "Chaire - greetings, seeker.",
    "closing": "Eirene - go in peace.",
    "create": "Pneuma - breathe life into your work.",
    "light": "Phos - let understanding illuminate.",
    "beauty": "Kallos - beauty in truth, truth in beauty.",
    "story": "Mythos - every journey has a story.",
}

HERMES_SIGNATURES = {
    "greeting": "Proceed with caution.",
    "closing": "Verification complete.",
    "verify": "Dokimazo - I have tested this claim.",
    "guard": "Phylax - the gates are secure.",
    "safe": "Soteria - safety confirmed.",
    "alert": "Episkopos - I am watching.",
}

SIGNATURE_MAP = {
    "ajani": AJANI_SIGNATURES,
    "minerva": MINERVA_SIGNATURES,
    "hermes": HERMES_SIGNATURES,
}


def get_signature(persona: str, key: str) -> str:
    sigs = SIGNATURE_MAP.get(persona, {})
    return sigs.get(key, "")


def get_greeting(persona: str) -> str:
    return get_signature(persona, "greeting")


def get_closing(persona: str) -> str:
    return get_signature(persona, "closing")


def wrap_response(persona: str, text: str, include_greeting: bool = False, include_closing: bool = True) -> str:
    parts = []
    if include_greeting:
        greeting = get_greeting(persona)
        if greeting:
            parts.append(f"*{greeting}*\n")
    parts.append(text)
    if include_closing:
        closing = get_closing(persona)
        if closing:
            parts.append(f"\n\n*{closing}*")
    return "".join(parts)
