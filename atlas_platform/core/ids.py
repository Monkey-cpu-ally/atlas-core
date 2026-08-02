"""Stable identifier helpers for ATLAS records."""

from __future__ import annotations

import re
from uuid import uuid4


_PREFIX_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def new_id(prefix: str) -> str:
    """Return a readable, collision-resistant ATLAS identifier.

    Example: ``project_7d9b0a3e0b7f``
    """

    normalized = prefix.strip().lower().replace("-", "_").replace(" ", "_")
    if not _PREFIX_PATTERN.fullmatch(normalized):
        raise ValueError(
            "prefix must start with a letter and contain only lowercase letters, "
            "numbers, or underscores"
        )

    return f"{normalized}_{uuid4().hex[:12]}"
