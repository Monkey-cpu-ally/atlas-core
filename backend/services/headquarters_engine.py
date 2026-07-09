"""ATLAS Headquarters Engine.

A polished identity and status layer over ATLAS subsystems. This avoids making
ATLAS feel like a pile of generic backend endpoints. The generic APIs remain for
compatibility; Headquarters presents them as an intentional engineering command
center.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


ATLAS_SEALS = [
    "Architecture",
    "Engineering",
    "Testing",
    "Documentation",
    "Security",
    "Performance",
    "Luxury Review",
]


DIVISIONS = [
    {
        "division_id": "atlas-core-engineering",
        "name": "ATLAS Core Engineering",
        "owner": "Council",
        "purpose": "Architecture, integration, CI, repository health, and final approval.",
        "status": "active",
    },
    {
        "division_id": "knowledge-division",
        "name": "Knowledge Division",
        "owner": "Minerva",
        "purpose": "Discovery approval, knowledge records, Chronicle, evidence, and source reliability.",
        "status": "active",
    },
    {
        "division_id": "robotics-division",
        "name": "Robotics Division",
        "owner": "Hermes",
        "purpose": "Weaver, robot control, sensors, digital twins, CAD, and manufacturing planning.",
        "status": "planned",
    },
    {
        "division_id": "hud-ux-division",
        "name": "HUD and Luxury UX Division",
        "owner": "Hermes",
        "purpose": "Luxury HUD, AI faces, Figma handoff, voice, and Council chamber experience.",
        "status": "planned",
    },
    {
        "division_id": "innovation-lab",
        "name": "Innovation Lab",
        "owner": "Council",
        "purpose": "Quantum Outcome, Probability, Innovation, Evolution, and Experiment engines.",
        "status": "queued",
    },
]


QUALITY_GATES = [
    {"gate": "Built", "meaning": "The subsystem exists as real code, not only a roadmap item.", "required": True},
    {"gate": "Connected", "meaning": "The subsystem is mounted into ATLAS and linked to the correct services.", "required": True},
    {"gate": "Tested", "meaning": "Unit and integration tests cover core behavior and failure behavior.", "required": True},
    {"gate": "Cleaned", "meaning": "Names, modules, imports, error handling, and responsibilities are organized.", "required": True},
    {"gate": "Documented", "meaning": "Purpose, routes, inputs, outputs, and limitations are documented.", "required": True},
    {"gate": "Approved", "meaning": "Headquarters confirms it meets the ATLAS Luxury Engineering Standard.", "required": True},
]


GENERIC_REPLACEMENT_MAP = {
    "/api/discovery-approval": "/api/headquarters/knowledge-gate",
    "/api/external-access": "/api/headquarters/source-clearance",
    "/api/project-intelligence": "/api/headquarters/project-briefing",
    "/api/self-improve": "/api/headquarters/refinement",
}


TECHNICAL_DEBT_ITEMS = [
    {
        "debt_id": "DEBT-HUD-001",
        "subsystem": "HUD",
        "severity": "medium",
        "quality_gate": "Luxury Review",
        "issue": "Some HUD docs used older dashboard/ring wording instead of Headquarters language.",
        "next_safe_action": "Refresh HUD docs and design-bank contract.",
        "status": "completed",
    },
    {
        "debt_id": "DEBT-HQ-001",
        "subsystem": "Headquarters",
        "severity": "medium",
        "quality_gate": "Engineering",
        "issue": "Headquarters command surfaces needed integration tests proving they stay mapped to developer APIs.",
        "next_safe_action": "Keep command-surface mapping tests updated when adding or renaming Headquarters surfaces.",
        "status": "completed",
    },
    {
        "debt_id": "DEBT-PERSIST-001",
        "subsystem": "Startup Persistence",
        "severity": "high",
        "quality_gate": "Engineering",
        "issue": "Discovery Approval, External Access, and Project Intelligence needed persistence wiring coverage.",
        "next_safe_action": "Keep startup hydration tests updated when persistence-backed collections change.",
        "status": "completed",
    },
    {
        "debt_id": "DEBT-KNOW-001",
        "subsystem": "Knowledge Division",
        "severity": "medium",
        "quality_gate": "Architecture",
        "issue": "World Knowledge Graph exists as a core service but still needs final server mounting verification.",
        "next_safe_action": "Confirm route registration and add route tests if missing.",
        "status": "open",
    },
    {
        "debt_id": "DEBT-DOC-001",
        "subsystem": "Documentation",
        "severity": "low",
        "quality_gate": "Documentation",
        "issue": "Some roadmap docs lag behind completed command-surface work.",
        "next_safe_action": "Update refinement plan after every subsystem sprint.",
        "status": "active",
    },
    {
        "debt_id": "DEBT-TWIN-001",
        "subsystem": "Digital Twin",
        "severity": "high",
        "quality_gate": "Engineering",
        "issue": "Digital Twin registry exists, but no real solver layer is confirmed.",
        "next_safe_action": "Begin D2 engineering stack after Headquarters hardening.",
        "status": "queued",
    },
    {
        "debt_id": "DEBT-HW-001",
        "subsystem": "Hardware Bridge",
        "severity": "high",
        "quality_gate": "Security",
        "issue": "ESP32 and hardware bridge work must stay sim-first until safety boundaries and device permissions are clear.",
        "next_safe_action": "Add simulation contract before any device-control work.",
        "status": "queued",
    },
]


def headquarters_status() -> Dict[str, Any]:
    debt = technical_debt_register()
    return {
        "name": "ATLAS Headquarters",
        "motto": "Order. Precision. Craftsmanship. Legacy.",
        "standard": "ATLAS Luxury Engineering Standard",
        "active_operation": "Operation ATLAS Refinement",
        "active_phase": "Phase 14 - Knowledge Validation",
        "phase_state": "under_verification",
        "release_posture": "not_ready_until_verified",
        "seals": [{"name": seal, "status": "pending_verification"} for seal in ATLAS_SEALS],
        "divisions": DIVISIONS,
        "quality_gates": QUALITY_GATES,
        "technical_debt": {
            "active_count": debt["active_count"],
            "highest_open_severity": debt["highest_open_severity"],
            "next_safe_action": debt["next_safe_action"],
        },
        "generated_at": _utc_now(),
    }


def quality_gate_report() -> Dict[str, Any]:
    return {
        "title": "ATLAS Quality Gate Report",
        "rule": "A subsystem is not complete because files exist; it is complete only when it is built, connected, tested, cleaned, documented, and approved.",
        "gates": QUALITY_GATES,
        "approval_status": "pending",
        "generated_at": _utc_now(),
    }


def atlas_standard() -> Dict[str, Any]:
    return {
        "title": "ATLAS Luxury Engineering Standard",
        "principles": [
            "Truth over assumptions.",
            "Evidence over opinions.",
            "Craftsmanship over shortcuts.",
            "Elegance over complexity.",
            "Quality over speed.",
            "Security over convenience.",
            "Legacy over trends.",
        ],
        "completion_rule": "Leave ATLAS better than you found it.",
        "generic_replacement_map": GENERIC_REPLACEMENT_MAP,
        "generated_at": _utc_now(),
    }


def mission_control() -> Dict[str, Any]:
    return {
        "title": "ATLAS Mission Control",
        "active": {
            "operation": "Operation ATLAS Refinement",
            "mission": "Verify and refine Phase 14 before any new major phase begins.",
            "status": "active",
        },
        "queue": [
            "Verify World Knowledge Graph route mounting and route tests.",
            "Continue Knowledge Division roadmap after refinement hardening.",
            "Add Source Reliability Ranking after Phase 14 is stable.",
            "Create ATLAS System Inspector after Knowledge Validation passes Headquarters review.",
        ],
        "blocked_until": "Phase 14 verification passes.",
        "generated_at": _utc_now(),
    }


def knowledge_gate() -> Dict[str, Any]:
    return _command_surface(
        title="ATLAS Knowledge Gate",
        replaces="/api/discovery-approval",
        purpose="Controls whether discoveries are promoted into trusted ATLAS knowledge.",
        owner="Minerva + Council",
        responsibilities=[
            "Create discovery drafts.",
            "Collect Ajani, Hermes, and Minerva reviews.",
            "Score evidence.",
            "Record Council decisions.",
            "Promote approved discoveries into Knowledge Records and Chronicle entries.",
        ],
        current_state="under_verification",
    )


def source_clearance() -> Dict[str, Any]:
    return _command_surface(
        title="ATLAS Source Clearance",
        replaces="/api/external-access",
        purpose="Controls what outside systems ATLAS is allowed to read or import.",
        owner="Council",
        responsibilities=[
            "Define source permissions.",
            "Block unrestricted private access.",
            "Create import plans.",
            "Route approved content through Council review.",
        ],
        current_state="under_verification",
    )


def project_briefing() -> Dict[str, Any]:
    return _command_surface(
        title="ATLAS Project Briefing",
        replaces="/api/project-intelligence",
        purpose="Presents living project workspaces as executive engineering briefs.",
        owner="Council",
        responsibilities=[
            "Track missions, risks, recommendations, materials, tests, and decisions.",
            "Detect cross-project reuse opportunities.",
            "Keep project intelligence connected to ATLAS knowledge.",
        ],
        current_state="active_foundation_needs_more_tests",
    )


def refinement() -> Dict[str, Any]:
    surface = _command_surface(
        title="ATLAS Refinement Office",
        replaces="/api/self-improve",
        purpose="Turns rough edges, failed tests, and code-quality issues into safe improvement proposals.",
        owner="Council",
        responsibilities=[
            "Scan repository health.",
            "Create improvement proposals.",
            "Require approval for risky changes.",
            "Keep technical debt visible instead of hidden.",
        ],
        current_state="active",
    )
    surface["technical_debt"] = technical_debt_register()
    return surface


def technical_debt_register(status: str | None = None, severity: str | None = None) -> Dict[str, Any]:
    items = TECHNICAL_DEBT_ITEMS
    if status:
        items = [item for item in items if item["status"] == status]
    if severity:
        items = [item for item in items if item["severity"] == severity]

    active_items = [item for item in TECHNICAL_DEBT_ITEMS if item["status"] in {"open", "active"}]
    severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    highest = "none"
    if active_items:
        highest = max(active_items, key=lambda item: severity_rank.get(item["severity"], 0))["severity"]
    next_action = active_items[0]["next_safe_action"] if active_items else "No active debt items. Continue normal quality-gate review."

    by_status: Dict[str, int] = {}
    by_gate: Dict[str, int] = {}
    for item in TECHNICAL_DEBT_ITEMS:
        by_status[item["status"]] = by_status.get(item["status"], 0) + 1
        by_gate[item["quality_gate"]] = by_gate.get(item["quality_gate"], 0) + 1

    return {
        "title": "ATLAS Technical Debt Register",
        "rule": "Technical debt is allowed only when it is visible, prioritized, and tied to a next safe action.",
        "active_count": len(active_items),
        "highest_open_severity": highest,
        "next_safe_action": next_action,
        "by_status": by_status,
        "by_quality_gate": by_gate,
        "items": items,
        "generated_at": _utc_now(),
    }


def _command_surface(
    *,
    title: str,
    replaces: str,
    purpose: str,
    owner: str,
    responsibilities: List[str],
    current_state: str,
) -> Dict[str, Any]:
    return {
        "title": title,
        "identity": "ATLAS Headquarters Command Surface",
        "developer_api_underneath": replaces,
        "purpose": purpose,
        "owner": owner,
        "responsibilities": responsibilities,
        "current_state": current_state,
        "quality_gate": "pending_headquarters_approval",
        "generated_at": _utc_now(),
    }
