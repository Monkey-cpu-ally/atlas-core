import os
import json
import logging
import re
import time
from typing import Optional

logger = logging.getLogger("atlas.build_plan_generator")

PERSONA_BUILD_CONTEXT = {
    "ajani": {
        "role": "Builder — breaks every project into physical, buildable steps",
        "style": "Think like a warrior-engineer. Every step must have a purpose. No wasted motion.",
    },
    "minerva": {
        "role": "Confidence Guide — ensures every step is understandable and ethically sound",
        "style": "Think like a wise teacher. Every step must teach something. No confusion allowed.",
    },
    "hermes": {
        "role": "Rules Keeper — ensures precision, safety, and correct sequencing",
        "style": "Think like a precision engineer. Every measurement matters. No shortcuts.",
    },
}


def get_db_session():
    from atlas_core_new.db.session import SessionLocal
    if SessionLocal is None:
        return None
    return SessionLocal()


def get_openai_client():
    from openai import OpenAI
    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    if not api_key or not base_url:
        return None
    return OpenAI(api_key=api_key, base_url=base_url)


def build_plan_prompt(project, persona: str) -> str:
    ctx = PERSONA_BUILD_CONTEXT.get(persona, {})

    return f"""You are {persona.capitalize()}, creating a LEGO-Style Build Plan for your project.

YOUR ROLE: {ctx.get('role', 'Builder')}
YOUR STYLE: {ctx.get('style', 'Be precise and thorough')}

PROJECT: {project.project_name} (codename: {project.codename})
PROJECT ID: {project.project_id}
CURRENT PHASE: {project.current_phase}
CURRENT FOCUS: {project.current_focus or 'General development'}
DESIGN INTENT: {project.design_intent or 'Not yet defined'}

LEGO-STYLE BUILD SYSTEM RULES:
1. Build-before-explain: Show what to do FIRST, explain why AFTER
2. One-page-one-action: Each step does exactly ONE thing
3. Visual-first: Describe what it looks like at each step
4. Every step must be completable by someone with basic tools
5. Include safety notes where relevant
6. List exact parts needed before building starts
7. Steps must be in correct dependency order

FABRICATION-READY REQUIREMENTS:
- Every part MUST have an estimated cost in USD
- Every part MUST specify its fabrication method (3d_print, cnc_mill, laser_cut, hand_fabricate, off_the_shelf, pcb_fabrication, cast_mold)
- Custom parts MUST specify the digital file format needed (STL, STEP, DXF, Gerber, G-code)
- Include real dimensions and tolerances where applicable
- Include material specifications (e.g., "PLA filament 1.75mm", "6061 aluminum sheet 2mm")
- Provide supplier references (Amazon, McMaster-Carr, Digi-Key, Adafruit, etc.)
- Include a tools_required list for the entire build
- Include a difficulty_level (beginner, intermediate, advanced, expert)

Generate a complete LEGO-style fabrication-ready build plan. Respond with valid JSON only:

{{
    "plan_name": "Descriptive name for this build plan",
    "description": "What this build plan produces when complete (1-2 sentences)",
    "build_type": "component|subsystem|prototype|framework",
    "difficulty_level": "beginner|intermediate|advanced|expert",
    "tools_required": ["3D Printer (FDM)", "Soldering Iron", "Multimeter", "etc"],
    "fabrication_notes": "Overall notes about fabrication approach, print settings, or special considerations",
    "parts": [
        {{
            "part_name": "Name of part or material",
            "part_type": "material|component|tool|sensor|electronic|structural",
            "specification": "Exact specs (dimensions, ratings, tolerances)",
            "quantity": 1,
            "unit": "pcs|kg|m|L",
            "sourcing_notes": "Where to get this or how to make it",
            "is_custom": false,
            "estimated_cost": 12.99,
            "fabrication_method": "3d_print|cnc_mill|laser_cut|hand_fabricate|off_the_shelf|pcb_fabrication|cast_mold",
            "material_spec": "Specific material (e.g., PLA 1.75mm, 6061 Aluminum, FR-4 PCB)",
            "dimensions": "L x W x H in mm (e.g., 120x80x40mm)",
            "weight_grams": 45.0,
            "tolerance": "±0.2mm or as applicable",
            "file_format": "STL|STEP|DXF|Gerber|G-code|null (for off-the-shelf)",
            "supplier_url": "Example: amazon.com, mcmaster.com, digikey.com, adafruit.com"
        }}
    ],
    "steps": [
        {{
            "title": "Step title (action verb first)",
            "description": "Detailed instruction for this single step",
            "tools_needed": "Tools required for this step",
            "safety_notes": "Safety considerations (or null)",
            "expected_outcome": "What it should look like when done correctly"
        }}
    ]
}}

Generate 6-10 parts and 8-12 steps. Be specific and technical but accessible. Use realistic prices. No generic filler."""


