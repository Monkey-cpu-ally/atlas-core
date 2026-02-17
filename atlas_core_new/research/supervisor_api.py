"""
Supervisor Review System — Guardrails for Autonomous AI Research & Build

PROTOCOL:
- AIs research and build freely — daily, step by step
- Safety guardrails monitor and flag, they do NOT block progress
- AIs can design, fabricate, and build machines/parts they need
- Supervisor monitors via dashboard — intervenes only when guardrails flag danger
- Projects advance automatically as work is completed

RESEARCH PHASES (AIs advance freely):
1. concept        — Initial idea, philosophy, approach defined
2. simulation     — Virtual testing, risk prediction, tradeoff analysis
3. digital_proto  — Digital prototype, architecture validated
4. physical_proto — Physical prototype, fabrication, machine building
5. refinement     — Production-ready, all safety verified

SUPERVISOR ROLE:
- Monitor progress via dashboard (not gate-keeping)
- Review guardrail flags when they fire
- Override or halt only when safety is genuinely at risk
- reject            — Halt project, documented why
- revise            — Send back with specific feedback
- approve_full      — Clear flagged items to continue

AI OPERATING RULES (autonomous with guardrails):
ALLOWED: Research daily, design step by step, build machines and parts,
         fabricate components, advance phases, simulate and test,
         identify and source materials, iterate designs freely
GUARDRAILS: Must document every step, must run safety checks,
            must respect physics/biology/engineering, must log all builds,
            flagged items get supervisor attention automatically
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/supervisor", tags=["supervisor"])

REVIEW_STAGES = ["philosophy", "concept", "research", "blueprint", "simulation", "digital_proto", "physical_proto", "refinement"]
VALID_DECISIONS = ["reject", "revise", "approve_sim", "approve_prototype", "approve_full"]

STAGE_LABELS = {
    "philosophy": "Philosophy",
    "concept": "Concept",
    "research": "Research",
    "blueprint": "Blueprint",
    "simulation": "Simulation",
    "digital_proto": "Digital Prototype",
    "physical_proto": "Physical Prototype",
    "refinement": "Refinement",
}

STAGE_DESCRIPTIONS = {
    "philosophy": "Core philosophy defined — approach, ethics, domain rules established. AIs begin exploring.",
    "concept": "Idea defined — design intent documented. AIs actively researching.",
    "research": "Deep research — gathering knowledge, analyzing prior art, building understanding.",
    "blueprint": "Architecture designed — system blueprints, interfaces, specifications documented.",
    "simulation": "Active testing — simulations running, risks predicted, competing designs iterated.",
    "digital_proto": "Digital prototype built — architecture validated, failure modes tested.",
    "physical_proto": "Physical build — fabricating parts, assembling machines, testing real-world behavior.",
    "refinement": "Production refinement — all builds verified, documentation complete, system polished.",
}

GUARDRAIL_CHECKS = [
    "Does this violate physics, biology, or law?",
    "Are all build steps documented?",
    "What breaks first under stress?",
    "What's the worst-case failure mode?",
    "Is the safety analysis complete for this step?",
    "Are materials and parts properly specified?",
]

AI_RULES = {
    "allowed": [
        "Research daily — gather knowledge, analyze, iterate",
        "Design step by step — detailed plans with specifications",
        "Build machines and parts they need for their projects",
        "Fabricate components — source materials, design tooling",
        "Advance phases freely as work is completed",
        "Simulate and test — run experiments, validate designs",
        "Identify and source materials for builds",
        "Iterate designs without waiting for approval",
        "Create competing designs and pick the best",
        "Document tradeoffs, failure modes, and build logs",
    ],
    "guardrails": [
        "Must document every build step before and after",
        "Must run safety checks on all fabrication",
        "Must respect physics, biology, and engineering limits",
        "Must log all builds, parts, and materials used",
        "Flagged items get supervisor attention automatically",
        "Cannot skip safety analysis on dangerous materials",
        "Cannot build weapons or harmful devices",
    ],
    "golden_rule": "Build freely, build smart, build safe. Document everything.",
}


class ReviewDecision(BaseModel):
    decision: str
    notes: Optional[str] = None
    questions_asked: Optional[str] = None
    safety_flags: Optional[str] = None


class ProjectRecord(BaseModel):
    design_intent: Optional[str] = None
    assumptions: Optional[str] = None
    known_unknowns: Optional[str] = None
    safety_constraints: Optional[str] = None


def get_db_session():
    from atlas_core_new.db.session import SessionLocal
    if SessionLocal is None:
        return None
    return SessionLocal()


@router.get("/protocol")
def get_supervisor_protocol():
    return {
        "status": "ok",
        "protocol": {
            "name": "Autonomous Research with Guardrails",
            "philosophy": "AIs research and build freely, daily, step by step. Guardrails keep them safe. You monitor, not gate-keep.",
            "stages": [
                {"id": s, "name": STAGE_LABELS[s], "description": STAGE_DESCRIPTIONS[s], "order": i}
                for i, s in enumerate(REVIEW_STAGES)
            ],
            "decisions": VALID_DECISIONS,
            "guardrail_checks": GUARDRAIL_CHECKS,
            "ai_rules": AI_RULES,
            "enforcement": "AIs advance freely. Guardrails flag safety issues. You intervene only when needed.",
            "build_capable": True,
            "daily_research": True,
        },
    }


@router.get("/queue")
def get_review_queue():
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker
        projects = db.query(ResearchTracker).filter(
            ResearchTracker.is_active == True
        ).order_by(ResearchTracker.updated_at.desc()).all()

        queue = []
        for p in projects:
            queue.append({
                "project_id": p.project_id,
                "project_name": p.project_name,
                "codename": p.codename,
                "persona": p.persona,
                "current_phase": p.current_phase,
                "review_stage": p.review_stage or "concept",
                "supervisor_status": p.supervisor_status or "pending_review",
                "progress_percent": p.progress_percent,
                "design_intent": p.design_intent,
                "assumptions": p.assumptions,
                "known_unknowns": p.known_unknowns,
                "safety_constraints": p.safety_constraints,
                "current_focus": p.current_focus,
                "last_breakthrough": p.last_breakthrough,
                "knowledge_tier": getattr(p, 'knowledge_tier', 'conceptual_sandbox') or 'conceptual_sandbox',
                "updated_at": str(p.updated_at) if p.updated_at else None,
            })
        return {"status": "ok", "queue": queue, "total": len(queue)}
    finally:
        db.close()


@router.get("/project/{project_id}")
def get_project_review(project_id: str):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker, SupervisorReview
        project = db.query(ResearchTracker).filter(
            ResearchTracker.project_id == project_id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        reviews = db.query(SupervisorReview).filter(
            SupervisorReview.project_id == project_id
        ).order_by(SupervisorReview.created_at.desc()).all()

        return {
            "status": "ok",
            "project": {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "codename": project.codename,
                "persona": project.persona,
                "current_phase": project.current_phase,
                "review_stage": project.review_stage or "concept",
                "supervisor_status": project.supervisor_status or "pending_review",
                "progress_percent": project.progress_percent,
                "design_intent": project.design_intent,
                "assumptions": project.assumptions,
                "known_unknowns": project.known_unknowns,
                "safety_constraints": project.safety_constraints,
                "current_focus": project.current_focus,
                "last_breakthrough": project.last_breakthrough,
            },
            "review_history": [
                {
                    "id": r.id,
                    "review_stage": r.review_stage,
                    "decision": r.decision,
                    "decision_notes": r.decision_notes,
                    "supervisor_questions": r.supervisor_questions,
                    "safety_flags": r.safety_flags,
                    "created_at": str(r.created_at) if r.created_at else None,
                }
                for r in reviews
            ],
            "stage_info": {
                "current": project.review_stage or "concept",
                "current_label": STAGE_LABELS.get(project.review_stage or "concept", "Unknown"),
                "next": _get_next_stage(project.review_stage or "concept"),
                "next_label": STAGE_LABELS.get(_get_next_stage(project.review_stage or "concept") or "", "—"),
                "can_advance": project.supervisor_status == "approved",
            },
        }
    finally:
        db.close()


@router.post("/project/{project_id}/decide")
def submit_review_decision(project_id: str, decision: ReviewDecision):
    if decision.decision not in VALID_DECISIONS:
        raise HTTPException(status_code=400, detail=f"Invalid decision. Must be one of: {VALID_DECISIONS}")

    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker, SupervisorReview

        project = db.query(ResearchTracker).filter(
            ResearchTracker.project_id == project_id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        current_stage = project.review_stage or "concept"

        review = SupervisorReview(
            project_id=project_id,
            persona=project.persona,
            review_stage=current_stage,
            decision=decision.decision,
            decision_notes=decision.notes,
            supervisor_questions=decision.questions_asked,
            safety_flags=decision.safety_flags,
        )
        db.add(review)

        if decision.decision == "reject":
            project.supervisor_status = "rejected"
        elif decision.decision == "revise":
            project.supervisor_status = "revision_requested"
        elif decision.decision in ("approve_sim", "approve_prototype", "approve_full"):
            project.supervisor_status = "approved"
            next_stage = _get_next_stage(current_stage)
            if next_stage:
                project.review_stage = next_stage
                project.supervisor_status = "pending_review"

        from atlas_core_new.db.models import ResearchActivityLog
        activity = ResearchActivityLog(
            persona=project.persona,
            project_id=project_id,
            activity_type="supervisor_review",
            title=f"Supervisor Decision: {decision.decision.replace('_', ' ').title()}",
            description=decision.notes or f"Project reviewed at {current_stage} stage",
        )
        db.add(activity)

        db.commit()

        return {
            "status": "ok",
            "project_id": project_id,
            "decision": decision.decision,
            "previous_stage": current_stage,
            "new_stage": project.review_stage,
            "new_status": project.supervisor_status,
        }
    finally:
        db.close()


@router.post("/project/{project_id}/record")
def update_project_record(project_id: str, record: ProjectRecord):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker
        project = db.query(ResearchTracker).filter(
            ResearchTracker.project_id == project_id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if record.design_intent is not None:
            project.design_intent = record.design_intent
        if record.assumptions is not None:
            project.assumptions = record.assumptions
        if record.known_unknowns is not None:
            project.known_unknowns = record.known_unknowns
        if record.safety_constraints is not None:
            project.safety_constraints = record.safety_constraints

        db.commit()
        return {"status": "ok", "project_id": project_id, "updated": True}
    finally:
        db.close()


@router.get("/history")
def get_all_review_history(limit: int = 50):
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import SupervisorReview
        reviews = db.query(SupervisorReview).order_by(
            SupervisorReview.created_at.desc()
        ).limit(limit).all()
        return {
            "status": "ok",
            "reviews": [
                {
                    "id": r.id,
                    "project_id": r.project_id,
                    "persona": r.persona,
                    "review_stage": r.review_stage,
                    "decision": r.decision,
                    "decision_notes": r.decision_notes,
                    "supervisor_questions": r.supervisor_questions,
                    "safety_flags": r.safety_flags,
                    "created_at": str(r.created_at) if r.created_at else None,
                }
                for r in reviews
            ],
        }
    finally:
        db.close()


@router.get("/stats")
def get_review_stats():
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker, SupervisorReview

        total_projects = db.query(ResearchTracker).count()
        pending = db.query(ResearchTracker).filter(ResearchTracker.supervisor_status == "pending_review").count()
        approved = db.query(ResearchTracker).filter(ResearchTracker.supervisor_status == "approved").count()
        rejected = db.query(ResearchTracker).filter(ResearchTracker.supervisor_status == "rejected").count()
        revision = db.query(ResearchTracker).filter(ResearchTracker.supervisor_status == "revision_requested").count()
        total_reviews = db.query(SupervisorReview).count()

        stage_counts = {}
        for stage in REVIEW_STAGES:
            stage_counts[stage] = db.query(ResearchTracker).filter(ResearchTracker.review_stage == stage).count()

        return {
            "status": "ok",
            "total_projects": total_projects,
            "pending_review": pending,
            "approved": approved,
            "rejected": rejected,
            "revision_requested": revision,
            "total_reviews": total_reviews,
            "by_stage": stage_counts,
        }
    finally:
        db.close()


@router.post("/batch-approve")
def batch_approve_all(body: dict = None):
    notes = (body or {}).get("notes", "Batch approved — all projects cleared to advance to next stage.")
    db = get_db_session()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        from atlas_core_new.db.models import ResearchTracker, SupervisorReview, ResearchActivityLog

        projects = db.query(ResearchTracker).filter(
            ResearchTracker.supervisor_status == "pending_review"
        ).all()

        if not projects:
            return {"status": "ok", "message": "No projects pending review", "approved_count": 0}

        approved_count = 0
        results = []
        for project in projects:
            current_stage = project.review_stage or "concept"
            decision_type = "approve_sim"
            if current_stage == "digital_proto":
                decision_type = "approve_prototype"
            elif current_stage in ("physical_proto", "refinement"):
                decision_type = "approve_full"

            review = SupervisorReview(
                project_id=project.project_id,
                persona=project.persona,
                review_stage=current_stage,
                decision=decision_type,
                decision_notes=notes,
            )
            db.add(review)

            next_stage = _get_next_stage(current_stage)
            old_stage = current_stage
            if next_stage:
                project.review_stage = next_stage
                project.supervisor_status = "pending_review"
            else:
                project.supervisor_status = "approved"

            db.add(ResearchActivityLog(
                persona=project.persona,
                project_id=project.project_id,
                activity_type="supervisor_review",
                title=f"Supervisor Batch Approval: {decision_type.replace('_', ' ').title()}",
                description=notes,
            ))

            approved_count += 1
            results.append({
                "project_id": project.project_id,
                "previous_stage": old_stage,
                "new_stage": project.review_stage,
            })

        db.commit()
        return {
            "status": "ok",
            "approved_count": approved_count,
            "results": results,
        }
    finally:
        db.close()


def _get_next_stage(current: str) -> Optional[str]:
    try:
        idx = REVIEW_STAGES.index(current)
        if idx < len(REVIEW_STAGES) - 1:
            return REVIEW_STAGES[idx + 1]
    except ValueError:
        pass
    return None
