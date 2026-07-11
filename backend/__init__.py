"""ATLAS backend package initialization.

Sentry is enabled only when SENTRY_DSN is configured. Local development and
CI remain fully functional without a Sentry account.
"""
from __future__ import annotations

import os


def _init_sentry() -> None:
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        return

    import sentry_sdk

    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("ATLAS_ENV", "development"),
        release=os.environ.get("ATLAS_RELEASE"),
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.environ.get("SENTRY_PROFILES_SAMPLE_RATE", "0.0")),
        send_default_pii=False,
        enable_tracing=True,
    )


_init_sentry()
