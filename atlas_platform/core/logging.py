"""Logging configuration for ATLAS services."""

from __future__ import annotations

import logging
from typing import Optional


_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: str = "INFO", *, force: bool = False) -> None:
    """Configure process-wide logging with a consistent ATLAS format."""

    normalized = level.strip().upper()
    numeric_level: Optional[int] = getattr(logging, normalized, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unknown log level: {level}")

    logging.basicConfig(
        level=numeric_level,
        format=_DEFAULT_FORMAT,
        force=force,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger for an ATLAS module."""

    cleaned = name.strip()
    if not cleaned:
        raise ValueError("logger name cannot be empty")

    return logging.getLogger(f"atlas.{cleaned}")
