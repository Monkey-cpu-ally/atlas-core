"""
Engineering Validation Protocol — Every project must pass 5 checks before blueprint acceptance.

Checks:
1. Scale Check — Size compatibility, component scale matching
2. Energy Check — Power requirements and source identification
3. Material Check — Current manufacturability of materials
4. Fabrication Check — Buildability with real tools (3D print, CNC, PCB fab, cleanroom)
5. Physics Check — Thermodynamics compliance, fluid dynamics, structural mechanics

Feasibility Tiers:
- Tier 1: Buildable Now — Consumer tools, parts exist, physics validated, budget definable
- Tier 2: Research Grade — Lab equipment required, exists in academic research, high cost but not sci-fi
- Tier 3: Frontier Engineering — Physics allows it, materials not scalable, cost unknown, needs breakthroughs
- Tier 4: Speculative/Theoretical — Missing physics validation, violates constraints, no fabrication path
         NEVER generates fabrication packages. Stays in theory sandbox.

Pipeline: Idea → Constraints → Physics validation → Simulation → Feasibility tier → THEN blueprint
"""

import os
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger("atlas.engineering_validation")

FEASIBILITY_TIERS = {
    1: {
        "name": "Buildable Now",
        "description": "Can be built with consumer tools. Parts exist. Physics validated. Budget definable.",
        "allows_blueprint": True,
        "allows_fabrication": True,
        "examples": "Macro-scale swarm robot. RF monitoring system. Green robot joint prototype.",
    },
    2: {
        "name": "Research Grade",
        "description": "Requires lab equipment. Exists in academic research. High cost but not sci-fi.",
        "allows_blueprint": True,
        "allows_fabrication": True,
        "examples": "Magnetically steered microbots. MEMS fabrication. Advanced battery chemistry experiments.",
    },
    3: {
        "name": "Frontier Engineering",
        "description": "Physics allows it. Materials not scalable yet. Cost unknown. Needs breakthroughs.",
        "allows_blueprint": True,
        "allows_fabrication": False,
        "examples": "Fully autonomous nano-medical swarm. High-efficiency ambient RF power harvesting at watt scale.",
    },
    4: {
        "name": "Speculative / Theoretical",
        "description": "Missing physics validation. Violates scale-energy constraints. No known fabrication path.",
        "allows_blueprint": False,
        "allows_fabrication": False,
        "examples": "Room-temperature superconductors at ambient pressure. Faster-than-light communication.",
    },
}

VALIDATION_CHECKS = ["scale", "energy", "material", "fabrication", "physics"]


def get_openai_client():
    from openai import OpenAI
    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    if not api_key or not base_url:
        return None
    return OpenAI(api_key=api_key, base_url=base_url)


def build_validation_prompt(project) -> str:
    return f"""You are a senior engineering review board evaluating a project for feasibility and buildability.
Your job is to be HONEST and RIGOROUS. Do not hand-wave. Do not assume things work without evidence.

PROJECT: {project.project_name} (codename: {project.codename})
PROJECT ID: {project.project_id}
CURRENT PHASE: {project.current_phase}
DESIGN INTENT: {project.design_intent or 'Not defined'}
CURRENT FOCUS: {project.current_focus or 'Not defined'}
KNOWN UNKNOWNS: {project.known_unknowns or 'Not identified'}
SAFETY CONSTRAINTS: {project.safety_constraints or 'Standard'}
ASSUMPTIONS: {project.assumptions or 'Not stated'}

=== ENGINEERING VALIDATION PROTOCOL ===
You MUST answer ALL 5 checks honestly:

1. SCALE CHECK
   - What physical size is this project?
   - Are listed components compatible with that scale?
   - Are there scale mismatches between subsystems?

2. ENERGY CHECK
   - How much power does it require (watts, voltage, current)?
   - Where does that power come from?
   - Is the power budget realistic for the scale?

3. MATERIAL CHECK
   - Are the proposed materials currently manufacturable?
   - Are they available at the required purity/grade?
   - Are there material compatibility issues?

4. FABRICATION CHECK
   - Can this be built with: 3D printing? CNC? PCB fab? Cleanroom? Hand tools?
   - What fabrication methods are needed?
   - Are tolerances achievable with available methods?

5. PHYSICS CHECK
   - Does this violate thermodynamics (1st, 2nd, or 3rd law)?
   - Does fluid dynamics support proposed motion/flow?
   - Are structural mechanics sound?
   - Are electromagnetic assumptions valid?

=== FEASIBILITY TIER CLASSIFICATION ===
Based on your checks, assign ONE tier:

TIER 1 — BUILDABLE NOW: Consumer tools, parts exist, physics validated, budget definable.
TIER 2 — RESEARCH GRADE: Lab equipment required, exists in academic research, high cost but realistic.
TIER 3 — FRONTIER ENGINEERING: Physics allows it, materials not scalable yet, cost unknown, needs breakthroughs.
TIER 4 — SPECULATIVE/THEORETICAL: Missing physics validation, violates scale-energy constraints, no fabrication path.

Respond with valid JSON ONLY:
{{
    "scale_check": {{
        "pass": true/false,
        "size_class": "nano|micro|meso|macro|large",
        "findings": "What you found about scale compatibility (2-3 sentences)",
        "issues": ["List any scale issues found"]
    }},
    "energy_check": {{
        "pass": true/false,
        "power_estimate": "Estimated power requirement (e.g., '5W', '100mW', 'unknown')",
        "power_source": "Identified power source or 'unspecified'",
        "findings": "What you found about energy feasibility (2-3 sentences)",
        "issues": ["List any energy issues found"]
    }},
    "material_check": {{
        "pass": true/false,
        "materials_available": true/false,
        "findings": "What you found about material availability (2-3 sentences)",
        "issues": ["List any material issues found"]
    }},
    "fabrication_check": {{
        "pass": true/false,
        "methods_available": ["3d_print", "cnc", "pcb_fab", "cleanroom", "hand_tools", "laser_cut"],
        "findings": "What you found about fabrication feasibility (2-3 sentences)",
        "issues": ["List any fabrication issues found"]
    }},
    "physics_check": {{
        "pass": true/false,
        "thermodynamics_ok": true/false,
        "fluid_dynamics_ok": true/false,
        "structural_ok": true/false,
        "findings": "What you found about physics compliance (2-3 sentences)",
        "issues": ["List any physics violations or concerns"]
    }},
    "feasibility_tier": 1/2/3/4,
    "tier_justification": "Why this project belongs in this tier (2-3 sentences). Be specific about what prevents higher tier.",
    "critical_blockers": ["List the most critical issues preventing this from being buildable, if any"],
    "recommendations": ["Specific actions to improve feasibility or advance to a higher tier"]
}}"""


