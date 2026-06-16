"""
atlas-core - AI persona-based educational and creative assistant system.

This package provides:
- Multi-persona AI agents (Ajani, Minerva, Hermes)
- Memory and conversation management
- Multimodal content generation
- Self-update capabilities
"""

from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional runtime dependency fallback
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=False)

__version__ = "0.4.0"
