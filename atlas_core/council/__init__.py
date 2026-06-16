# Council package — internal Atlas Core routing/assembly.
# `route_internal` is the canonical name post Phase 0 cleanup.
# `route` is kept as a backwards-compat alias for older imports
# (legacy: `from atlas_core.council import route`).
from .router import route_internal, assemble, CouncilDecision

# Alias preserves the original public name without renaming callers.
route = route_internal

__all__ = ["route_internal", "route", "assemble", "CouncilDecision"]
