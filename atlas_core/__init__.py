"""ATLAS Core v1 — modular cognitive backend.

A real Python package now (renamed from ``atlas-core`` so the dotted
import path actually works). Exposes the FastAPI router via
:mod:`atlas_core.app`.

Subpackages:
    cores            — Titan / Gaia / Mercury cognitive cores
    council          — lead/support/critic router + assembler
    teaching_engine  — 4-band depth lesson generator
    blueprint_engine — parallel mental simulation + 5-phase plan
    archive_engine   — PDF / ZIP / TXT scan → classify → summarize
    shield_core      — sanitize / quarantine / gates / identity anchor
    memory           — thread-safe in-memory store w/ DB-shaped interface

Mount on an existing FastAPI app::

    from atlas_core.app import atlas_router
    app.include_router(atlas_router, prefix="/api")
"""

__version__ = "1.0.0"

from .app import atlas_router  # noqa: F401  (re-export for convenience)

__all__ = ["atlas_router", "__version__"]
