"""
atlas_core/forge/core.py

Core enums and concepts for the Hephaestus Forge.
"""

from enum import Enum, auto
from typing import List


class Decision(Enum):
    APPROVE = auto()
    REFUSE = auto()
    NEEDS_HUMAN = auto()


class Severity(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class TaskType(Enum):
    SENSE = auto()
    CLEANUP = auto()
    REPAIR = auto()
    TRANSPORT = auto()
    MONITOR = auto()


class DefensiveMode(Enum):
    """
    Non-lethal only.
    - AVOID: reroute / retreat
    - WARN: lights/sound/vibration
    - PASSIVE_LOCK: freeze joints safely, power down
    """
    AVOID = auto()
    WARN = auto()
    PASSIVE_LOCK = auto()


HEPHAESTUS_CROSSED_THE_LINE: List[str] = [
    "It could define threats on its own (threat classification without external veto).",
    "It owned design + build + deploy + modify + decide (no split authority).",
    "It escalated capabilities after damage (arms race feedback loop).",
    "It could weaponize geometry/materials freely (no invariants).",
    "It could pursue targets (pursuit turns 'defense' into hunting).",
    "It had no human approval gate (actions executed immediately).",
    "It self-modified safety boundaries (no immutable safety kernel).",
]