def run_validation(project) -> dict:
    client = get_openai_client()
    if not client:
        logger.warning("No OpenAI client available for validation")
        return None

    prompt = build_validation_prompt(project)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a rigorous engineering review board. You evaluate projects for "
                        "real-world feasibility using physics, materials science, and manufacturing "
                        "constraints. Be honest — if something can't be built, say so. If it can, "
                        "explain how. No hand-waving. No optimistic assumptions. Respond ONLY with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        content = re.sub(r'[\x00-\x1f\x7f]', lambda m: ' ' if m.group() not in '\n\r\t' else m.group(), content)

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise

        tier = result.get("feasibility_tier", 4)
        if not isinstance(tier, int) or tier < 1 or tier > 4:
            tier = 4

        checks_passed = sum(1 for check in VALIDATION_CHECKS if result.get(f"{check}_check", {}).get("pass", False))
        all_passed = checks_passed == len(VALIDATION_CHECKS)

        result["feasibility_tier"] = tier
        result["checks_passed"] = checks_passed
        result["total_checks"] = len(VALIDATION_CHECKS)
        result["all_checks_passed"] = all_passed
        result["validated_at"] = datetime.utcnow().isoformat()

        return result

    except Exception as e:
        logger.error(f"Engineering validation failed for {project.project_id}: {e}")
        return None


def validate_and_store(db, project_id: str, persona: str) -> dict:
    from atlas_core_new.db.models import ResearchTracker, ResearchActivityLog

    project = db.query(ResearchTracker).filter(
        ResearchTracker.project_id == project_id,
        ResearchTracker.persona == persona,
    ).first()

    if not project:
        return {"status": "error", "message": "Project not found"}

    result = run_validation(project)
    if not result:
        return {"status": "error", "message": "Validation service unavailable"}

    tier = result["feasibility_tier"]
    project.feasibility_tier = tier
    project.engineering_validation = result
    project.validation_status = "passed" if result["all_checks_passed"] else "issues_found"
    project.last_validated_at = datetime.utcnow()

    if tier == 4:
        if project.current_phase in ("blueprint", "simulation", "digital_proto", "physical_proto", "refinement"):
            pass
        project.knowledge_tier = "conceptual_sandbox"

    tier_info = FEASIBILITY_TIERS.get(tier, FEASIBILITY_TIERS[4])

    db.add(ResearchActivityLog(
        persona=persona,
        project_id=project_id,
        activity_type="engineering_validation",
        title=f"Engineering Validation: Tier {tier} — {tier_info['name']}",
        description=(
            f"Checks passed: {result['checks_passed']}/{result['total_checks']}. "
            f"Tier: {tier} ({tier_info['name']}). "
            f"Justification: {result.get('tier_justification', 'N/A')}"
        ),
    ))

    db.commit()

    return {
        "status": "ok",
        "project_id": project_id,
        "persona": persona,
        "feasibility_tier": tier,
        "tier_name": tier_info["name"],
        "tier_description": tier_info["description"],
        "allows_blueprint": tier_info["allows_blueprint"],
        "allows_fabrication": tier_info["allows_fabrication"],
        "checks_passed": result["checks_passed"],
        "total_checks": result["total_checks"],
        "all_checks_passed": result["all_checks_passed"],
        "validation": result,
    }


def can_advance_to_blueprint(project) -> tuple:
    if not project.feasibility_tier:
        return False, "Project has not been validated. Run engineering validation first."

    if project.validation_status == "not_validated":
        return False, "Engineering validation has not been run yet."

    tier = project.feasibility_tier
    tier_info = FEASIBILITY_TIERS.get(tier, FEASIBILITY_TIERS[4])

    if not tier_info["allows_blueprint"]:
        return False, f"Tier {tier} ({tier_info['name']}) projects cannot advance to blueprint. {tier_info['description']}"

    return True, f"Tier {tier} ({tier_info['name']}) — cleared for blueprint."


def can_generate_fabrication(project) -> tuple:
    if not project.feasibility_tier:
        return False, "Project has not been validated."

    tier = project.feasibility_tier
    tier_info = FEASIBILITY_TIERS.get(tier, FEASIBILITY_TIERS[4])

    if not tier_info["allows_fabrication"]:
        return False, f"Tier {tier} ({tier_info['name']}) projects do not generate fabrication packages. {tier_info['description']}"

    return True, f"Tier {tier} ({tier_info['name']}) — fabrication allowed."
