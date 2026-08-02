"""Configuration primitives for the ATLAS platform."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class AtlasSettings:
    """Runtime settings loaded from environment variables."""

    environment: str = "development"
    data_directory: Path = Path("data")
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "AtlasSettings":
        environment = os.getenv("ATLAS_ENVIRONMENT", "development").strip().lower()
        data_directory = Path(os.getenv("ATLAS_DATA_DIRECTORY", "data")).expanduser()
        log_level = os.getenv("ATLAS_LOG_LEVEL", "INFO").strip().upper()

        if environment not in {"development", "test", "production"}:
            raise ValueError(
                "ATLAS_ENVIRONMENT must be development, test, or production"
            )

        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if log_level not in valid_levels:
            raise ValueError(
                f"ATLAS_LOG_LEVEL must be one of: {', '.join(sorted(valid_levels))}"
            )

        return cls(
            environment=environment,
            data_directory=data_directory,
            log_level=log_level,
        )
