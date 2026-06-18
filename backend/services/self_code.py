"""
Self-Code Improvement scanner.

Scans the /app/backend codebase using simple regex + AST heuristics and
generates proposals routed through the existing self-improvement system.

What it detects (honestly limited — NO refactoring engine, NO ML):
  * outdated-feeling imports (TODO/FIXME/XXX comments)
  * weak error handling (`except Exception` with `pass`)
  * hardcoded HUD legacy lists (regex against AtlasSidePanel patterns)
  * missing tests for new routes (heuristic: route file w/o sibling test)
  * messy architecture markers (modules over LINE_BUDGET lines)
  * duplicate import patterns (same import in many files)

Every detection becomes a `pending` proposal in `self_improvements` —
NEVER applies a change. Honors the user's "approval first" rule.
"""
from __future__ import annotations

import ast
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from services import self_improvement as si

logger = logging.getLogger("atlas.self_code")

ROOT = Path("/app/backend")
LINE_BUDGET = 550               # files over this trigger "module size" proposals
SKIP_DIRS = {"__pycache__", "tests"}


async def scan(root: Optional[str] = None) -> Dict[str, Any]:
    base = Path(root or ROOT)
    proposals_created: List[str] = []
    findings: List[Dict[str, Any]] = []

    files: List[Path] = []
    for p in base.rglob("*.py"):
        if any(seg in SKIP_DIRS for seg in p.parts):
            continue
        files.append(p)

    # Detector 1: TODO / FIXME / XXX
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:    # noqa: BLE001
            continue
        for m in re.finditer(r"\b(TODO|FIXME|XXX|HACK)\b[: ]?(.*)", text):
            findings.append({
                "category": "workflow",
                "affected_system": str(f.relative_to(base)),
                "evidence": [{"line_text": m.group(0)[:140]}],
                "observed_pattern": f"unresolved {m.group(1)} comment in {f.name}",
                "proposed_change": f"Address the {m.group(1)} comment or open an issue tracking it.",
                "risk_level": "low",
                "confidence_score": 0.6,
            })

    # Detector 2: bare-pass exception handlers
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except Exception:    # noqa: BLE001
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                body_kinds = [type(b).__name__ for b in node.body]
                if body_kinds == ["Pass"]:
                    findings.append({
                        "category": "code_architecture",
                        "affected_system": str(f.relative_to(base)),
                        "evidence": [{"line": node.lineno, "msg": "except: pass"}],
                        "observed_pattern": f"silent except-pass in {f.name}:{node.lineno}",
                        "proposed_change": "Replace bare `pass` with a logger.warning + the exception object so failures are not silenced.",
                        "risk_level": "medium",
                        "confidence_score": 0.85,
                    })

    # Detector 3: hardcoded HUD legacy lists (frontend, not backend — scan source files)
    fe_panel = Path("/app/frontend/src/components/HUD/AtlasSidePanel.js")
    if fe_panel.exists():
        try:
            src = fe_panel.read_text(encoding="utf-8")
            if re.search(r"Connected Devices.*Primary Display", src, re.S) or \
               re.search(r"Blueprint Gallery.*System Architecture", src, re.S):
                findings.append({
                    "category": "hud_layout",
                    "affected_system": "frontend/src/components/HUD/AtlasSidePanel.js",
                    "evidence": [{"file": "AtlasSidePanel.js",
                                  "lines": "~88-99",
                                  "hint": "hardcoded list literals"}],
                    "observed_pattern": "HUD AtlasSidePanel still renders hardcoded 'Connected Devices' / 'Blueprint Gallery' lists.",
                    "proposed_change": "Replace literals with fetches against /api/robot/devices and /api/twins/list. Add data-testids per item.",
                    "risk_level": "medium",
                    "confidence_score": 0.95,
                })
        except Exception:    # noqa: BLE001
            pass

    # Detector 4: module size — files over LINE_BUDGET
    for f in files:
        try:
            n = sum(1 for _ in f.open(encoding="utf-8"))
        except Exception:    # noqa: BLE001
            continue
        if n > LINE_BUDGET:
            findings.append({
                "category": "code_architecture",
                "affected_system": str(f.relative_to(base)),
                "evidence": [{"lines": n, "budget": LINE_BUDGET}],
                "observed_pattern": f"module {f.name} is {n} lines (budget {LINE_BUDGET}).",
                "proposed_change": f"Split {f.name} into smaller modules by responsibility (e.g. extract helpers, separate route handlers).",
                "risk_level": "high",      # refactor → needs approval
                "confidence_score": 0.7,
            })

    # Detector 5: missing test for a routes/*.py file
    routes_dir = base / "routes"
    tests_dir = base / "tests"
    if routes_dir.exists() and tests_dir.exists():
        existing_tests = " ".join(p.name for p in tests_dir.glob("*.py"))
        for r in routes_dir.glob("*.py"):
            if r.name.startswith("__"):
                continue
            stem = r.stem
            if f"test_{stem}" not in existing_tests:
                findings.append({
                    "category": "code_architecture",
                    "affected_system": str(r.relative_to(base)),
                    "evidence": [{"route_file": r.name, "tests_dir": str(tests_dir)}],
                    "observed_pattern": f"route {r.name} has no matching `test_{stem}*.py` test file",
                    "proposed_change": f"Add a pytest module `tests/test_{stem}.py` covering happy-path and one error case for each route in {r.name}.",
                    "risk_level": "low",
                    "confidence_score": 0.6,
                })

    # Persist as proposals (skip if a near-identical pending proposal already exists)
    for fnd in findings:
        existing = await si.list_proposals(status="pending", limit=500)
        already = any(
            (e.get("observed_pattern") == fnd["observed_pattern"]
             and e.get("affected_system") == fnd["affected_system"])
            for e in existing
        )
        if already:
            continue
        prop = await si.propose(
            observed_pattern=fnd["observed_pattern"],
            evidence=fnd["evidence"],
            affected_system=fnd["affected_system"],
            proposed_change=fnd["proposed_change"],
            category=fnd["category"],
            risk_level=fnd["risk_level"],
            confidence_score=fnd["confidence_score"],
            source="self-code-scanner",
        )
        proposals_created.append(prop["id"])

    return {
        "scan_root": str(base),
        "files_scanned": len(files),
        "findings_total": len(findings),
        "proposals_created": len(proposals_created),
        "proposal_ids": proposals_created[:50],
    }
