"""
Research Tracker API — Edge Panel backend for persona research progress tracking.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from atlas_core_new.db.session import SessionLocal
from atlas_core_new.db.models import ResearchTracker, ResearchActivityLog, ResearchResource, DailyResearchLog
from atlas_core_new.research.persona_research import PERSONA_RESEARCH_PROFILES
from atlas_core_new.research.research_resources_data import RESEARCH_RESOURCES

router = APIRouter(prefix="/research-tracker", tags=["research-tracker"])

PHASE_PROGRESS = {
    "philosophy": 5,
    "concept": 15,
    "research": 30,
    "blueprint": 45,
    "simulation": 60,
    "digital_proto": 75,
    "physical_proto": 85,
    "refinement": 100,
}


def get_db():
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_resources(db: Session):
    db.query(ResearchResource).delete()
    db.flush()

    for project_id, project_data in RESEARCH_RESOURCES.items():
        persona = project_data["persona"]
        for res in project_data["resources"]:
            db.add(ResearchResource(
                persona=persona,
                project_id=project_id,
                resource_type=res["resource_type"],
                title=res["title"],
                description=res["description"],
                url=res.get("url"),
                source=res.get("source"),
                year=res.get("year"),
                is_evidence_based=res.get("is_evidence_based", True),
            ))

    db.flush()


SUPERVISOR_SEED_DATA = {
    "insert-cell": {"design_intent": "Universal power spine — standardized docking, negotiation, and isolation for any energy source", "assumptions": "All energy sources can be abstracted into a common interface; hot-plug is achievable with arc suppression; galvanic isolation prevents cascading failures", "known_unknowns": "Optimal negotiation protocol latency; long-term degradation of isolation barriers under extreme thermal cycling; compatibility with future unknown energy types", "safety_constraints": "Must isolate faults within 50ms; no energy source may bypass negotiation; physical blast containment required; fail-safe defaults to power-off", "review_stage": "simulation"},
    "hydra-core": {"design_intent": "Hydrogen fuel cell engine — clean conversion with no combustion, integrated into INSERT-CELL spine", "assumptions": "PEM fuel cell technology is mature enough for modular integration; hydrogen storage can be safe at small scale; water byproduct is manageable", "known_unknowns": "Membrane durability under rapid load cycling; hydrogen purity requirements at miniature scale; cold-start performance below -10C", "safety_constraints": "Hydrogen leak detection mandatory; no ignition sources within containment zone; pressure relief valves at every storage point; INSERT-CELL isolation required", "review_stage": "simulation"},
    "resonance-engine": {"design_intent": "Acoustic-to-electrical energy conversion engine — harvests ambient sound and vibration", "assumptions": "Piezoelectric materials can achieve useful power density from ambient vibration; resonant frequency tuning is feasible for variable environments", "known_unknowns": "Power output vs size tradeoff at practical scales; efficiency degradation from material fatigue; environmental noise spectrum variability", "safety_constraints": "No harmful acoustic emission; material containment for piezo elements; INSERT-CELL isolation mandatory; output capped to prevent overcurrent", "review_stage": "simulation"},
    "photon-sink": {"design_intent": "Photonic energy harvesting engine — converts light across multiple spectra into usable power", "assumptions": "Multi-junction photovoltaic cells can be miniaturized; spectral splitting is achievable at module scale; thermal management is solvable", "known_unknowns": "Efficiency ceiling at miniature scale; heat dissipation in enclosed environments; degradation rate of experimental PV materials", "safety_constraints": "No concentrated beam outputs; thermal runaway prevention; INSERT-CELL isolation mandatory; UV shielding for exposed components", "review_stage": "concept"},
    "wave-rider": {"design_intent": "RF/electromagnetic energy harvesting engine — captures ambient RF energy for low-power applications", "assumptions": "Ambient RF density is sufficient in urban environments; rectenna design can achieve useful efficiency; broadband harvesting is feasible", "known_unknowns": "Regulatory compliance for RF harvesting; interference with existing communications; minimum viable RF density threshold", "safety_constraints": "No active transmission; must not interfere with licensed bands; INSERT-CELL isolation mandatory; SAR limits must be respected", "review_stage": "concept"},
    "kinetic-forge": {"design_intent": "Kinetic energy harvesting — converts mechanical motion into stored electrical energy", "assumptions": "Mechanical-to-electrical conversion via electromagnetic induction is mature; energy storage in supercapacitors is viable; motion sources are consistent enough", "known_unknowns": "Minimum viable motion amplitude for useful output; bearing wear rates at microscale; optimal flywheel mass-to-output ratio", "safety_constraints": "Rotating mass containment required; no exposed moving parts; INSERT-CELL isolation mandatory; emergency brake mechanism for flywheel", "review_stage": "simulation"},
    "solar-gem": {"design_intent": "Advanced solar energy collection — multi-spectrum array with concentrator optics", "assumptions": "Concentrator photovoltaics can be cost-effective at module scale; tracking systems can be simplified; thermal management is achievable passively", "known_unknowns": "Optimal concentration ratio for reliability vs efficiency; degradation of optical elements in outdoor environments; cost trajectory of III-V solar cells", "safety_constraints": "No focused beam hazard to eyes or skin; thermal runaway prevention; INSERT-CELL isolation mandatory; weatherproofing for all optical elements", "review_stage": "simulation"},
    "density-matrix": {"design_intent": "Matter density manipulation research — theoretical framework for material property control", "assumptions": "Density can be influenced through electromagnetic field interactions at molecular scale; computational models can predict material behavior changes", "known_unknowns": "Whether density manipulation is physically achievable beyond theory; energy requirements vs practical limits; reversibility of any modifications", "safety_constraints": "Simulation-only until physics verified; no claims of completed technology; must clearly label all work as theoretical; peer review required before any physical experimentation", "review_stage": "concept"},
    "element-synthesis": {"design_intent": "Controlled element transmutation research — theoretical study of atomic-level material synthesis", "assumptions": "Nuclear transmutation is well-documented in physics; controlled low-energy nuclear reactions may be possible; computational modeling can guide safe approaches", "known_unknowns": "Whether LENR is reproducible; energy balance of any transmutation process; radiation byproduct management; scalability beyond laboratory conditions", "safety_constraints": "Purely theoretical phase — no physical experiments without full safety review; radiation modeling mandatory; regulatory compliance required; triple containment design for any future physical work", "review_stage": "concept"},
    "ancestral-code": {"design_intent": "Ancestral genomic knowledge recovery — mapping beneficial traits from human evolutionary history", "assumptions": "Ancient DNA sequencing is reliable enough for trait identification; epigenetic markers can reveal dormant beneficial adaptations; computational genomics can reconstruct ancestral trait networks", "known_unknowns": "Which ancient variants are safely reactivatable; interaction effects between reactivated genes; ethical consensus on ancestral modification", "safety_constraints": "Read-only research — no gene editing without full ethics board review; all findings must be validated against multiple reference genomes; informed consent framework required before any human application", "review_stage": "concept"},
    "splice-sanctuary": {"design_intent": "Ethical framework for genetic splicing and modification — consent, oversight, and registry system", "assumptions": "Gene editing technology will continue advancing; ethical frameworks must anticipate future capabilities; public registry increases accountability", "known_unknowns": "How to handle cross-jurisdictional genetic regulations; long-term societal impact of widespread gene modification; consent models for modifications affecting offspring", "safety_constraints": "No modifications without documented reversibility plan; mandatory multi-party ethics review; public registry for all approved modifications; emergency shutdown protocols for any active gene therapy", "review_stage": "digital_proto"},
    "apex-protocol": {"design_intent": "Human enhancement framework — mapping safe, reversible biological improvements", "assumptions": "Some enhancements can be made reversible through controlled gene expression windows; myostatin modulation has documented effects; enhancement categories can be risk-stratified", "known_unknowns": "Long-term effects of controlled expression windows; individual variation in enhancement response; psychological effects of biological enhancement; societal equity implications", "safety_constraints": "Phase 1 is mapping only — no human testing; all enhancements must be theoretically reversible; risk stratification mandatory before any advancement; no permanent modifications without absolute certainty of safety", "review_stage": "concept"},
    "chimera-healing": {"design_intent": "Regenerative healing through cross-species gene activation — unlocking dormant repair pathways", "assumptions": "Developmental pathway genes like LIN28 can be safely reactivated in adult tissue; lipid nanoparticle delivery is targetable and controllable; regenerative capacity exists in dormant form in human genome", "known_unknowns": "Cancer risk from reactivated developmental pathways; tissue-specificity of nanoparticle delivery; duration and controllability of regenerative response; immune system interaction", "safety_constraints": "Simulation and computational modeling only until safety proven; no in-vivo testing without full review; mandatory cancer risk assessment for every pathway; fail-safe gene switches required in any delivery vector", "review_stage": "simulation"},
    "atomic-architect": {"design_intent": "Precision nano-fabrication at atomic level — constructing materials atom by atom", "assumptions": "Scanning probe microscopy can be extended to practical fabrication; quantum effects at atomic scale can be managed through precise control; computational prediction of atomic placement is feasible", "known_unknowns": "Speed vs precision tradeoff at scale; thermal stability of atom-by-atom constructions; error correction at atomic level; vacuum vs ambient operation feasibility", "safety_constraints": "Simulation-only until proven safe; no self-replicating designs; containment protocols for all experimental materials; dual-key authorization for any physical fabrication", "review_stage": "concept"},
    "bio-nanotech": {"design_intent": "Biological nanotechnology integration — bridging organic and synthetic systems at nanoscale", "assumptions": "Biological systems can interface with engineered nanostructures; biocompatibility can be achieved through biomimetic design; self-assembly principles from biology can guide nano-engineering", "known_unknowns": "Immune response to persistent nanostructures; long-term biocompatibility of novel materials; environmental fate of released nanoparticles; cross-kingdom genetic transfer risks", "safety_constraints": "No environmental release without full ecosystem impact study; biocontainment mandatory for all research; degradation pathway must be documented; no self-replicating nanostructures", "review_stage": "concept"},
    "grey-garden": {"design_intent": "Contaminated environment rehabilitation using engineered biological agents", "assumptions": "Extremophile organisms can be adapted for remediation; synthetic biology can enhance natural degradation pathways; contained release is possible for targeted cleanup", "known_unknowns": "Ecological impact of releasing engineered organisms; horizontal gene transfer risks; long-term population control of remediation agents; effectiveness across contamination types", "safety_constraints": "Kill-switch genes mandatory in all engineered organisms; contained field trials only with full environmental monitoring; no open release without regulatory approval; reversibility plan required", "review_stage": "concept"},
    "nano-medic": {"design_intent": "Medical nanobot swarm for targeted therapeutic delivery and micro-surgery", "assumptions": "Nanoscale robots can navigate biological environments; targeted drug delivery improves outcomes; swarm coordination is achievable through chemical signaling", "known_unknowns": "Clearance mechanisms for spent nanobots; immune evasion strategies; power source for sustained operation in vivo; precision of swarm coordination in turbulent blood flow", "safety_constraints": "Computational simulation only until safety proven; biodegradable materials mandatory; emergency recall mechanism required; no autonomous decision-making in treatment — all actions physician-directed", "review_stage": "simulation"},
}

def seed_from_static(db: Session):
    db.query(ResearchTracker).delete()
    db.query(ResearchActivityLog).delete()
    db.flush()

    for persona_key, profile in PERSONA_RESEARCH_PROFILES.items():
        for project in profile.projects:
            progress = PHASE_PROGRESS.get(project.phase, 0)
            last_bt = project.breakthroughs[-1] if project.breakthroughs else None

            sv_data = SUPERVISOR_SEED_DATA.get(project.id, {})
            tracker = ResearchTracker(
                persona=persona_key,
                project_id=project.id,
                project_name=project.name,
                codename=project.codename,
                current_phase=project.phase,
                progress_percent=progress,
                current_focus=project.current_focus,
                last_breakthrough=last_bt,
                is_active=True,
                design_intent=sv_data.get("design_intent"),
                assumptions=sv_data.get("assumptions"),
                known_unknowns=sv_data.get("known_unknowns"),
                safety_constraints=sv_data.get("safety_constraints"),
                review_stage=sv_data.get("review_stage", "concept"),
                supervisor_status="pending_review",
            )
            db.add(tracker)

            db.add(ResearchActivityLog(
                persona=persona_key,
                project_id=project.id,
                activity_type="daily_update",
                title=f"{project.name} initialized",
                description=f"Project {project.codename} seeded at phase: {project.phase} ({progress}% complete). Focus: {project.current_focus}",
            ))

            for bt in project.breakthroughs:
                db.add(ResearchActivityLog(
                    persona=persona_key,
                    project_id=project.id,
                    activity_type="breakthrough",
                    title=f"Breakthrough — {project.codename}",
                    description=bt,
                ))

    seed_resources(db)
    db.commit()


@router.get("/dashboard")
def research_dashboard(db: Session = Depends(get_db)):
    if db is None:
        return {"personas": {}, "error": "Database not available"}

    trackers = db.query(ResearchTracker).filter(ResearchTracker.is_active == True).all()

    if not trackers:
        seed_from_static(db)
        trackers = db.query(ResearchTracker).filter(ResearchTracker.is_active == True).all()

    resource_counts = {}
    counts = (
        db.query(ResearchResource.project_id, func.count(ResearchResource.id))
        .group_by(ResearchResource.project_id)
        .all()
    )
    for pid, cnt in counts:
        resource_counts[pid] = cnt

    log_counts = {}
    lcounts = (
        db.query(DailyResearchLog.project_id, DailyResearchLog.persona, func.count(DailyResearchLog.id))
        .group_by(DailyResearchLog.project_id, DailyResearchLog.persona)
        .all()
    )
    for pid, per, cnt in lcounts:
        log_counts[(pid, per)] = cnt

    personas = {}
    for t in trackers:
        if t.persona not in personas:
            profile = PERSONA_RESEARCH_PROFILES.get(t.persona)
            personas[t.persona] = {
                "persona": t.persona,
                "domain": profile.domain if profile else "",
                "projects": [],
            }
        personas[t.persona]["projects"].append({
            "project_id": t.project_id,
            "project_name": t.project_name,
            "codename": t.codename,
            "current_phase": t.current_phase,
            "progress_percent": t.progress_percent,
            "current_focus": t.current_focus,
            "last_breakthrough": t.last_breakthrough,
            "knowledge_tier": getattr(t, 'knowledge_tier', 'conceptual_sandbox') or 'conceptual_sandbox',
            "feasibility_tier": getattr(t, 'feasibility_tier', None),
            "validation_status": getattr(t, 'validation_status', 'not_validated'),
            "engineering_validation": getattr(t, 'engineering_validation', None),
            "last_validated_at": t.last_validated_at.isoformat() if getattr(t, 'last_validated_at', None) else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            "resource_count": resource_counts.get(t.project_id, 0),
            "daily_log_count": log_counts.get((t.project_id, t.persona), 0),
        })

    return {"personas": personas}


@router.get("/resources/{project_id}")
def get_project_resources(project_id: str, db: Session = Depends(get_db)):
    if db is None:
        return {"resources": [], "error": "Database not available"}

    resources = db.query(ResearchResource).filter(
        ResearchResource.project_id == project_id
    ).all()

    if not resources:
        if project_id in RESEARCH_RESOURCES:
            seed_resources(db)
            db.commit()
            resources = db.query(ResearchResource).filter(
                ResearchResource.project_id == project_id
            ).all()

    grouped = {}
    for r in resources:
        rtype = r.resource_type
        if rtype not in grouped:
            grouped[rtype] = []
        grouped[rtype].append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "url": r.url,
            "source": r.source,
            "year": r.year,
            "is_evidence_based": r.is_evidence_based,
        })

    return {"project_id": project_id, "resources": grouped}


@router.get("/resources")
def get_all_resources(db: Session = Depends(get_db)):
    if db is None:
        return {"projects": {}, "error": "Database not available"}

    resources = db.query(ResearchResource).all()

    if not resources:
        seed_resources(db)
        db.commit()
        resources = db.query(ResearchResource).all()

    projects = {}
    for r in resources:
        if r.project_id not in projects:
            projects[r.project_id] = {"persona": r.persona, "resources": {}}
        rtype = r.resource_type
        if rtype not in projects[r.project_id]["resources"]:
            projects[r.project_id]["resources"][rtype] = []
        projects[r.project_id]["resources"][rtype].append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "url": r.url,
            "source": r.source,
            "year": r.year,
            "is_evidence_based": r.is_evidence_based,
        })

    return {"projects": projects}


@router.get("/activity")
def all_activity(db: Session = Depends(get_db)):
    if db is None:
        return {"activities": [], "error": "Database not available"}

    logs = (
        db.query(ResearchActivityLog)
        .order_by(ResearchActivityLog.created_at.desc())
        .limit(30)
        .all()
    )

    return {"activities": [
        {
            "id": l.id,
            "persona": l.persona,
            "project_id": l.project_id,
            "activity_type": l.activity_type,
            "title": l.title,
            "description": l.description,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]}


@router.get("/{persona}/activity")
def persona_activity(persona: str, db: Session = Depends(get_db)):
    if db is None:
        return {"activities": [], "error": "Database not available"}

    logs = (
        db.query(ResearchActivityLog)
        .filter(ResearchActivityLog.persona == persona.lower())
        .order_by(ResearchActivityLog.created_at.desc())
        .limit(30)
        .all()
    )

    return {"activities": [
        {
            "id": l.id,
            "persona": l.persona,
            "project_id": l.project_id,
            "activity_type": l.activity_type,
            "title": l.title,
            "description": l.description,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]}


@router.get("/engineering-specs/{project_id}")
def get_engineering_specs(project_id: str):
    from atlas_core_new.research.engineering_specs_data import ENGINEERING_SPECS
    specs = ENGINEERING_SPECS.get(project_id)
    if not specs:
        return {"project_id": project_id, "specs": None}
    return {"project_id": project_id, "specs": specs}


@router.post("/seed")
def seed_research(db: Session = Depends(get_db)):
    if db is None:
        return {"status": "error", "message": "Database not available"}

    seed_from_static(db)
    count = db.query(ResearchTracker).count()
    log_count = db.query(ResearchActivityLog).count()
    resource_count = db.query(ResearchResource).count()
    return {"status": "ok", "trackers": count, "activity_logs": log_count, "resources": resource_count}


@router.post("/run-hypothesis-cycle")
def trigger_hypothesis_cycle(
    persona: Optional[str] = None,
    max_per_persona: int = 3,
    dry_run: bool = False,
    enable_web_research: bool = True,
):
    from atlas_core_new.research.daily_hypothesis_runner import run_hypothesis_cycle
    result = run_hypothesis_cycle(
        persona=persona,
        max_per_persona=max_per_persona,
        dry_run=dry_run,
        enable_web_research=enable_web_research,
    )
    return result


@router.post("/web-research/{project_id}")
def trigger_web_research(project_id: str, persona: Optional[str] = None, db: Session = Depends(get_db)):
    if db is None:
        return {"status": "error", "message": "Database not available"}
    from atlas_core_new.db.models import ResearchTracker
    from atlas_core_new.research.web_researcher import (
        research_for_project, build_research_context, save_research_sources
    )
    project = db.query(ResearchTracker).filter(
        ResearchTracker.project_id == project_id
    ).first()
    if not project:
        return {"status": "error", "message": f"Project {project_id} not found"}

    per = persona or project.persona
    domain_map = {"ajani": "robotics", "minerva": "genetics", "hermes": "nanotechnology"}
    domain = getattr(project, 'domain', None) or domain_map.get(per, "materials_science")

    research_data = research_for_project(
        project_name=project.project_name,
        domain=domain,
        hypothesis=project.design_intent or project.current_focus or project.project_name,
        current_focus=project.current_focus,
        deep_read_count=3,
        persona=per,
        include_creative=True,
    )

    saved = save_research_sources(db, project_id, per, research_data)
    context = build_research_context(research_data)

    return {
        "status": "ok",
        "project_id": project_id,
        "persona": per,
        "sources_found": research_data.get("sources_found", 0),
        "scientific_sources": research_data.get("scientific_sources", 0),
        "creative_sources": research_data.get("creative_sources", 0),
        "sources_saved": saved,
        "deep_reads": research_data.get("deep_read_count", 0),
        "queries_used": research_data.get("queries_used", []),
        "creative_queries_used": research_data.get("creative_queries_used", []),
        "sources": research_data.get("sources", [])[:15],
        "deep_read_excerpts": [{
            "title": dr["title"],
            "source": dr["source"],
            "excerpt_length": len(dr.get("content_excerpt", "")),
        } for dr in research_data.get("deep_reads", [])],
        "research_context_preview": context[:500],
    }


@router.get("/sources/{project_id}")
def get_research_sources(project_id: str, limit: int = 20, db: Session = Depends(get_db)):
    if db is None:
        return {"sources": []}
    from atlas_core_new.research.web_researcher import get_project_sources
    sources = get_project_sources(db, project_id, limit=limit)
    return {"status": "ok", "project_id": project_id, "total": len(sources), "sources": sources}


@router.post("/generate-build-plans")
def trigger_build_plan_generation(
    persona: Optional[str] = None,
    min_phase: str = "blueprint",
    max_plans: int = 5,
):
    from atlas_core_new.research.build_plan_generator import generate_build_plans_for_advanced_projects
    result = generate_build_plans_for_advanced_projects(
        persona=persona,
        min_phase=min_phase,
        max_plans=max_plans,
    )
    return result


@router.get("/daily-logs/{project_id}")
def get_daily_logs(project_id: str, persona: Optional[str] = None, limit: int = 10, db: Session = Depends(get_db)):
    if db is None:
        return {"logs": []}
    from atlas_core_new.db.models import DailyResearchLog
    query = db.query(DailyResearchLog).filter(DailyResearchLog.project_id == project_id)
    if persona:
        query = query.filter(DailyResearchLog.persona == persona)
    logs = query.order_by(DailyResearchLog.research_date.desc()).limit(limit).all()
    return {"logs": [{
        "id": l.id,
        "persona": l.persona,
        "focus_area": l.focus_area,
        "findings": l.findings,
        "next_steps": l.next_steps,
        "design_iterations": l.design_iterations,
        "phase_before": l.phase_before,
        "phase_after": l.phase_after,
        "progress_delta": l.progress_delta,
        "guardrail_flags": l.guardrail_flags,
        "date": l.research_date.isoformat() if l.research_date else None,
    } for l in logs]}


@router.get("/persona-schedule")
def get_persona_schedule():
    now = datetime.now()
    hour = now.hour

    if 1 <= hour < 6:
        mode = "deep_work"
        label = "Deep Work"
        desc = "Personas are in deep research mode — running hypotheses, building designs, and pushing projects forward."
        icon = "brain"
        next_shift = "Rest Break at 1:00 PM"
    elif 6 <= hour < 13:
        mode = "active_work"
        label = "Active Work"
        desc = "Personas are actively working — responding to queries, developing projects, and collaborating."
        icon = "hammer"
        next_shift = "Rest Break at 1:00 PM"
    elif 13 <= hour < 18:
        mode = "rest_break"
        label = "Rest Break"
        desc = "Personas are resting and recharging. Systems are in low-power mode. Non-urgent tasks queued for later."
        icon = "moon"
        next_shift = "Web Research at 6:00 PM"
    elif 18 <= hour < 24:
        mode = "web_research"
        label = "Web Research"
        desc = "Personas are browsing research papers, patents, and technical references — gathering new ideas for their projects."
        icon = "search"
        next_shift = "Deep Work at 1:00 AM"
    else:
        mode = "deep_work"
        label = "Deep Work"
        desc = "Personas are in deep research mode."
        icon = "brain"
        next_shift = "Rest Break at 1:00 PM"

    schedule_blocks = [
        {"start": "1:00 AM", "end": "6:00 AM", "mode": "deep_work", "label": "Deep Work", "icon": "brain"},
        {"start": "6:00 AM", "end": "1:00 PM", "mode": "active_work", "label": "Active Work", "icon": "hammer"},
        {"start": "1:00 PM", "end": "6:00 PM", "mode": "rest_break", "label": "Rest Break", "icon": "moon"},
        {"start": "6:00 PM", "end": "12:00 AM", "mode": "web_research", "label": "Web Research", "icon": "search"},
    ]

    return {
        "current_mode": mode,
        "label": label,
        "description": desc,
        "icon": icon,
        "next_shift": next_shift,
        "current_hour": hour,
        "schedule": schedule_blocks,
    }


@router.get("/blueprint-handbooks")
def list_blueprint_handbooks():
    from atlas_core_new.research.blueprint_handbook import get_available_handbooks
    return {"status": "ok", "handbooks": get_available_handbooks()}


@router.get("/blueprint-handbook/{project_id}")
def get_blueprint_handbook(project_id: str):
    from atlas_core_new.research.blueprint_handbook import get_handbook
    handbook = get_handbook(project_id)
    if not handbook:
        return {"status": "not_found", "project_id": project_id, "handbook": None}
    return {"status": "ok", "project_id": project_id, "handbook": handbook}
