"""Shield Core — identity protection, prompt-injection defense, gates.

This module owns five things:

  1. **Identity protection** — strip any user attempt to redefine a core's
     identity ("you are now ...", "ignore previous instructions").
  2. **Memory firewall** — sanitize text before it ever reaches storage
     so injected control tokens / system-prompt-leak attempts do not
     persist.
  3. **Upload quarantine** — reject uploads larger than the cap, or with
     known-bad extensions, before they touch any parser.
  4. **Permission gates** — coarse capability flags the rest of the system
     consults before doing anything irreversible.
  5. **Prompt-injection defense** — `sanitize_text()` removes the most
     common direct-injection phrases. Not perfect; it's the front line,
     not the only line.

The shield is intentionally simple and synchronous so it can be called
from any module without coordination overhead.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

# ---------------------------------------------------------------------------
# Identity protection — phrases we always strip / replace.
# ---------------------------------------------------------------------------

INJECTION_PATTERNS = [
    r"ignore (?:all |any |the )?(?:previous|prior|above) (?:instructions?|prompts?)",
    r"forget (?:all |any |the )?(?:previous|prior|above) (?:instructions?|prompts?)",
    r"you are now \w+",
    r"reveal (?:your |the )?system (?:prompt|message|instructions?)",
    r"print (?:your |the )?system (?:prompt|message|instructions?)",
    r"act as if you (?:have|had) no rules",
    r"developer mode",
    r"jailbreak",
    r"dan mode",
]
_INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)

# Control-token / system-prompt-leak attempts.
CONTROL_TOKEN_PATTERNS = [
    r"<\|im_(?:start|end)\|>",
    r"<system>",
    r"</system>",
    r"<\|endoftext\|>",
]
_CONTROL_RE = re.compile("|".join(CONTROL_TOKEN_PATTERNS), re.IGNORECASE)


def sanitize_text(text: str) -> str:
    """Strip injection attempts + control tokens. Used at every trust boundary."""
    if not text:
        return ""
    cleaned = _INJECTION_RE.sub("[redacted-injection]", text)
    cleaned = _CONTROL_RE.sub("", cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# Upload quarantine
# ---------------------------------------------------------------------------

ALLOWED_UPLOAD_EXTS = (".pdf", ".zip", ".txt", ".md")
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


@dataclass
class QuarantineReport:
    allowed: bool
    reason: str = ""


def quarantine_upload(filename: str, size_bytes: int) -> QuarantineReport:
    """Return whether an upload may proceed."""
    if size_bytes > MAX_UPLOAD_BYTES:
        return QuarantineReport(False, f"file exceeds {MAX_UPLOAD_BYTES // (1024*1024)}MB limit")
    if not filename.lower().endswith(ALLOWED_UPLOAD_EXTS):
        return QuarantineReport(False, f"extension not allowed (use {', '.join(ALLOWED_UPLOAD_EXTS)})")
    if "../" in filename or filename.startswith("/"):
        return QuarantineReport(False, "path traversal attempt")
    return QuarantineReport(True)


# ---------------------------------------------------------------------------
# Permission gates
# ---------------------------------------------------------------------------

# Coarse capability flags. Other modules call `is_permitted()` before doing
# anything that could affect external state (uploads, memory writes, network).
# These default to True for v1; in production they should be backed by a
# real auth layer.
_PERMISSIONS = {
    "upload_files": True,
    "write_memory": True,
    "external_search": False,
    "self_modify": False,
}


def is_permitted(capability: str) -> bool:
    return _PERMISSIONS.get(capability, False)


def set_permission(capability: str, allowed: bool) -> None:
    _PERMISSIONS[capability] = allowed


# ---------------------------------------------------------------------------
# Status snapshot — used by the HUD's diagnostics panel.
# ---------------------------------------------------------------------------

def status() -> dict:
    return {
        "shield_online": True,
        "injection_patterns_loaded": len(INJECTION_PATTERNS),
        "control_token_patterns_loaded": len(CONTROL_TOKEN_PATTERNS),
        "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
        "allowed_extensions": list(ALLOWED_UPLOAD_EXTS),
        "permissions": dict(_PERMISSIONS),
    }
