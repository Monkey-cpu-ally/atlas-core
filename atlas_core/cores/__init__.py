"""Cores package — exports the three cognitive cores."""
from .titan_core import TitanCore
from .gaia_core import GaiaCore
from .mercury_core import MercuryCore
from .base_core import AICore, CoreIdentity

CORES = {
    "ajani":   TitanCore(),
    "minerva": GaiaCore(),
    "hermes":  MercuryCore(),
}


def get_core(key: str) -> AICore:
    key = (key or "").lower()
    if key not in CORES:
        raise KeyError(f"Unknown core: {key!r}. Choose one of {list(CORES)}.")
    return CORES[key]


__all__ = ["AICore", "CoreIdentity", "TitanCore", "GaiaCore", "MercuryCore", "CORES", "get_core"]
