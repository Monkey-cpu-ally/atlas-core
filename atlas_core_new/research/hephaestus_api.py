"""
atlas_core_new/research/hephaestus_api.py

API endpoints for the Hephaestus-lite Discovery Pipeline.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, desc
from atlas_core_new.db.models import ExperimentRun, FailureMode, ConstraintSet, IterationLog
from atlas_core_new.research.hephaestus_engine import (
    PIPELINE_PHASES, PHASE_LABELS, PHASE_PERSONA, PHASE_DESCRIPTIONS,
    INNOVATION_LEVELS, SCIENTIFIC_DOMAINS, DOMAIN_LABELS,
    generate_run_id, get_domain_intersection, get_all_intersections_for_domain,
    get_default_constraints, score_innovation_level, get_pipeline_status, next_phase
)


def get_db_session():
    from atlas_core_new.db.session import SessionLocal
    if SessionLocal is None:
        raise HTTPException(500, "Database not available")
    return SessionLocal()


router = APIRouter(prefix="/hephaestus", tags=["Discovery Pipeline"])


class CreateRunRequest(BaseModel):
    project_id: str
    domain_primary: str
    domain_secondary: Optional[str] = None
    hypothesis: str
    max_iterations: int = 100


class AdvancePhaseRequest(BaseModel):
    model_spec: Optional[str] = None
    sim_parameters: Optional[dict] = None
    sim_results: Optional[dict] = None
    notes: Optional[str] = None


class LogIterationRequest(BaseModel):
    persona: str
    action: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    adjustments: Optional[dict] = None
    failure_modes_found: int = 0
    score_before: Optional[float] = None
    score_after: Optional[float] = None
    notes: Optional[str] = None


class AddFailureModeRequest(BaseModel):
    failure_type: str
    severity: str = "medium"
    description: str
    evidence: Optional[str] = None
    mitigation: Optional[str] = None
    iteration_found: int = 0


class CreateConstraintRequest(BaseModel):
    project_id: str
    domain: str
    physics_laws: Optional[list] = None
    materials_available: Optional[list] = None
    manufacturing_tools: Optional[list] = None
    energy_requirements: Optional[dict] = None
    safety_profile: Optional[list] = None
    failure_envelope: Optional[list] = None
    cost_constraints: Optional[dict] = None


@router.get("/dashboard")
def hephaestus_dashboard():
    db = get_db_session()
    try:
        runs = db.execute(
            select(ExperimentRun).order_by(desc(ExperimentRun.updated_at)).limit(20)
        ).scalars().all()

        active_runs = []
        for run in runs:
            fm_list = db.execute(
                select(FailureMode).where(FailureMode.run_id == run.run_id)
            ).scalars().all()
            resolved = sum(1 for fm in fm_list if fm.resolved)

            iter_list = db.execute(
                select(IterationLog).where(IterationLog.run_id == run.run_id)
            ).scalars().all()

            pipeline = get_pipeline_status(run.phase)

            active_runs.append({
                "run_id": run.run_id,
                "project_id": run.project_id,
                "domain_primary": run.domain_primary,
                "domain_primary_label": DOMAIN_LABELS.get(run.domain_primary, run.domain_primary),
                "domain_secondary": run.domain_secondary,
                "domain_secondary_label": DOMAIN_LABELS.get(run.domain_secondary, "") if run.domain_secondary else None,
                "intersection_hypothesis": run.intersection_hypothesis,
                "hypothesis": run.hypothesis,
                "phase": run.phase,
                "phase_label": PHASE_LABELS.get(run.phase, run.phase),
                "pipeline": pipeline,
                "innovation_level": run.innovation_level,
                "innovation_label": INNOVATION_LEVELS.get(run.innovation_level, {}).get("name", "Unknown"),
                "iteration_count": run.iteration_count,
                "max_iterations": run.max_iterations,
                "failure_modes_total": len(fm_list),
                "failure_modes_resolved": resolved,
                "total_iterations_logged": len(iter_list),
                "status": run.status,
                "created_at": run.created_at.isoformat() if run.created_at else None,
                "updated_at": run.updated_at.isoformat() if run.updated_at else None
            })
    finally:
        db.close()

    return {
        "status": "ok",
        "runs": active_runs,
        "total_runs": len(active_runs),
        "domains": [{"id": d, "label": DOMAIN_LABELS.get(d, d)} for d in SCIENTIFIC_DOMAINS],
        "innovation_levels": INNOVATION_LEVELS,
        "pipeline_phases": [{"id": p, "label": PHASE_LABELS[p], "persona": PHASE_PERSONA[p]} for p in PIPELINE_PHASES]
    }


@router.post("/runs")
def create_run(req: CreateRunRequest):
    run_id = generate_run_id()
    intersection = None
    if req.domain_secondary:
        ix = get_domain_intersection(req.domain_primary, req.domain_secondary)
        if ix:
            intersection = f"{ix['name']}: {ix['potential']}"

    db = get_db_session()
    try:
        run = ExperimentRun(
            run_id=run_id,
            project_id=req.project_id,
            domain_primary=req.domain_primary,
            domain_secondary=req.domain_secondary,
            intersection_hypothesis=intersection,
            phase="idea",
            hypothesis=req.hypothesis,
            max_iterations=req.max_iterations,
            innovation_level=1,
            innovation_label="creative_remix",
            assigned_personas={"ajani": "theorist", "hermes": "simulator", "minerva": "evaluator"},
            status="active"
        )
        db.add(run)

        default_constraints = get_default_constraints(req.domain_primary)
        cs = ConstraintSet(
            project_id=req.project_id,
            domain=req.domain_primary,
            physics_laws=default_constraints.get("physics_laws"),
            materials_available=default_constraints.get("materials_available"),
            manufacturing_tools=default_constraints.get("manufacturing_tools"),
            energy_requirements=default_constraints.get("energy_requirements"),
            safety_profile=default_constraints.get("safety_profile"),
            failure_envelope=default_constraints.get("failure_envelope")
        )
        db.add(cs)
        db.commit()

        run.constraint_set_id = cs.id
        db.commit()

        initial_log = IterationLog(
            run_id=run_id,
            iteration_number=0,
            persona="ajani",
            action="hypothesis_proposed",
            input_data={"domain": req.domain_primary, "secondary": req.domain_secondary},
            output_data={"hypothesis": req.hypothesis, "intersection": intersection},
            notes="Initial hypothesis submitted to Discovery Pipeline"
        )
        db.add(initial_log)
        db.commit()
    finally:
        db.close()

    return {
        "status": "ok",
        "run_id": run_id,
        "phase": "idea",
        "message": f"Discovery Pipeline initiated for {DOMAIN_LABELS.get(req.domain_primary, req.domain_primary)}"
    }


@router.get("/runs/{run_id}")
def get_run_detail(run_id: str):
    db = get_db_session()
    try:
        run = db.execute(
            select(ExperimentRun).where(ExperimentRun.run_id == run_id)
        ).scalar_one_or_none()
        if not run:
            raise HTTPException(404, "Experiment run not found")

        fms = db.execute(
            select(FailureMode).where(FailureMode.run_id == run_id).order_by(desc(FailureMode.created_at))
        ).scalars().all()

        iters = db.execute(
            select(IterationLog).where(IterationLog.run_id == run_id).order_by(desc(IterationLog.created_at)).limit(20)
        ).scalars().all()

        constraints = None
        if run.constraint_set_id:
            cs = db.execute(
                select(ConstraintSet).where(ConstraintSet.id == run.constraint_set_id)
            ).scalar_one_or_none()
            if cs:
                constraints = {
                    "physics_laws": cs.physics_laws,
                    "materials_available": cs.materials_available,
                    "manufacturing_tools": cs.manufacturing_tools,
                    "energy_requirements": cs.energy_requirements,
                    "safety_profile": cs.safety_profile,
                    "failure_envelope": cs.failure_envelope,
                    "cost_constraints": cs.cost_constraints
                }

        pipeline = get_pipeline_status(run.phase)
        intersections = get_all_intersections_for_domain(run.domain_primary)

        result = {
            "status": "ok",
            "run": {
                "run_id": run.run_id,
                "project_id": run.project_id,
                "domain_primary": run.domain_primary,
                "domain_primary_label": DOMAIN_LABELS.get(run.domain_primary, run.domain_primary),
                "domain_secondary": run.domain_secondary,
                "domain_secondary_label": DOMAIN_LABELS.get(run.domain_secondary, "") if run.domain_secondary else None,
                "intersection_hypothesis": run.intersection_hypothesis,
                "hypothesis": run.hypothesis,
                "model_spec": run.model_spec,
                "sim_parameters": run.sim_parameters,
                "sim_results": run.sim_results,
                "phase": run.phase,
                "pipeline": pipeline,
                "innovation_level": run.innovation_level,
                "innovation_label": INNOVATION_LEVELS.get(run.innovation_level, {}).get("name", "Unknown"),
                "iteration_count": run.iteration_count,
                "max_iterations": run.max_iterations,
                "status": run.status,
                "created_at": run.created_at.isoformat() if run.created_at else None,
                "updated_at": run.updated_at.isoformat() if run.updated_at else None
            },
            "constraints": constraints,
            "failure_modes": [
                {
                    "id": fm.id,
                    "failure_type": fm.failure_type,
                    "severity": fm.severity,
                    "description": fm.description,
                    "evidence": fm.evidence,
                    "mitigation": fm.mitigation,
                    "resolved": fm.resolved,
                    "iteration_found": fm.iteration_found
                } for fm in fms
            ],
            "iterations": [
                {
                    "id": it.id,
                    "iteration_number": it.iteration_number,
                    "persona": it.persona,
                    "action": it.action,
                    "input_data": it.input_data,
                    "output_data": it.output_data,
                    "adjustments": it.adjustments,
                    "failure_modes_found": it.failure_modes_found,
                    "score_before": it.score_before,
                    "score_after": it.score_after,
                    "notes": it.notes,
                    "created_at": it.created_at.isoformat() if it.created_at else None
                } for it in iters
            ],
            "available_intersections": intersections
        }
    finally:
        db.close()
    return result


@router.post("/runs/{run_id}/advance")
def advance_phase(run_id: str, req: AdvancePhaseRequest):
    db = get_db_session()
    try:
        run = db.execute(
            select(ExperimentRun).where(ExperimentRun.run_id == run_id)
        ).scalar_one_or_none()
        if not run:
            raise HTTPException(404, "Run not found")

        old_phase = run.phase
        new_phase = next_phase(old_phase)

        if new_phase == old_phase:
            return {"status": "ok", "message": "Already at final phase", "phase": old_phase}

        run.phase = new_phase
        if req.model_spec:
            run.model_spec = req.model_spec
        if req.sim_parameters:
            run.sim_parameters = req.sim_parameters
        if req.sim_results:
            run.sim_results = req.sim_results

        fm_list = db.execute(
            select(FailureMode).where(FailureMode.run_id == run_id)
        ).scalars().all()
        fm_count = len(fm_list)
        resolved = sum(1 for fm in fm_list if fm.resolved)

        new_level = score_innovation_level({
            "domain_secondary": run.domain_secondary,
            "iteration_count": run.iteration_count,
            "failure_modes_count": fm_count,
            "resolved_count": resolved,
            "phase": new_phase
        })
        run.innovation_level = new_level
        run.innovation_label = INNOVATION_LEVELS.get(new_level, {}).get("label", "creative_remix")

        log = IterationLog(
            run_id=run_id,
            iteration_number=run.iteration_count,
            persona=PHASE_PERSONA.get(new_phase, "ajani"),
            action=f"phase_advanced:{old_phase}->{new_phase}",
            notes=req.notes or f"Advanced from {PHASE_LABELS.get(old_phase)} to {PHASE_LABELS.get(new_phase)}"
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

    return {
        "status": "ok",
        "old_phase": old_phase,
        "new_phase": new_phase,
        "new_phase_label": PHASE_LABELS.get(new_phase),
        "innovation_level": new_level,
        "pipeline": get_pipeline_status(new_phase)
    }


@router.post("/runs/{run_id}/iterate")
def log_iteration(run_id: str, req: LogIterationRequest):
    db = get_db_session()
    try:
        run = db.execute(
            select(ExperimentRun).where(ExperimentRun.run_id == run_id)
        ).scalar_one_or_none()
        if not run:
            raise HTTPException(404, "Run not found")

        run.iteration_count += 1
        log = IterationLog(
            run_id=run_id,
            iteration_number=run.iteration_count,
            persona=req.persona,
            action=req.action,
            input_data=req.input_data,
            output_data=req.output_data,
            adjustments=req.adjustments,
            failure_modes_found=req.failure_modes_found,
            score_before=req.score_before,
            score_after=req.score_after,
            notes=req.notes
        )
        db.add(log)
        db.commit()
        count = run.iteration_count
    finally:
        db.close()

    return {
        "status": "ok",
        "iteration_number": count,
        "total_iterations": count
    }


@router.post("/runs/{run_id}/failure-modes")
def add_failure_mode(run_id: str, req: AddFailureModeRequest):
    db = get_db_session()
    try:
        run = db.execute(
            select(ExperimentRun).where(ExperimentRun.run_id == run_id)
        ).scalar_one_or_none()
        if not run:
            raise HTTPException(404, "Run not found")

        fm = FailureMode(
            run_id=run_id,
            failure_type=req.failure_type,
            severity=req.severity,
            description=req.description,
            evidence=req.evidence,
            mitigation=req.mitigation,
            iteration_found=req.iteration_found
        )
        db.add(fm)
        db.commit()
        fm_id = fm.id
    finally:
        db.close()

    return {"status": "ok", "failure_mode_id": fm_id}


@router.post("/runs/{run_id}/failure-modes/{fm_id}/resolve")
def resolve_failure_mode(run_id: str, fm_id: int):
    db = get_db_session()
    try:
        fm = db.execute(
            select(FailureMode).where(FailureMode.id == fm_id, FailureMode.run_id == run_id)
        ).scalar_one_or_none()
        if not fm:
            raise HTTPException(404, "Failure mode not found")
        fm.resolved = True
        db.commit()
    finally:
        db.close()
    return {"status": "ok", "resolved": True}


@router.get("/domains")
def list_domains():
    return {
        "status": "ok",
        "domains": [{"id": d, "label": DOMAIN_LABELS.get(d, d)} for d in SCIENTIFIC_DOMAINS],
        "total": len(SCIENTIFIC_DOMAINS)
    }


@router.get("/domains/{domain}/intersections")
def domain_intersections(domain: str):
    intersections = get_all_intersections_for_domain(domain)
    return {
        "status": "ok",
        "domain": domain,
        "domain_label": DOMAIN_LABELS.get(domain, domain),
        "intersections": intersections,
        "total": len(intersections)
    }


@router.get("/domains/{domain}/constraints")
def domain_constraints(domain: str):
    constraints = get_default_constraints(domain)
    return {
        "status": "ok",
        "domain": domain,
        "domain_label": DOMAIN_LABELS.get(domain, domain),
        "constraints": constraints
    }


@router.get("/innovation-levels")
def list_innovation_levels():
    return {
        "status": "ok",
        "levels": INNOVATION_LEVELS
    }
