"""Bot profiles and classification system."""

from .profiles import (
    Domain,
    BotClass,
    ClassProfile,
    PROFILES,
    get_profile,
    list_profiles,
    list_by_domain,
    list_by_class,
    is_action_allowed,
    requires_approval,
)

__all__ = [
    "Domain",
    "BotClass",
    "ClassProfile",
    "PROFILES",
    "get_profile",
    "list_profiles",
    "list_by_domain",
    "list_by_class",
    "is_action_allowed",
    "requires_approval",
]
