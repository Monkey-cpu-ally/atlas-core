"""
atlas_core/bots/profiles.py

GAIA-style bot classification system with strict, safe, scalable rules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set


class Domain(str, Enum):
    LAND = "LAND"
    WATER = "WATER"
    AIR = "AIR"
    INFRA = "INFRA"
    FAB = "FAB"


class BotClass(str, Enum):
    SCOUT = "SCOUT"        # sense/map/log only
    STATION = "STATION"    # fixed monitoring
    BUOY = "BUOY"          # floating monitoring
    SENTINEL = "SENTINEL"  # protective alerts, no force
    WORKER = "WORKER"      # safe tasks, approval required


@dataclass(frozen=True)
class ClassProfile:
    domain: Domain
    bot_class: BotClass
    default_sensors: List[str]
    allowed_actions: Set[str]
    requires_human_approval_for: Set[str]


PROFILES: Dict[str, ClassProfile] = {
    "POSEIDON-BUOY": ClassProfile(
        domain=Domain.WATER,
        bot_class=BotClass.BUOY,
        default_sensors=["pH", "turbidity", "water_temp", "gps"],
        allowed_actions={"sense", "log", "map", "sync", "sleep"},
        requires_human_approval_for={"deploy", "relocate"}
    ),
    "AETHER-STATION": ClassProfile(
        domain=Domain.AIR,
        bot_class=BotClass.STATION,
        default_sensors=["pm25", "co2", "voc", "air_temp", "humidity"],
        allowed_actions={"sense", "log", "sync", "sleep"},
        requires_human_approval_for={"deploy", "relocate"}
    ),
    "DEMETER-SCOUT": ClassProfile(
        domain=Domain.LAND,
        bot_class=BotClass.SCOUT,
        default_sensors=["soil_moisture", "soil_temp", "camera", "gps"],
        allowed_actions={"sense", "log", "map", "route", "sync", "sleep"},
        requires_human_approval_for={"deploy", "relocate"}
    ),
    "HERMES-SENTINEL": ClassProfile(
        domain=Domain.INFRA,
        bot_class=BotClass.SENTINEL,
        default_sensors=["gps", "accelerometer", "tamper", "camera"],
        allowed_actions={"sense", "log", "alert", "lockdown", "sync", "sleep"},
        requires_human_approval_for={"deploy", "relocate"}
    ),
}


def get_profile(name: str) -> ClassProfile | None:
    return PROFILES.get(name)


def list_profiles() -> List[str]:
    return list(PROFILES.keys())


def list_by_domain(domain: Domain) -> List[str]:
    return [k for k, v in PROFILES.items() if v.domain == domain]


def list_by_class(bot_class: BotClass) -> List[str]:
    return [k for k, v in PROFILES.items() if v.bot_class == bot_class]


def is_action_allowed(profile_name: str, action: str) -> bool:
    profile = PROFILES.get(profile_name)
    if not profile:
        return False
    return action in profile.allowed_actions


def requires_approval(profile_name: str, action: str) -> bool:
    profile = PROFILES.get(profile_name)
    if not profile:
        return True
    return action in profile.requires_human_approval_for
