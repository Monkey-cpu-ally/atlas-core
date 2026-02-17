"""
atlas_core/core/personas/registry.py

Persona registry - simple lookup by key.
"""

from .definitions import AJANI, MINERVA, HERMES, PersonaDef


class PersonaRegistry:
    def __init__(self):
        self._defs = {p.key: p for p in [AJANI, MINERVA, HERMES]}

    def get(self, key: str) -> PersonaDef:
        key = (key or "ajani").lower().strip()
        return self._defs.get(key, AJANI)
