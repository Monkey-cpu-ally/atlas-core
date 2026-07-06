"""ATLAS System Inspector.

V1 engineering auditor for ATLAS. It performs deterministic repository checks
without mutating code: structure, tests, docs, technical debt markers, security
signals, and Headquarters certification posture.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def inspect_repository() -> Dict[str, Any]:
    services = sorted((BACKEND_DIR / "services").glob("*.py")) if (BACKEND_DIR / "services").exists() else []
    routes = sorted((BACKEND_DIR / "routes").glob("*.py")) if (BACKEND_DIR / "routes").exists() else []
    tests = sorted((BACKEND_DIR / "tests").glob("test_*.py")) if (BACKEND_DIR / "tests").exists() else []
    docs = sorted((ROOT_DIR / "memory").glob("*.md")) if (ROOT_DIR / "memory").exists() else []

    test_names = {p.name for p in tests}
    missing_service_tests: List[str] = []
    large_modules: List[Dict[str, Any]] = []
    debt_markers: List[Dict[str, Any]] = []
    security_flags: List[Dict[str, Any]] = []

    for service in services:
        if service.name.startswith("__"):
            continue
        expected_test = f"test_{service.stem}.py"
        if expected_test not in test_names:
            missing_service_tests.append(str(service.relative_to(ROOT_DIR)))

        text = _safe_read(service)
        lines = text.splitlines()
        if len(lines) > 450:
            large_modules.append({"path": str(service.relative_to(ROOT_DIR)), "lines": len(lines)})
        for idx, line in enumerate(lines, start=1):
            upper = line.upper()
            if "TODO" in upper or "FIXME" in upper or "HACK" in upper:
                debt_markers.append({"path": str(service.relative_to(ROOT_DIR)), "line": idx, "text": line.strip()[:180]})
            if "API_KEY" in upper and "TEST-KEY" not in upper and "ENVIRON" not in upper:
                security_flags.append({"path": str(service.relative_to(ROOT_DIR)), "line": idx, "signal": "possible_api_key_reference"})

    score = _score_health(
        missing_tests=len(missing_service_tests),
        large_modules=len(large_modules),
        debt_markers=len(debt_markers),
        security_flags=len(security_flags),
    )

    return {
        "title": "ATLAS System Inspector Report",
        "generated_at": _utc_now(),
        "repository_root": str(ROOT_DIR),
        "counts": {
            "services": len(services),
            "routes": len(routes),
            "tests": len(tests),
            "memory_docs": len(docs),
        },
        "health_score": score,
        "certification_posture": _certification_posture(score),
        "findings": {
            "missing_service_tests": missing_service_tests[:100],
            "large_modules": large_modules[:40],
            "technical_debt_markers": debt_markers[:80],
            "security_flags": security_flags[:40],
        },
        "recommendations": _recommendations(missing_service_tests, large_modules, debt_markers, security_flags),
        "headquarters_rule": "No subsystem is complete until built, connected, tested, cleaned, documented, and approved.",
    }


def technical_debt_register() -> Dict[str, Any]:
    report = inspect_repository()
    debt_items: List[Dict[str, Any]] = []

    for path in report["findings"]["missing_service_tests"]:
        debt_items.append({
            "type": "missing_test",
            "severity": "medium",
            "path": path,
            "recommendation": "Add a focused unit test for this service before declaring it Headquarters-approved.",
        })
    for item in report["findings"]["large_modules"]:
        debt_items.append({
            "type": "large_module",
            "severity": "medium",
            "path": item["path"],
            "recommendation": "Review for split opportunities only after tests exist.",
        })
    for item in report["findings"]["technical_debt_markers"]:
        debt_items.append({
            "type": "debt_marker",
            "severity": "low",
            "path": item["path"],
            "line": item["line"],
            "recommendation": "Resolve or convert into a tracked improvement proposal.",
        })

    return {
        "title": "ATLAS Technical Debt Register",
        "generated_at": _utc_now(),
        "count": len(debt_items),
        "items": debt_items[:200],
    }


def certification_report() -> Dict[str, Any]:
    inspection = inspect_repository()
    score = inspection["health_score"]
    seals = []
    gates = {
        "Architecture": score >= 70,
        "Engineering": score >= 70,
        "Testing": len(inspection["findings"]["missing_service_tests"]) == 0,
        "Documentation": inspection["counts"]["memory_docs"] >= 5,
        "Security": len(inspection["findings"]["security_flags"]) == 0,
        "Performance": len(inspection["findings"]["large_modules"]) <= 10,
        "Luxury Review": score >= 85,
    }
    for name, passed in gates.items():
        seals.append({"seal": name, "status": "pass" if passed else "needs_refinement"})

    return {
        "title": "ATLAS Headquarters Certification Report",
        "generated_at": _utc_now(),
        "overall_status": "approved" if all(gates.values()) else "needs_refinement",
        "health_score": score,
        "seals": seals,
        "next_action": "Fix failing seals before moving to the next major phase.",
    }


def _score_health(*, missing_tests: int, large_modules: int, debt_markers: int, security_flags: int) -> int:
    score = 100
    score -= min(45, missing_tests * 2)
    score -= min(15, large_modules * 2)
    score -= min(15, debt_markers)
    score -= min(30, security_flags * 10)
    return max(0, min(100, score))


def _certification_posture(score: int) -> str:
    if score >= 90:
        return "gold_candidate"
    if score >= 75:
        return "silver_candidate"
    if score >= 55:
        return "bronze_candidate_needs_refinement"
    return "not_ready"


def _recommendations(missing_tests: List[str], large_modules: List[Dict[str, Any]], debt_markers: List[Dict[str, Any]], security_flags: List[Dict[str, Any]]) -> List[str]:
    recommendations: List[str] = []
    if missing_tests:
        recommendations.append("Add focused tests for services missing dedicated test coverage.")
    if large_modules:
        recommendations.append("Review large modules for clean split opportunities after tests exist.")
    if debt_markers:
        recommendations.append("Convert TODO/FIXME/HACK markers into tracked improvement proposals or resolve them.")
    if security_flags:
        recommendations.append("Review possible sensitive key references and ensure all secrets come from environment variables.")
    if not recommendations:
        recommendations.append("Maintain current discipline; no major inspector findings detected.")
    return recommendations
