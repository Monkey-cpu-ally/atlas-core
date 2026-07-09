# ATLAS Core

The Core package provides shared infrastructure used by every ATLAS subsystem.

Responsibilities:
- Unique ID generation
- Configuration loading
- Logging
- Validation helpers
- Shared constants
- Time utilities
- Version information

Design goal: every subsystem depends on Core, while Core depends on none of them.
