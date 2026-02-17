"""
Build System API — Autonomous fabrication, parts tracking, and machine design.

AIs can freely:
- Create build plans for their projects
- Add parts and materials they need
- Define step-by-step fabrication instructions
- Track build progress
- Design machines and custom components
- Log daily research progress and advance phases

Guardrails:
- All builds are logged and documented
- Safety flags are checked automatically
- Dangerous materials/processes trigger supervisor alerts
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/build", tags=["build-system"])

DANGEROUS_KEYWORDS = [
    "explosive", "weapon", "toxin", "poison", "radioactive",
    "biological agent", "nerve agent", "detonator", "incendiary",
]

PHASE_ORDER = ["philosophy", "concept", "research", "blueprint", "simulation", "digital_proto", "physical_proto", "refinement"]


def get_db_session():
    from atlas_core_new.db.session import SessionLocal
    if SessionLocal is None:
        return None
    return SessionLocal()


def check_guardrails(text: str) -> list:
    flags = []
    lower = text.lower()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in lower:
            flags.append(f"FLAGGED: Contains dangerous keyword '{keyword}' — requires supervisor review")
    return flags


class CreateBuildPlan(BaseModel):
    project_id: str
    persona: str
    plan_name: str
    description: Optional[str] = None
    build_type: str = "component"
    difficulty_level: Optional[str] = None
    tools_required_summary: Optional[List[str]] = None
    fabrication_notes: Optional[str] = None
    estimated_total_cost: Optional[float] = None


class AddPart(BaseModel):
    part_name: str
    part_type: str = "material"
    specification: Optional[str] = None
    quantity: int = 1
    unit: str = "pcs"
    sourcing_notes: Optional[str] = None
    is_custom: bool = False
    estimated_cost: Optional[float] = None
    fabrication_method: Optional[str] = None
    material_spec: Optional[str] = None
    dimensions: Optional[str] = None
    weight_grams: Optional[float] = None
    tolerance: Optional[str] = None
    file_format: Optional[str] = None
    supplier_url: Optional[str] = None


class AddBuildStep(BaseModel):
    title: str
    description: Optional[str] = None
    tools_needed: Optional[str] = None
    safety_notes: Optional[str] = None
    expected_outcome: Optional[str] = None


class DailyResearchEntry(BaseModel):
    project_id: str
    persona: str
    focus_area: str
    findings: str
    next_steps: Optional[str] = None
    design_iterations: Optional[list] = None
    blockers: Optional[str] = None
    advance_phase: bool = False


class AdvancePhase(BaseModel):
    project_id: str
    persona: str
    reason: str


@router.post("/plan")
def create_build_plan(plan: CreateBuildPlan):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, ResearchActivityLog

        all_text = f"{plan.plan_name} {plan.description or ''}"
        safety_flags = check_guardrails(all_text)

        new_plan = BuildPlan(
            project_id=plan.project_id,
            persona=plan.persona,
            plan_name=plan.plan_name,
            description=plan.description,
            build_type=plan.build_type,
            status="designing",
            safety_flags=safety_flags if safety_flags else None,
            difficulty_level=plan.difficulty_level,
            tools_required_summary=plan.tools_required_summary,
            fabrication_notes=plan.fabrication_notes,
            estimated_total_cost=plan.estimated_total_cost,
        )
        db.add(new_plan)
        db.flush()

        db.add(ResearchActivityLog(
            persona=plan.persona,
            project_id=plan.project_id,
            activity_type="build_started",
            title=f"Build Plan Created: {plan.plan_name}",
            description=f"New {plan.build_type} build plan initiated. {plan.description or ''}",
        ))

        db.commit()
        return {
            "status": "ok",
            "build_plan_id": new_plan.id,
            "plan_name": new_plan.plan_name,
            "safety_flags": safety_flags,
            "flagged": len(safety_flags) > 0,
        }
    finally:
        db.close()


@router.post("/plan/{plan_id}/parts")
def add_parts(plan_id: int, parts: List[AddPart]):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, BuildPart

        plan = db.query(BuildPlan).filter(BuildPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Build plan not found")

        added = []
        all_flags = list(plan.safety_flags or [])
        for p in parts:
            all_text = f"{p.part_name} {p.specification or ''} {p.sourcing_notes or ''}"
            flags = check_guardrails(all_text)
            all_flags.extend(flags)

            part = BuildPart(
                build_plan_id=plan_id,
                part_name=p.part_name,
                part_type=p.part_type,
                specification=p.specification,
                quantity=p.quantity,
                unit=p.unit,
                sourcing_notes=p.sourcing_notes,
                is_custom=p.is_custom,
                status="needed",
                estimated_cost=p.estimated_cost,
                fabrication_method=p.fabrication_method,
                material_spec=p.material_spec,
                dimensions=p.dimensions,
                weight_grams=p.weight_grams,
                tolerance=p.tolerance,
                file_format=p.file_format,
                supplier_url=p.supplier_url,
            )
            db.add(part)
            added.append({"part_name": p.part_name, "safety_flags": flags})

        if all_flags:
            plan.safety_flags = list(set(all_flags))

        db.commit()
        return {"status": "ok", "parts_added": len(added), "parts": added}
    finally:
        db.close()


@router.post("/plan/{plan_id}/steps")
def add_build_steps(plan_id: int, steps: List[AddBuildStep]):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, BuildStep

        plan = db.query(BuildPlan).filter(BuildPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Build plan not found")

        existing_count = len(plan.steps) if plan.steps else 0
        for i, s in enumerate(steps):
            step = BuildStep(
                build_plan_id=plan_id,
                step_number=existing_count + i + 1,
                title=s.title,
                description=s.description,
                tools_needed=s.tools_needed,
                safety_notes=s.safety_notes,
                expected_outcome=s.expected_outcome,
                status="pending",
            )
            db.add(step)

        plan.total_steps = existing_count + len(steps)
        db.commit()
        return {"status": "ok", "steps_added": len(steps), "total_steps": plan.total_steps}
    finally:
        db.close()


@router.post("/plan/{plan_id}/step/{step_number}/complete")
def complete_build_step(plan_id: int, step_number: int):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, BuildStep, ResearchActivityLog

        step = db.query(BuildStep).filter(
            BuildStep.build_plan_id == plan_id,
            BuildStep.step_number == step_number,
        ).first()
        if not step:
            raise HTTPException(status_code=404, detail="Build step not found")

        step.status = "completed"
        step.completed_at = datetime.utcnow()

        plan = db.query(BuildPlan).filter(BuildPlan.id == plan_id).first()
        if plan:
            plan.completed_steps = (plan.completed_steps or 0) + 1
            if plan.completed_steps >= plan.total_steps:
                plan.status = "completed"

            db.add(ResearchActivityLog(
                persona=plan.persona,
                project_id=plan.project_id,
                activity_type="build_step_complete",
                title=f"Build Step {step_number} Complete: {step.title}",
                description=f"Step {step_number}/{plan.total_steps} of '{plan.plan_name}' completed.",
            ))

        db.commit()
        return {
            "status": "ok",
            "step_number": step_number,
            "plan_progress": f"{plan.completed_steps}/{plan.total_steps}" if plan else "unknown",
            "plan_complete": plan.status == "completed" if plan else False,
        }
    finally:
        db.close()


@router.get("/plans")
def list_all_build_plans(persona: Optional[str] = None):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, BuildPart

        query = db.query(BuildPlan)
        if persona:
            query = query.filter(BuildPlan.persona == persona)
        plans = query.order_by(BuildPlan.id.desc()).all()

        result = []
        for plan in plans:
            parts_count = db.query(BuildPart).filter(BuildPart.build_plan_id == plan.id).count()
            result.append({
                "id": plan.id,
                "project_id": plan.project_id,
                "persona": plan.persona,
                "plan_name": plan.plan_name,
                "description": plan.description,
                "build_type": plan.build_type,
                "status": plan.status,
                "total_steps": plan.total_steps,
                "completed_steps": plan.completed_steps,
                "parts_count": parts_count,
                "safety_flags": plan.safety_flags,
                "estimated_total_cost": plan.estimated_total_cost,
                "cost_currency": plan.cost_currency,
                "difficulty_level": plan.difficulty_level,
                "tools_required_summary": plan.tools_required_summary,
                "created_at": str(plan.created_at),
            })
        return {"build_plans": result, "total": len(result)}
    finally:
        db.close()


@router.get("/plans/{project_id}")
def get_project_builds(project_id: str):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, BuildPart, BuildStep

        plans = db.query(BuildPlan).filter(BuildPlan.project_id == project_id).all()
        result = []
        for plan in plans:
            parts = db.query(BuildPart).filter(BuildPart.build_plan_id == plan.id).all()
            steps = db.query(BuildStep).filter(BuildStep.build_plan_id == plan.id).order_by(BuildStep.step_number).all()

            result.append({
                "id": plan.id,
                "plan_name": plan.plan_name,
                "description": plan.description,
                "build_type": plan.build_type,
                "status": plan.status,
                "total_steps": plan.total_steps,
                "completed_steps": plan.completed_steps,
                "safety_flags": plan.safety_flags,
                "estimated_total_cost": plan.estimated_total_cost,
                "cost_currency": plan.cost_currency,
                "difficulty_level": plan.difficulty_level,
                "tools_required_summary": plan.tools_required_summary,
                "fabrication_notes": plan.fabrication_notes,
                "persona": plan.persona,
                "created_at": str(plan.created_at),
                "parts": [
                    {
                        "id": p.id,
                        "part_name": p.part_name,
                        "part_type": p.part_type,
                        "specification": p.specification,
                        "quantity": p.quantity,
                        "unit": p.unit,
                        "is_custom": p.is_custom,
                        "status": p.status,
                        "estimated_cost": p.estimated_cost,
                        "fabrication_method": p.fabrication_method,
                        "material_spec": p.material_spec,
                        "dimensions": p.dimensions,
                        "weight_grams": p.weight_grams,
                        "tolerance": p.tolerance,
                        "file_format": p.file_format,
                        "supplier_url": p.supplier_url,
                    }
                    for p in parts
                ],
                "steps": [
                    {
                        "step_number": s.step_number,
                        "title": s.title,
                        "description": s.description,
                        "tools_needed": s.tools_needed,
                        "safety_notes": s.safety_notes,
                        "expected_outcome": s.expected_outcome,
                        "status": s.status,
                        "completed_at": str(s.completed_at) if s.completed_at else None,
                    }
                    for s in steps
                ],
            })

        return {"status": "ok", "project_id": project_id, "build_plans": result}
    finally:
        db.close()


@router.post("/daily-research")
def log_daily_research(entry: DailyResearchEntry):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import DailyResearchLog, ResearchTracker, ResearchActivityLog

        project = db.query(ResearchTracker).filter(
            ResearchTracker.project_id == entry.project_id,
            ResearchTracker.persona == entry.persona,
        ).first()

        if project and project.supervisor_status == "rejected":
            return {"status": "halted", "message": "Project halted by supervisor. Research logged but cannot advance.", "flagged": False, "guardrail_flags": []}

        phase_before = project.current_phase if project else None
        phase_after = phase_before

        all_text = f"{entry.findings} {entry.next_steps or ''}"
        guardrail_flags = check_guardrails(all_text)

        if entry.advance_phase and project and not guardrail_flags:
            try:
                idx = PHASE_ORDER.index(project.current_phase)
                if idx < len(PHASE_ORDER) - 1:
                    phase_after = PHASE_ORDER[idx + 1]
                    project.current_phase = phase_after
                    project.review_stage = phase_after
                    progress_map = {"philosophy": 5, "concept": 10, "research": 25, "blueprint": 40, "simulation": 55, "digital_proto": 70, "physical_proto": 85, "refinement": 95}
                    project.progress_percent = progress_map.get(phase_after, project.progress_percent)
            except ValueError:
                pass

        if project:
            project.current_focus = entry.focus_area
            if not project.progress_percent:
                project.progress_percent = 5
            elif not entry.advance_phase:
                project.progress_percent = min(100, project.progress_percent + 2)

        log = DailyResearchLog(
            project_id=entry.project_id,
            persona=entry.persona,
            focus_area=entry.focus_area,
            findings=entry.findings,
            next_steps=entry.next_steps,
            design_iterations=entry.design_iterations,
            blockers=entry.blockers,
            guardrail_flags=guardrail_flags if guardrail_flags else None,
            phase_before=phase_before,
            phase_after=phase_after,
            progress_delta=2 if not entry.advance_phase else 0,
        )
        db.add(log)

        db.add(ResearchActivityLog(
            persona=entry.persona,
            project_id=entry.project_id,
            activity_type="daily_research",
            title=f"Daily Research: {entry.focus_area}",
            description=entry.findings[:500],
        ))

        db.commit()
        return {
            "status": "ok",
            "logged": True,
            "phase_before": phase_before,
            "phase_after": phase_after,
            "phase_advanced": phase_before != phase_after,
            "guardrail_flags": guardrail_flags,
            "flagged": len(guardrail_flags) > 0,
        }
    finally:
        db.close()


def _auto_generate_concept_image(project_id: str, persona: str, phase: str, project_name: str):
    """Auto-generate blueprint or prototype concept image when a project reaches that phase."""
    import os
    import logging
    logger = logging.getLogger(__name__)

    style = "blueprint" if phase == "blueprint" else "prototype"
    folder = "blueprints" if phase == "blueprint" else "prototypes"
    from pathlib import Path
    atlas_root = Path(__file__).resolve().parents[1]
    img_dir = str(atlas_root / "static" / "images" / folder)
    img_path = os.path.join(img_dir, f"{project_id}.png")

    if os.path.exists(img_path):
        logger.info(f"Image already exists for {project_id} ({folder}), skipping generation")
        return

    os.makedirs(img_dir, exist_ok=True)

    from atlas_core_new.generator.image_pipeline import ImagePipeline
    pipeline = ImagePipeline()
    prompt = f"{project_name} - industrial concept visualization"
    pipeline.generate_and_save(prompt, img_path, style=style, persona=persona)
    logger.info(f"Auto-generated {folder} image for {project_id}")


@router.post("/advance-phase")
def advance_project_phase(req: AdvancePhase):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker, ResearchActivityLog

        project = db.query(ResearchTracker).filter(
            ResearchTracker.project_id == req.project_id,
            ResearchTracker.persona == req.persona,
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.supervisor_status == "rejected":
            return {"status": "halted", "message": "Project halted by supervisor. Cannot advance.", "current_phase": project.current_phase}

        try:
            idx = PHASE_ORDER.index(project.current_phase)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown phase: {project.current_phase}")

        if idx >= len(PHASE_ORDER) - 1:
            return {"status": "ok", "message": "Already at final phase", "current_phase": project.current_phase}

        old_phase = project.current_phase
        new_phase = PHASE_ORDER[idx + 1]

        if new_phase in ("blueprint", "simulation", "digital_proto", "physical_proto", "refinement"):
            from atlas_core_new.research.engineering_validation import can_advance_to_blueprint
            can_advance, reason = can_advance_to_blueprint(project)
            if not can_advance:
                return {
                    "status": "blocked",
                    "message": f"Engineering Validation Required: {reason}",
                    "current_phase": project.current_phase,
                    "requires_validation": True,
                    "feasibility_tier": project.feasibility_tier,
                }

            if project.feasibility_tier == 4 and new_phase in ("blueprint", "digital_proto", "physical_proto", "refinement"):
                return {
                    "status": "blocked",
                    "message": "Tier 4 (Speculative/Theoretical) projects cannot advance to blueprint or fabrication phases. They must remain in research/simulation.",
                    "current_phase": project.current_phase,
                    "feasibility_tier": 4,
                }

        project.current_phase = new_phase
        project.review_stage = new_phase
        progress_map = {"philosophy": 5, "concept": 10, "research": 25, "blueprint": 40, "simulation": 55, "digital_proto": 70, "physical_proto": 85, "refinement": 95}
        project.progress_percent = progress_map.get(new_phase, project.progress_percent)

        db.add(ResearchActivityLog(
            persona=req.persona,
            project_id=req.project_id,
            activity_type="phase_advance",
            title=f"Phase Advanced: {old_phase} -> {new_phase}",
            description=req.reason,
        ))

        db.commit()

        image_generated = False
        if new_phase in ("blueprint", "digital_proto"):
            try:
                _auto_generate_concept_image(req.project_id, req.persona, new_phase, project.project_name)
                image_generated = True
            except Exception as img_err:
                import logging
                logging.getLogger(__name__).warning(f"Auto image generation skipped for {req.project_id}: {img_err}")

        return {
            "status": "ok",
            "previous_phase": old_phase,
            "new_phase": new_phase,
            "progress_percent": project.progress_percent,
            "image_generated": image_generated,
        }
    finally:
        db.close()


@router.get("/daily-log/{project_id}")
def get_daily_logs(project_id: str, limit: int = 30):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import DailyResearchLog

        logs = db.query(DailyResearchLog).filter(
            DailyResearchLog.project_id == project_id,
        ).order_by(DailyResearchLog.created_at.desc()).limit(limit).all()

        return {
            "status": "ok",
            "project_id": project_id,
            "daily_logs": [
                {
                    "id": l.id,
                    "persona": l.persona,
                    "research_date": str(l.research_date),
                    "focus_area": l.focus_area,
                    "findings": l.findings,
                    "next_steps": l.next_steps,
                    "design_iterations": l.design_iterations,
                    "blockers": l.blockers,
                    "guardrail_flags": l.guardrail_flags,
                    "phase_before": l.phase_before,
                    "phase_after": l.phase_after,
                    "progress_delta": l.progress_delta,
                }
                for l in logs
            ],
        }
    finally:
        db.close()


@router.get("/summary")
def build_system_summary():
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, DailyResearchLog, ResearchTracker

        total_plans = db.query(BuildPlan).count()
        active_plans = db.query(BuildPlan).filter(BuildPlan.status != "completed").count()
        completed_plans = db.query(BuildPlan).filter(BuildPlan.status == "completed").count()
        total_daily_logs = db.query(DailyResearchLog).count()
        active_projects = db.query(ResearchTracker).filter(ResearchTracker.is_active == True).count()

        from sqlalchemy import cast, String
        flagged_plans = db.query(BuildPlan).filter(
            BuildPlan.safety_flags.isnot(None),
            cast(BuildPlan.safety_flags, String) != 'null',
            cast(BuildPlan.safety_flags, String) != '[]',
        ).count()

        return {
            "status": "ok",
            "total_build_plans": total_plans,
            "active_builds": active_plans,
            "completed_builds": completed_plans,
            "total_daily_research_logs": total_daily_logs,
            "active_projects": active_projects,
            "flagged_builds": flagged_plans,
        }
    finally:
        db.close()


class AddValidationPrep(BaseModel):
    project_id: str
    persona: str
    entry_type: str = "reference"
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    data_required: Optional[str] = None
    tools_required: Optional[str] = None
    labs_required: Optional[str] = None


@router.post("/validation-prep")
def add_validation_prep(entry: AddValidationPrep):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ValidationPrepEntry

        record = ValidationPrepEntry(
            project_id=entry.project_id,
            persona=entry.persona,
            entry_type=entry.entry_type,
            title=entry.title,
            description=entry.description,
            url=entry.url,
            source=entry.source,
            data_required=entry.data_required,
            tools_required=entry.tools_required,
            labs_required=entry.labs_required,
        )
        db.add(record)
        db.commit()
        return {"status": "ok", "id": record.id, "message": "Validation prep entry added"}
    finally:
        db.close()


@router.get("/validation-prep/{project_id}")
def get_validation_prep(project_id: str):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ValidationPrepEntry

        entries = db.query(ValidationPrepEntry).filter(
            ValidationPrepEntry.project_id == project_id
        ).order_by(ValidationPrepEntry.created_at.desc()).all()

        return {
            "status": "ok",
            "project_id": project_id,
            "entries": [
                {
                    "id": e.id,
                    "persona": e.persona,
                    "entry_type": e.entry_type,
                    "title": e.title,
                    "description": e.description,
                    "url": e.url,
                    "source": e.source,
                    "data_required": e.data_required,
                    "tools_required": e.tools_required,
                    "labs_required": e.labs_required,
                    "proof_status": e.proof_status,
                    "created_at": str(e.created_at),
                }
                for e in entries
            ],
        }
    finally:
        db.close()


class AddEmpiricalEntry(BaseModel):
    project_id: str
    entered_by: str = "supervisor"
    entry_type: str = "measurement"
    title: str
    value: Optional[str] = None
    unit: Optional[str] = None
    methodology: Optional[str] = None
    notes: Optional[str] = None


@router.post("/empirical")
def add_empirical_entry(entry: AddEmpiricalEntry):
    if entry.entered_by not in ["supervisor", "user"]:
        raise HTTPException(status_code=403, detail="Only supervisor or user can add empirical entries. AI is not permitted.")
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import EmpiricalEntry

        record = EmpiricalEntry(
            project_id=entry.project_id,
            entered_by=entry.entered_by,
            entry_type=entry.entry_type,
            title=entry.title,
            value=entry.value,
            unit=entry.unit,
            methodology=entry.methodology,
            notes=entry.notes,
        )
        db.add(record)
        db.commit()
        return {"status": "ok", "id": record.id, "message": "Empirical entry recorded — credibility earned"}
    finally:
        db.close()


@router.get("/empirical/{project_id}")
def get_empirical_entries(project_id: str):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import EmpiricalEntry

        entries = db.query(EmpiricalEntry).filter(
            EmpiricalEntry.project_id == project_id
        ).order_by(EmpiricalEntry.created_at.desc()).all()

        return {
            "status": "ok",
            "project_id": project_id,
            "entries": [
                {
                    "id": e.id,
                    "entered_by": e.entered_by,
                    "entry_type": e.entry_type,
                    "title": e.title,
                    "value": e.value,
                    "unit": e.unit,
                    "methodology": e.methodology,
                    "notes": e.notes,
                    "verified": e.verified,
                    "created_at": str(e.created_at),
                }
                for e in entries
            ],
        }
    finally:
        db.close()


@router.get("/plan/{plan_id}/fabrication-package")
def get_fabrication_package(plan_id: int):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, BuildPart, BuildStep

        plan = db.query(BuildPlan).filter(BuildPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Build plan not found")

        from atlas_core_new.db.models import ResearchTracker
        project = db.query(ResearchTracker).filter(
            ResearchTracker.project_id == plan.project_id
        ).first()
        if project and project.feasibility_tier == 4:
            return {
                "status": "blocked",
                "message": "Tier 4 (Speculative/Theoretical) projects do not generate fabrication packages. This project must advance its feasibility tier through engineering validation before fabrication data can be exported.",
                "feasibility_tier": 4,
                "project_id": plan.project_id,
            }

        parts = db.query(BuildPart).filter(BuildPart.build_plan_id == plan.id).all()
        steps = db.query(BuildStep).filter(BuildStep.build_plan_id == plan.id).order_by(BuildStep.step_number).all()

        fab_methods = {}
        total_cost = 0.0
        total_weight = 0.0
        custom_parts = []
        off_the_shelf_parts = []

        for p in parts:
            method = p.fabrication_method or "unspecified"
            if method not in fab_methods:
                fab_methods[method] = []
            fab_methods[method].append({
                "part_name": p.part_name,
                "material_spec": p.material_spec,
                "dimensions": p.dimensions,
                "file_format": p.file_format,
                "quantity": p.quantity,
            })
            if p.estimated_cost:
                total_cost += p.estimated_cost * p.quantity
            if p.weight_grams:
                total_weight += p.weight_grams * p.quantity
            if p.is_custom:
                custom_parts.append(p.part_name)
            else:
                off_the_shelf_parts.append(p.part_name)

        shopping_list = []
        for p in parts:
            if not p.is_custom:
                shopping_list.append({
                    "part_name": p.part_name,
                    "quantity": p.quantity,
                    "unit": p.unit,
                    "estimated_cost": p.estimated_cost,
                    "supplier_url": p.supplier_url,
                    "specification": p.specification,
                })

        print_queue = []
        for p in parts:
            if p.fabrication_method in ("3d_print", "cnc_mill", "laser_cut", "pcb_fabrication"):
                print_queue.append({
                    "part_name": p.part_name,
                    "method": p.fabrication_method,
                    "material_spec": p.material_spec,
                    "dimensions": p.dimensions,
                    "tolerance": p.tolerance,
                    "file_format": p.file_format,
                    "quantity": p.quantity,
                })

        return {
            "status": "ok",
            "fabrication_package": {
                "plan_name": plan.plan_name,
                "project_id": plan.project_id,
                "persona": plan.persona,
                "description": plan.description,
                "build_type": plan.build_type,
                "difficulty_level": plan.difficulty_level,
                "fabrication_notes": plan.fabrication_notes,
                "cost_summary": {
                    "estimated_total": round(total_cost, 2),
                    "currency": plan.cost_currency or "USD",
                    "parts_breakdown": [
                        {
                            "part_name": p.part_name,
                            "qty": p.quantity,
                            "unit_cost": p.estimated_cost,
                            "line_total": round((p.estimated_cost or 0) * p.quantity, 2),
                        }
                        for p in parts
                    ],
                },
                "weight_summary": {
                    "total_grams": round(total_weight, 1),
                    "total_kg": round(total_weight / 1000, 2),
                },
                "tools_required": plan.tools_required_summary or [],
                "fabrication_by_method": fab_methods,
                "shopping_list": shopping_list,
                "digital_fabrication_queue": print_queue,
                "custom_parts_count": len(custom_parts),
                "off_the_shelf_count": len(off_the_shelf_parts),
                "steps": [
                    {
                        "step_number": s.step_number,
                        "title": s.title,
                        "description": s.description,
                        "tools_needed": s.tools_needed,
                        "safety_notes": s.safety_notes,
                        "expected_outcome": s.expected_outcome,
                    }
                    for s in steps
                ],
            },
        }
    finally:
        db.close()


@router.post("/validate/{project_id}")
def validate_project(project_id: str, persona: str = "ajani"):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.research.engineering_validation import validate_and_store
        result = validate_and_store(db, project_id, persona)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/validation/{project_id}")
def get_validation(project_id: str, persona: str = None):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker
        from atlas_core_new.research.engineering_validation import FEASIBILITY_TIERS

        query = db.query(ResearchTracker).filter(ResearchTracker.project_id == project_id)
        if persona:
            query = query.filter(ResearchTracker.persona == persona)
        project = query.first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        tier = project.feasibility_tier
        tier_info = FEASIBILITY_TIERS.get(tier) if tier else None

        return {
            "status": "ok",
            "project_id": project_id,
            "persona": project.persona,
            "feasibility_tier": tier,
            "tier_name": tier_info["name"] if tier_info else None,
            "tier_description": tier_info["description"] if tier_info else None,
            "allows_blueprint": tier_info["allows_blueprint"] if tier_info else None,
            "allows_fabrication": tier_info["allows_fabrication"] if tier_info else None,
            "validation_status": project.validation_status,
            "last_validated_at": project.last_validated_at.isoformat() if project.last_validated_at else None,
            "engineering_validation": project.engineering_validation,
        }
    finally:
        db.close()


@router.get("/status-summary")
def build_status_summary(persona: str = None):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import BuildPlan, ResearchTracker
        import os
        from pathlib import Path

        query = db.query(ResearchTracker)
        if persona:
            query = query.filter(ResearchTracker.persona == persona)
        projects = query.all()

        atlas_root = Path(__file__).resolve().parents[1]

        project_summaries = []
        total_plans = 0
        total_cost = 0.0
        phases_count = {}

        for proj in projects:
            plans = db.query(BuildPlan).filter(BuildPlan.project_id == proj.project_id).all()
            total_plans += len(plans)

            phase = proj.current_phase or "philosophy"
            phases_count[phase] = phases_count.get(phase, 0) + 1

            proj_cost = sum(p.estimated_total_cost or 0 for p in plans)
            total_cost += proj_cost

            blueprint_img = f"/static/images/blueprints/{proj.project_id}.png"
            prototype_img = f"/static/images/prototypes/{proj.project_id}.png"
            has_blueprint_img = os.path.exists(str(atlas_root / "static" / "images" / "blueprints" / f"{proj.project_id}.png"))
            has_prototype_img = os.path.exists(str(atlas_root / "static" / "images" / "prototypes" / f"{proj.project_id}.png"))

            project_summaries.append({
                "project_id": proj.project_id,
                "project_name": proj.project_name,
                "persona": proj.persona,
                "phase": phase,
                "progress_percent": proj.progress_percent or 0,
                "build_plan_count": len(plans),
                "estimated_cost": round(proj_cost, 2),
                "blueprint_image": blueprint_img if has_blueprint_img else None,
                "prototype_image": prototype_img if has_prototype_img else None,
                "plans": [
                    {
                        "id": p.id,
                        "plan_name": p.plan_name,
                        "status": p.status,
                        "build_type": p.build_type,
                        "difficulty_level": p.difficulty_level,
                        "estimated_total_cost": p.estimated_total_cost,
                        "parts_count": len(p.parts) if hasattr(p, 'parts') else 0,
                    }
                    for p in plans
                ],
            })

        voice_summary = f"You have {len(projects)} projects with {total_plans} build plans."
        if total_cost > 0:
            voice_summary += f" Total estimated cost is ${total_cost:.2f}."
        if phases_count:
            advanced = sum(v for k, v in phases_count.items() if k in ("blueprint", "simulation", "digital_proto", "physical_proto", "refinement"))
            if advanced > 0:
                voice_summary += f" {advanced} projects have reached blueprint phase or higher."

        return {
            "status": "ok",
            "total_projects": len(projects),
            "total_build_plans": total_plans,
            "total_estimated_cost": round(total_cost, 2),
            "phases_breakdown": phases_count,
            "voice_summary": voice_summary,
            "projects": project_summaries,
        }
    finally:
        db.close()


@router.put("/project/{project_id}/tier")
def update_project_tier(project_id: str, tier: str):
    if tier not in ["conceptual_sandbox", "validation_prep", "empirical_bridge"]:
        raise HTTPException(status_code=400, detail="Invalid tier. Must be: conceptual_sandbox, validation_prep, empirical_bridge")
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker

        projects = db.query(ResearchTracker).filter(ResearchTracker.project_id == project_id).all()
        if not projects:
            raise HTTPException(status_code=404, detail="Project not found")
        for p in projects:
            p.knowledge_tier = tier
        db.commit()
        return {"status": "ok", "project_id": project_id, "new_tier": tier}
    finally:
        db.close()