def parse_llm_response(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

    content = re.sub(r'[\x00-\x1f\x7f]', lambda m: ' ' if m.group() not in '\n\r\t' else m.group(), content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        content = content.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise


def generate_build_plan(client, persona: str, project) -> dict:
    from atlas_core_new.research.engineering_validation import can_generate_fabrication
    can_fab, fab_reason = can_generate_fabrication(project)
    if not can_fab and getattr(project, 'feasibility_tier', None) == 4:
        return {
            "plan_name": f"Theoretical Design Study: {project.project_name}",
            "description": f"TIER 4 — SPECULATIVE/THEORETICAL. {fab_reason} This plan is for conceptual exploration only. No fabrication package will be generated.",
            "build_type": "framework",
            "difficulty_level": "expert",
            "parts": [],
            "steps": [],
            "tools_required": [],
            "fabrication_notes": f"BLOCKED: {fab_reason}",
            "_tier_blocked": True,
        }

    ctx = PERSONA_BUILD_CONTEXT.get(persona, {})

    system_msg = f"You are {persona.capitalize()}, an AI research persona generating LEGO-style build plans. Role: {ctx.get('role', 'Builder')}. Respond ONLY with valid JSON. No markdown, no code fences, no extra text."

    prompt = build_plan_prompt(project, persona)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2500,
    )

    return parse_llm_response(response.choices[0].message.content)


def save_build_plan(db, project_id: str, persona: str, plan_data: dict) -> dict:
    from atlas_core_new.db.models import BuildPlan, BuildPart, BuildStep, ResearchActivityLog
    from atlas_core_new.research.build_api import check_guardrails

    all_text = f"{plan_data.get('plan_name', '')} {plan_data.get('description', '')}"
    safety_flags = check_guardrails(all_text)

    total_cost = 0.0
    for part in plan_data.get("parts", []):
        cost = part.get("estimated_cost")
        if cost and isinstance(cost, (int, float)):
            total_cost += cost * part.get("quantity", 1)

    plan = BuildPlan(
        project_id=project_id,
        persona=persona,
        plan_name=plan_data.get("plan_name", f"Build Plan for {project_id}"),
        description=plan_data.get("description", ""),
        build_type=plan_data.get("build_type", "component"),
        status="designing",
        safety_flags=safety_flags if safety_flags else None,
        total_steps=len(plan_data.get("steps", [])),
        completed_steps=0,
        estimated_total_cost=round(total_cost, 2) if total_cost > 0 else None,
        difficulty_level=plan_data.get("difficulty_level"),
        tools_required_summary=plan_data.get("tools_required"),
        fabrication_notes=plan_data.get("fabrication_notes"),
    )
    db.add(plan)
    db.flush()

    for part in plan_data.get("parts", []):
        part_flags = check_guardrails(f"{part.get('part_name', '')} {part.get('specification', '')}")
        safety_flags.extend(part_flags)

        db.add(BuildPart(
            build_plan_id=plan.id,
            part_name=part.get("part_name", "Unknown Part"),
            part_type=part.get("part_type", "material"),
            specification=part.get("specification"),
            quantity=part.get("quantity", 1),
            unit=part.get("unit", "pcs"),
            sourcing_notes=part.get("sourcing_notes"),
            is_custom=part.get("is_custom", False),
            status="needed",
            estimated_cost=part.get("estimated_cost"),
            fabrication_method=part.get("fabrication_method"),
            material_spec=part.get("material_spec"),
            dimensions=part.get("dimensions"),
            weight_grams=part.get("weight_grams"),
            tolerance=part.get("tolerance"),
            file_format=part.get("file_format"),
            supplier_url=part.get("supplier_url"),
        ))

    for i, step in enumerate(plan_data.get("steps", [])):
        db.add(BuildStep(
            build_plan_id=plan.id,
            step_number=i + 1,
            title=step.get("title", f"Step {i+1}"),
            description=step.get("description"),
            tools_needed=step.get("tools_needed"),
            safety_notes=step.get("safety_notes"),
            expected_outcome=step.get("expected_outcome"),
            status="pending",
        ))

    db.add(ResearchActivityLog(
        persona=persona,
        project_id=project_id,
        activity_type="build_plan_created",
        title=f"LEGO Build Plan: {plan_data.get('plan_name', 'New Plan')}",
        description=f"Build plan with {len(plan_data.get('parts',[]))} parts and {len(plan_data.get('steps',[]))} steps created.",
    ))

    if safety_flags:
        plan.safety_flags = list(set(safety_flags))

    db.commit()

    return {
        "plan_id": plan.id,
        "plan_name": plan.plan_name,
        "parts_count": len(plan_data.get("parts", [])),
        "steps_count": len(plan_data.get("steps", [])),
        "safety_flags": safety_flags,
    }


def generate_build_plans_for_advanced_projects(persona: Optional[str] = None, min_phase: str = "blueprint", max_plans: int = 5):
    db = get_db_session()
    if not db:
        return {"status": "error", "message": "Database not available"}

    client = get_openai_client()
    if not client:
        return {"status": "error", "message": "OpenAI client not configured"}

    try:
        from atlas_core_new.db.models import ResearchTracker, BuildPlan

        phase_rank = {
            "philosophy": 0, "concept": 1, "research": 2, "blueprint": 3,
            "simulation": 4, "digital_proto": 5, "physical_proto": 6, "refinement": 7,
        }
        min_rank = phase_rank.get(min_phase, 3)

        query = db.query(ResearchTracker).filter(
            ResearchTracker.is_active == True,
            ResearchTracker.supervisor_status != "rejected",
        )
        if persona:
            query = query.filter(ResearchTracker.persona == persona)

        projects = query.all()
        advanced = [p for p in projects if phase_rank.get(p.current_phase, 0) >= min_rank]
        advanced.sort(key=lambda p: phase_rank.get(p.current_phase, 0), reverse=True)

        existing_plans = set()
        all_plans = db.query(BuildPlan.project_id, BuildPlan.persona).all()
        for pid, per in all_plans:
            existing_plans.add((pid, per))

        to_build = [p for p in advanced if (p.project_id, p.persona) not in existing_plans][:max_plans]

        results = []
        errors = []

        for project in to_build:
            try:
                plan_data = generate_build_plan(client, project.persona, project)
                result = save_build_plan(db, project.project_id, project.persona, plan_data)
                result["status"] = "created"
                result["persona"] = project.persona
                result["project_id"] = project.project_id
                results.append(result)
                logger.info(f"Build plan created: {project.persona}/{project.project_id} — {result['plan_name']}")
                time.sleep(1)
            except json.JSONDecodeError as e:
                errors.append({"project_id": project.project_id, "persona": project.persona, "error": f"JSON parse: {str(e)}"})
            except Exception as e:
                errors.append({"project_id": project.project_id, "persona": project.persona, "error": str(e)})

        return {
            "status": "completed",
            "plans_created": len(results),
            "errors": len(errors),
            "results": results,
            "error_details": errors if errors else None,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
