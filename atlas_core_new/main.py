"""
atlas_core/main.py

FastAPI entry point.
"""

import os
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, StreamingResponse
from .utils.error_handling import register_error_handlers, AtlasError, not_found, bad_request, service_unavailable, ai_not_configured, sanitize_error
from .utils.rate_limiter import rate_limit_ai, rate_limit_strict
from typing import Optional
from pydantic import BaseModel

from .core.agent.agent_state import AgentLoop, AgentState
from .core.agent.toolbelt import Toolbelt
from .core.memory.memory_store import SimpleMemoryStore
from .core.memory.persistent_store import PersistentMemoryStore
from .core.brain.persona_kernel import PersonaKernel
from .core.brain.response_pipeline import ResponsePipeline
from .core.personas.registry import PersonaRegistry
from .core.agent.persona_runners import AjaniRunner, MinervaRunner, HermesRunner
from .generator.multimodal_router import MultimodalRouter
from .generator.image_pipeline import ImagePipeline
from .core.update_engine.updater import Updater
from .bots import profiles as bot_profiles
from .pipeline.validator import validate_pipeline
from .pipeline.bot_files import ensure_bot_files, load_spec, append_history, update_spec
from .identity import get_identity, get_principles, safety_check
from .research.research_docs import (
    get_research_document, get_all_documents_for_persona, get_test_ready_projects,
    get_projects_by_phase, format_document_summary, format_document_full, ProjectPhase
)
import os
from .forge import (
    SafetyKernel, RefusalEngine, HumanGate, CauldronLiteFactory,
    AjaniStrategist, MinervaEthics, HermesFabrication,
    HEPHAESTUS_CROSSED_THE_LINE,
)
from .forge.templates import (
    blueprint_ant_cleaner, blueprint_crab_water_sampler, blueprint_octopus_pipe_repair,
)
from .forge.parts_library import STANDARD_PARTS, JOINT_FAMILIES, ORGAN_PACKS
from .curriculum import get_all_fields, get_field_lessons, get_lesson, get_next_lesson, ALL_CURRICULA
from .projects.registry import project_registry
from .knowledge import (
    KNOWLEDGE_PHILOSOPHY, KNOWLEDGE_SOURCES, KNOWLEDGE_BOUNDARIES,
    get_sources_for_persona, knowledge_pack_registry, get_context_from_packs
)
from .specs import (
    CORE_ARCHITECTURE, TRI_CORE_COUNCIL,
    COGNITIVE_CAPABILITIES, LEARNING_INTELLIGENCE,
    TEACHING_SYSTEM, ASSESSMENT_SYSTEM,
    AUTONOMY_SPECS, SYSTEM_BOUNDARIES,
    PERSONALITY_SPECS, BEHAVIORAL_TRAITS,
    MULTIMODAL_CAPABILITIES, HARDWARE_AWARENESS,
    SECURITY_SPECS, ETHICS_LAYER,
    KNOWLEDGE_SPECTRUM, EVOLUTION_SPECS
)
from .db import (
    init_db, SessionLocal, UserProgress, LessonProgress, KnowledgePack,
    PersonalProject, ProjectStep
)
from .research.persona_research import (
    get_persona_research, get_research_summary, get_project_details
)
from .research.equipment_forge import (
    get_all_equipment, get_persona_equipment, get_equipment_details,
    get_equipment_by_status, get_ready_to_build
)
from .research.simulation_data import (
    get_all_projects_summary, get_project_theoretical_data,
    get_project_models, get_model_detail, SYSTEM_DISCLAIMER
)
from sqlalchemy.orm import Session
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from umojaforge.simulator_api import router as simulator_router
from umojaforge.spcm_api import router as spcm_router
from atlas_core_new.core.agents.api import router as agents_router
from atlas_core_new.core.runtime.hermes_router_api import router as hermes_api_router
from doctrine.api import router as doctrine_router
from doctrine.chameleon_api import router as chameleon_router
from uws_workshop.uws.api import router as uws_router
from pre_reality_engine.api import router as pre_reality_router
from atlas_core_new.research.research_tracker_api import router as research_tracker_router
from atlas_core_new.engineering.api import router as engineering_router
from atlas_core_new.research.supervisor_api import router as supervisor_router
from atlas_core_new.research.build_api import router as build_router
from atlas_core_new.tools.figma_api import router as figma_router
from atlas_core_new.research.hephaestus_api import router as hephaestus_router
from atlas_core_new.hermes_reality.api.reality_routes import router as reality_router
from atlas_core_new.design_engine.api import router as design_engine_router
from atlas_core_new.blueprint_engine.api import router as blueprint_engine_router
from atlas_core_new.blueprint_engine.storage import router as atlas_storage_router

app = FastAPI(title="Atlas Core", version="0.3.3")
register_error_handlers(app)

app.include_router(simulator_router)
app.include_router(spcm_router)
app.include_router(agents_router)
app.include_router(hermes_api_router)
app.include_router(doctrine_router)
app.include_router(chameleon_router)
app.include_router(uws_router)
app.include_router(pre_reality_router)
app.include_router(research_tracker_router)
app.include_router(engineering_router)
app.include_router(supervisor_router)
app.include_router(build_router)
app.include_router(figma_router)
app.include_router(hephaestus_router)
app.include_router(reality_router)
app.include_router(design_engine_router)
app.include_router(blueprint_engine_router)
app.include_router(atlas_storage_router)

def get_db():
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
VIEWER_DIR = STATIC_DIR / "viewer"
app.mount("/viewer/assets", StaticFiles(directory=str(VIEWER_DIR)), name="viewer_assets")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

simple_memory = SimpleMemoryStore()
persistent_memory = PersistentMemoryStore(db_session_factory=SessionLocal)
registry = PersonaRegistry()
kernel = PersonaKernel(registry=registry)
pipeline = ResponsePipeline(kernel=kernel, memory=simple_memory)
toolbelt = Toolbelt()
router = MultimodalRouter()
image_pipe = ImagePipeline()

agent_loop = AgentLoop(
    state=AgentState(),
    runners={
        "ajani": AjaniRunner(pipeline=pipeline),
        "minerva": MinervaRunner(pipeline=pipeline),
        "hermes": HermesRunner(pipeline=pipeline),
    },
)

updater = Updater(
    current_version=os.getenv("ATLAS_VERSION", "0.3.1"),
    update_url=os.getenv("ATLAS_UPDATE_URL", ""),
    public_key_pem=os.getenv("ATLAS_UPDATE_PUBKEY", ""),
)


class GenerateRequest(BaseModel):
    persona: str = "ajani"
    text: str
    style: str | None = None
    mode: str = "teach"
    use_tools: bool = True



# Route modules
from .routes.chat import router as chat_router
from .routes.design import router as design_router
from .routes.conversations import router as conversations_router
from .routes.tts import router as tts_router
from .routes.user_data import router as user_data_router
from .routes.lesson_plans import router as lesson_plans_router
from .routes.ai_routing import router as ai_routing_router

@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-cache"})


@app.get("/viewer/{name}")
def serve_viewer(name: str):
    viewer_path = STATIC_DIR / "viewer" / f"{name}.html"
    if not viewer_path.exists():
        return not_found(f"Viewer '{name}' not found")
    return FileResponse(viewer_path, headers={"Cache-Control": "no-cache"})


@app.get("/download-project")
def download_project():
    """Download the entire Atlas Core project as a zip file."""
    zip_path = Path(__file__).parent.parent / "atlas-core-project.zip"
    if not zip_path.exists():
        return {"error": "Project zip not found"}
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="atlas-core-project.zip",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/sw.js")
def service_worker():
    """Serve service worker from root with proper scope header."""
    return FileResponse(
        STATIC_DIR / "sw.js",
        media_type="application/javascript",
        headers={
            "Cache-Control": "no-cache",
            "Service-Worker-Allowed": "/"
        }
    )


@app.get("/api")
def api_info():
    identity = get_identity()
    return {
        "name": "Atlas Core",
        "codename": identity.codename,
        "version": identity.version,
        "fingerprint": identity.fingerprint,
        "personas": ["ajani", "minerva", "hermes"],
        "modes": ["chat", "counsel"],
        "endpoints": {
            "core": ["/health", "/identity", "/generate", "/chat", "/counsel"],
            "ai": ["/suggest", "/validate"],
            "bots": ["/bots", "/pipeline/validate", "/pipeline/init/{name}"],
            "forge": ["/forge/audit", "/forge/templates", "/forge/build/{template}"],
        },
    }


@app.get("/health")
def health():
    return {"ok": True, "version": updater.current_version}


@app.get("/research")
def list_all_research():
    """Get research profiles for all personas"""
    return {
        persona: get_research_summary(persona)
        for persona in ["ajani", "minerva", "hermes"]
    }


@app.get("/research/docs")
def list_all_research_docs():
    """Get summaries of all research documentation across all personas"""
    all_docs = []
    for persona in ["ajani", "minerva", "hermes"]:
        docs = get_all_documents_for_persona(persona)
        for doc in docs:
            all_docs.append(format_document_summary(doc))
    return {"documents": all_docs, "total": len(all_docs)}


@app.get("/research/docs/test-ready")
def get_test_ready():
    """Get all projects that are ready for testing"""
    ready = get_test_ready_projects()
    return {"test_ready_projects": ready, "count": len(ready)}


@app.get("/research/docs/by-phase/{phase}")
def get_docs_by_phase(phase: str):
    """Get all projects in a specific phase"""
    try:
        phase_enum = ProjectPhase(phase.lower())
    except ValueError:
        valid = [p.value for p in ProjectPhase]
        return {"error": f"Invalid phase '{phase}'", "valid_phases": valid}
    
    projects = get_projects_by_phase(phase_enum)
    return {"phase": phase, "projects": projects, "count": len(projects)}


@app.get("/research/{persona}")
def get_persona_research_profile(persona: str):
    """Get detailed research profile for a specific persona"""
    profile = get_persona_research(persona.lower())
    if not profile:
        return {"error": f"Unknown persona: {persona}", "available": ["ajani", "minerva", "hermes"]}
    
    return {
        "persona": profile.persona,
        "domain": profile.domain,
        "subdomain": profile.subdomain,
        "philosophy": {
            "core_belief": profile.philosophy.core_belief,
            "approach": profile.philosophy.approach,
            "ethical_stance": profile.philosophy.ethical_stance,
            "humanity_vision": profile.philosophy.humanity_vision,
        },
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "codename": p.codename,
                "description": p.description,
                "phase": p.phase,
                "humanity_goal": p.humanity_goal,
                "key_concepts": p.key_concepts,
                "current_focus": p.current_focus,
                "breakthroughs": p.breakthroughs,
                "applications": p.applications,
            }
            for p in profile.projects
        ],
        "specialties": profile.specialties,
        "influences": profile.influences,
        "favorite_elements": profile.favorite_elements,
    }


@app.get("/research/{persona}/project/{project_id}")
def get_research_project(persona: str, project_id: str):
    """Get details of a specific research project"""
    details = get_project_details(persona.lower(), project_id)
    if not details:
        return {"error": f"Project '{project_id}' not found for persona '{persona}'"}
    return details


@app.get("/research/docs/{persona}")
def get_persona_docs(persona: str):
    """Get all research documentation for a persona"""
    docs = get_all_documents_for_persona(persona.lower())
    if not docs:
        return {"error": f"No documents for persona '{persona}'", "available": ["ajani", "minerva", "hermes"]}
    return {
        "persona": persona,
        "documents": [format_document_summary(d) for d in docs],
        "count": len(docs),
    }


@app.get("/research/docs/{persona}/{project_id}")
def get_full_research_doc(persona: str, project_id: str):
    """Get full research documentation with steps, blueprints, simulations, and build phases"""
    doc = get_research_document(persona.lower(), project_id)
    if not doc:
        return {"error": f"Document '{project_id}' not found for persona '{persona}'"}
    return format_document_full(doc)


@app.get("/research/docs/{persona}/{project_id}/steps")
def get_project_steps(persona: str, project_id: str):
    """Get just the steps for a project"""
    doc = get_research_document(persona.lower(), project_id)
    if not doc:
        return {"error": f"Document '{project_id}' not found"}
    return {
        "project": doc.project_name,
        "steps": [
            {"number": s.number, "title": s.title, "description": s.description, "status": s.status, "notes": s.notes}
            for s in doc.steps
        ],
        "progress": f"{sum(1 for s in doc.steps if s.status == 'complete')}/{len(doc.steps)} complete",
    }


@app.get("/research/docs/{persona}/{project_id}/blueprints")
def get_project_blueprints(persona: str, project_id: str):
    """Get blueprints for a project"""
    doc = get_research_document(persona.lower(), project_id)
    if not doc:
        return {"error": f"Document '{project_id}' not found"}
    return {
        "project": doc.project_name,
        "blueprints": [
            {
                "id": b.id,
                "name": b.name,
                "version": b.version,
                "description": b.description,
                "specifications": b.specifications,
                "materials": b.materials,
                "diagrams": b.diagrams,
                "safety_notes": b.safety_notes,
            }
            for b in doc.blueprints
        ],
        "count": len(doc.blueprints),
    }


@app.get("/research/docs/{persona}/{project_id}/simulations")
def get_project_simulations(persona: str, project_id: str):
    """Get simulations for a project"""
    doc = get_research_document(persona.lower(), project_id)
    if not doc:
        return {"error": f"Document '{project_id}' not found"}
    return {
        "project": doc.project_name,
        "simulations": [
            {
                "id": sim.id,
                "name": sim.name,
                "description": sim.description,
                "inputs": sim.inputs,
                "expected_outputs": sim.expected_outputs,
                "success_criteria": sim.success_criteria,
                "risk_factors": sim.risk_factors,
                "results": sim.results,
                "status": sim.status,
            }
            for sim in doc.simulations
        ],
        "passed": sum(1 for s in doc.simulations if s.status == "passed"),
        "running": sum(1 for s in doc.simulations if s.status == "running"),
        "pending": sum(1 for s in doc.simulations if s.status == "pending"),
    }


@app.get("/research/docs/{persona}/{project_id}/build")
def get_project_build(persona: str, project_id: str):
    """Get physical build status for a project"""
    doc = get_research_document(persona.lower(), project_id)
    if not doc:
        return {"error": f"Document '{project_id}' not found"}
    if not doc.physical_build:
        return {"project": doc.project_name, "physical_build": None, "message": "No physical build phase yet"}
    
    pb = doc.physical_build
    return {
        "project": doc.project_name,
        "build_phase": pb.phase.value,
        "started": pb.started_date,
        "target_completion": pb.target_completion,
        "components": {
            "needed": pb.components_needed,
            "acquired": pb.components_acquired,
            "pending": [c for c in pb.components_needed if c not in pb.components_acquired],
        },
        "assembly_progress": f"{sum(1 for s in pb.assembly_steps if s.status == 'complete')}/{len(pb.assembly_steps)} steps complete",
        "assembly_steps": [{"number": s.number, "title": s.title, "status": s.status} for s in pb.assembly_steps],
        "quality_checks": pb.quality_checks,
        "blockers": pb.blockers,
        "ready_for_testing": pb.ready_for_testing,
        "test_requirements": pb.test_requirements,
    }


@app.get("/research/docs/{persona}/{project_id}/journal")
def get_project_journal(persona: str, project_id: str):
    """Get journal entries for a project"""
    doc = get_research_document(persona.lower(), project_id)
    if not doc:
        return {"error": f"Document '{project_id}' not found"}
    return {
        "project": doc.project_name,
        "persona": persona,
        "journal_entries": doc.journal_entries,
        "entry_count": len(doc.journal_entries),
    }


@app.get("/equipment")
async def list_all_equipment():
    """Get all functional equipment from all personas"""
    return get_all_equipment()


@app.get("/equipment/ready-to-build")
async def list_ready_equipment():
    """Get all equipment ready to build"""
    return {"ready_to_build": get_ready_to_build()}


@app.get("/equipment/by-status/{status}")
async def list_equipment_by_status(status: str):
    """Get equipment by status (concept, designing, spec_complete, parts_listed, ready_to_build, building, testing, functional)"""
    return {"status": status, "equipment": get_equipment_by_status(status)}


@app.get("/equipment/{persona}")
async def list_persona_equipment(persona: str):
    """Get all equipment for a specific persona"""
    equipment = get_persona_equipment(persona.lower())
    if not equipment:
        return {"error": f"No equipment found for persona: {persona}"}
    return {"persona": persona, "equipment": equipment}


@app.get("/equipment/{persona}/{equipment_id}")
async def get_equipment_full_details(persona: str, equipment_id: str):
    """Get full build details for specific equipment"""
    details = get_equipment_details(persona.lower(), equipment_id)
    if not details:
        return {"error": f"Equipment not found: {equipment_id}"}
    return details


@app.get("/theoretical")
async def list_all_theoretical_projects():
    """
    Get summary of all theoretical knowledge synthesis projects.
    
    SYSTEM DISCLAIMER: All AI-generated research is non-empirical, non-operational,
    and intended for conceptual exploration only.
    """
    return {
        "disclaimer": SYSTEM_DISCLAIMER,
        "projects": get_all_projects_summary()
    }


@app.get("/theoretical/{persona}/{project_id}")
async def get_theoretical_project(persona: str, project_id: str):
    """
    Get complete theoretical framework for a project.
    
    Returns knowledge domains, theoretical models, confidence levels,
    and hard rules - NOT experiments or procedures.
    """
    project = get_project_theoretical_data(persona.lower(), project_id)
    if not project:
        return {"error": f"No theoretical data found for {persona}/{project_id}"}
    
    domains = [{
        "domain_name": d.domain_name,
        "key_papers": d.key_papers,
        "core_principles": d.core_principles,
        "known_constraints": d.known_constraints,
        "ethical_boundaries": d.ethical_boundaries,
    } for d in project.knowledge_domains]
    
    models = get_project_models(persona.lower(), project_id)
    
    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "persona": project.persona,
        "overall_confidence": f"{project.overall_confidence:.0%}",
        "confidence_conditional_on": project.confidence_conditional_on,
        "knowledge_domains": domains,
        "theoretical_models": models,
        "hard_rules": project.hard_rules,
        "ethical_review_status": project.ethical_review_status,
        "last_updated": project.last_updated,
        "system_disclaimer": project.system_disclaimer,
    }


@app.get("/theoretical/{persona}/{project_id}/models")
async def get_theoretical_models(persona: str, project_id: str):
    """
    Get all theoretical models for a project.
    
    Each model includes hypothesis, confidence levels, assumptions,
    and breakthroughs - categorized as Conceptual, Theoretical, Ethical, or Safety.
    """
    models = get_project_models(persona.lower(), project_id)
    if not models:
        return {"error": f"No theoretical models found for {persona}/{project_id}"}
    
    return {
        "persona": persona,
        "project_id": project_id,
        "models": models,
        "total": len(models),
        "disclaimer": "These are theoretical models based on published knowledge. Results represent probabilistic simulations, not empirical data.",
    }


@app.get("/theoretical/{persona}/{project_id}/models/{model_id}")
async def get_theoretical_model_detail(persona: str, project_id: str, model_id: str):
    """
    Get full details for a specific theoretical model.
    
    Includes:
    - Hypothesis and theoretical basis
    - Knowledge sources (published literature)
    - Assumptions with confidence levels and falsifiability
    - Breakthroughs (Conceptual, Theoretical, Ethical, Safety)
    - Architect Review Gate status
    - What we don't know
    
    NEVER includes: experiments, pass/fail rates, materials lists, procedures
    """
    detail = get_model_detail(persona.lower(), project_id, model_id)
    if not detail:
        return {"error": f"Theoretical model not found: {model_id}"}
    return detail



# ==================== TOOLS ====================

from .core.agent.tools import tool_registry

class ToolExecuteRequest(BaseModel):
    tool: str
    params: dict

@app.get("/tools")
def list_tools():
    """List available tools for the AI personas."""
    return {"tools": tool_registry.list_tools()}

@app.post("/tools/execute")
def execute_tool(req: ToolExecuteRequest):
    """Execute a tool with given parameters."""
    result = tool_registry.execute(req.tool, req.params)
    return {
        "tool": req.tool,
        "success": result.success,
        "result": result.result,
        "error": result.error
    }

@app.post("/tools/calculate")
def calculate(expression: str):
    """Quick calculator endpoint."""
    result = tool_registry.execute("calculate", {"expression": expression})
    return {"expression": expression, "result": result.result, "error": result.error}

class CodeRequest(BaseModel):
    code: str

@app.post("/tools/run-code")
def run_code(req: CodeRequest):
    """Execute Python code safely."""
    result = tool_registry.execute("run_code", {"code": req.code})
    return {"success": result.success, "output": result.result, "error": result.error}



@app.post("/generate")
def generate(req: GenerateRequest):
    route = router.route(text=req.text, has_image=False)
    if route != "text":
        return {"error": f"Unsupported route: {route}"}

    result = agent_loop.step(
        persona=req.persona,
        user_text=req.text,
        style=req.style,
        mode=req.mode,
        use_tools=req.use_tools,
    )
    return result


@app.post("/generate-with-image")
async def generate_with_image(
    persona: str = "ajani",
    text: str = "",
    style: str | None = None,
    mode: str = "build",
    image: UploadFile = File(...),
):
    img_bytes = await image.read()
    route = router.route(text=text, has_image=True)

    if route == "image_to_text":
        result = agent_loop.step(
            persona=persona,
            user_text=f"{text}\n\n[IMAGE_ATTACHED: describe + interpret what I mean]",
            style=style,
            mode=mode,
            use_tools=True,
            image_bytes=img_bytes,
        )
        return result

    if route == "image_gen":
        plan = agent_loop.step(
            persona=persona,
            user_text=f"{text}\n\nTurn this into a perfect image prompt in style={style}",
            style=style,
            mode=mode,
            use_tools=False,
        )
        prompt = plan.get("text", "")
        img = image_pipe.generate(prompt=prompt, style=style)
        return {"prompt": prompt, "image_base64": img}

    return {"error": f"Unsupported route: {route}"}


@app.post("/update/check")
def update_check():
    return updater.check()


@app.post("/update/apply")
def update_apply():
    return updater.apply()


@app.get("/bots")
def list_bots():
    return {
        "profiles": bot_profiles.list_profiles(),
        "domains": [d.value for d in bot_profiles.Domain],
        "classes": [c.value for c in bot_profiles.BotClass],
    }


@app.get("/bots/{name}")
def get_bot(name: str):
    profile = bot_profiles.get_profile(name)
    if not profile:
        return {"error": f"Bot profile '{name}' not found"}
    return {
        "name": name,
        "domain": profile.domain.value,
        "class": profile.bot_class.value,
        "sensors": profile.default_sensors,
        "allowed_actions": list(profile.allowed_actions),
        "requires_approval_for": list(profile.requires_human_approval_for),
    }


@app.get("/bots/{name}/check-action/{action}")
def check_bot_action(name: str, action: str):
    profile = bot_profiles.get_profile(name)
    if not profile:
        return {"error": f"Bot profile '{name}' not found"}
    return {
        "name": name,
        "action": action,
        "allowed": bot_profiles.is_action_allowed(name, action),
        "requires_approval": bot_profiles.requires_approval(name, action),
    }


class PipelineValidateRequest(BaseModel):
    stage: str
    bot_type: str | None = None
    action: str | None = None
    blueprint_exists: bool = False
    human_approved: bool = False
    approved: bool = False


@app.post("/pipeline/validate")
def pipeline_validate(req: PipelineValidateRequest):
    try:
        validate_pipeline(
            stage=req.stage,
            data={
                "bot_type": req.bot_type,
                "action": req.action,
                "blueprint_exists": req.blueprint_exists,
                "human_approved": req.human_approved,
                "approved": req.approved,
            },
        )
        return {"valid": True, "stage": req.stage}
    except (ValueError, PermissionError) as e:
        return {"valid": False, "error": sanitize_error(e)}


@app.post("/pipeline/init/{bot_name}")
def pipeline_init(bot_name: str):
    try:
        ensure_bot_files(bot_name)
        spec = load_spec(bot_name)
        return {"ok": True, "bot": bot_name, "spec": spec}
    except ValueError as e:
        return {"ok": False, "error": sanitize_error(e)}


@app.get("/pipeline/spec/{bot_name}")
def pipeline_spec(bot_name: str):
    spec = load_spec(bot_name)
    if not spec:
        return {"error": f"No spec found for {bot_name}"}
    return spec


class SpecUpdateRequest(BaseModel):
    mission: str | None = None
    environment: str | None = None


@app.post("/pipeline/spec/{bot_name}")
def pipeline_spec_update(bot_name: str, req: SpecUpdateRequest):
    spec = load_spec(bot_name)
    if not spec:
        return {"error": f"No spec found for {bot_name}"}
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if updates:
        spec = update_spec(bot_name, updates)
        append_history(bot_name, f"[UPDATE] {list(updates.keys())}")
    return {"ok": True, "spec": spec}


@app.get("/identity")
def get_system_identity():
    identity = get_identity()
    return {
        "codename": identity.codename,
        "version": identity.version,
        "genesis_date": identity.genesis_date,
        "fingerprint": identity.fingerprint,
        "principles": list(get_principles()),
    }


@app.post("/identity/safety-check")
def identity_safety_check(text: str):
    return safety_check(text)


@app.get("/forge/audit")
def forge_audit():
    return {
        "hephaestus_crossed_the_line": HEPHAESTUS_CROSSED_THE_LINE,
        "message": "These are the lines Atlas Core will never cross.",
    }


@app.get("/forge/templates")
def forge_templates():
    from .forge.templates import (
        blueprint_butterfly_pollinator, blueprint_earthworm_aerator,
        blueprint_hummingbird_inspector, blueprint_turtle_transporter
    )
    templates = [
        blueprint_ant_cleaner(),
        blueprint_crab_water_sampler(),
        blueprint_octopus_pipe_repair(),
        blueprint_butterfly_pollinator(),
        blueprint_earthworm_aerator(),
        blueprint_hummingbird_inspector(),
        blueprint_turtle_transporter(),
    ]
    return {
        "templates": [
            {
                "name": t.name,
                "task": t.task_type.name,
                "biomimic": t.biomimic,
                "payload_kg": t.payload_kg,
                "energy_storage_j": t.energy_storage_j,
                "can_pursue": t.can_pursue_targets,
                "geometry": t.geometry_notes,
            }
            for t in templates
        ]
    }


forge_safety = SafetyKernel()
forge_reviewers = (AjaniStrategist(), MinervaEthics(), HermesFabrication())
forge_refusal = RefusalEngine(safety=forge_safety, reviewers=forge_reviewers, human_gate=HumanGate())
forge_factory = CauldronLiteFactory(safety=forge_safety, refusal=forge_refusal)


@app.post("/forge/build/{template_name}")
def forge_build(template_name: str, uncertainty: float = 0.25):
    from .forge.templates import (
        blueprint_butterfly_pollinator, blueprint_earthworm_aerator,
        blueprint_hummingbird_inspector, blueprint_turtle_transporter
    )
    templates = {
        "ant": blueprint_ant_cleaner,
        "crab": blueprint_crab_water_sampler,
        "octopus": blueprint_octopus_pipe_repair,
        "butterfly": blueprint_butterfly_pollinator,
        "earthworm": blueprint_earthworm_aerator,
        "hummingbird": blueprint_hummingbird_inspector,
        "turtle": blueprint_turtle_transporter,
    }
    if template_name not in templates:
        return {"error": f"Unknown template: {template_name}", "available": list(templates.keys())}
    bp = templates[template_name]()
    result = forge_factory.build(bp, uncertainty=uncertainty)
    return {"result": result, "blueprint": bp.name}


@app.get("/forge/parts")
def list_forge_parts():
    return {
        "parts": [
            {"name": k, "sample": fn().summary()}
            for k, fn in STANDARD_PARTS.items()
        ],
        "joints": [
            {"family": k, "sample": fn().summary()}
            for k, fn in JOINT_FAMILIES.items()
        ],
        "organs": list(ORGAN_PACKS.keys()),
    }


@app.get("/forge/parts/{part_name}")
def get_forge_part(part_name: str):
    if part_name in STANDARD_PARTS:
        p = STANDARD_PARTS[part_name]()
        return {"type": "part", "data": p.summary(), "description": p.description, "notes": p.notes}
    if part_name in JOINT_FAMILIES:
        j = JOINT_FAMILIES[part_name]()
        return {"type": "joint", "data": j.summary(), "description": j.description}
    if part_name in ORGAN_PACKS:
        o = ORGAN_PACKS[part_name]()
        return {"type": "organ", "data": o.summary(), "description": o.description, "notes": o.notes}
    return {"error": f"Unknown part: {part_name}", "available": list(STANDARD_PARTS.keys()) + list(JOINT_FAMILIES.keys()) + list(ORGAN_PACKS.keys())}


# ============ LESSON SYSTEM ============

from .routes._shared import user_lesson_progress

class StartLessonRequest(BaseModel):
    persona: str
    field: str
    lesson_id: str | None = None
    user_id: str = "default"

class LessonProgressRequest(BaseModel):
    user_id: str = "default"
    persona: str | None = None

@app.get("/lessons/progress/{user_id}")
def get_user_progress(user_id: str):
    """Get current lesson progress for a user"""
    progress = user_lesson_progress.get(user_id)
    if not progress:
        return {"status": "no_active_lesson", "message": "No lesson in progress. Use /lessons/{persona}/fields to see available subjects."}
    return {"status": "in_progress", "progress": progress}

@app.get("/lessons/resume/{user_id}")
def resume_lesson(user_id: str):
    """Get info to resume where user left off"""
    progress = user_lesson_progress.get(user_id)
    if not progress:
        return {"status": "no_active_lesson", "suggestion": "Start a new lesson with /lessons/start"}
    
    lesson = get_lesson(progress["persona"], progress["field"], progress["lesson_id"])
    return {
        "status": "ready_to_resume",
        "progress": progress,
        "lesson": lesson,
        "prompt": f"Ready to continue {progress['lesson_title']} with {progress['persona'].title()}?"
    }

@app.get("/lessons/{persona}/fields")
def get_persona_fields(persona: str):
    """Get all available fields for a persona"""
    fields = get_all_fields(persona)
    if not fields:
        return {"error": f"Unknown persona: {persona}", "available": ["ajani", "minerva", "hermes"]}
    return {"persona": persona, "fields": fields}

@app.get("/lessons/{persona}/{field}")
def get_field_curriculum(persona: str, field: str):
    """Get all lessons in a field"""
    field_data = get_field_lessons(persona, field)
    if not field_data:
        available = get_all_fields(persona)
        return {"error": f"Unknown field: {field}", "available": [f["id"] for f in available]}
    return {"persona": persona, "field": field, "curriculum": field_data}

@app.post("/lessons/start")
def start_lesson(req: StartLessonRequest):
    """Start or resume a lesson"""
    persona = req.persona.lower()
    field = req.field.lower()
    
    field_data = get_field_lessons(persona, field)
    if not field_data:
        return {"error": f"Unknown field: {field} for {persona}"}
    
    if req.lesson_id:
        lesson = get_lesson(persona, field, req.lesson_id)
    else:
        lessons = field_data.get("levels", {}).get("beginner", [])
        lesson = {**lessons[0], "level": "beginner", "field": field} if lessons else None
    
    if not lesson:
        return {"error": "Could not find lesson"}
    
    user_lesson_progress[req.user_id] = {
        "persona": persona,
        "field": field,
        "lesson_id": lesson["id"],
        "lesson_title": lesson["title"],
        "level": lesson["level"]
    }
    
    return {
        "status": "started",
        "lesson": lesson,
        "message": f"Starting lesson: {lesson['title']}"
    }

@app.post("/lessons/complete")
def complete_lesson(req: StartLessonRequest):
    """Mark lesson complete and get next"""
    persona = req.persona.lower()
    field = req.field.lower()
    
    next_lesson = get_next_lesson(persona, field, req.lesson_id or "")
    
    if next_lesson:
        user_lesson_progress[req.user_id] = {
            "persona": persona,
            "field": field,
            "lesson_id": next_lesson["id"],
            "lesson_title": next_lesson["title"],
            "level": next_lesson["level"]
        }
        return {"status": "completed", "next_lesson": next_lesson}
    else:
        if req.user_id in user_lesson_progress:
            del user_lesson_progress[req.user_id]
        return {"status": "completed", "next_lesson": None, "message": "Congratulations! You've completed this field."}


# ─────────────────────────────────────────────────────────────────────────────
# PROJECTS API - Personal projects with LEGO-style build instructions
# ─────────────────────────────────────────────────────────────────────────────

user_project_progress: dict = {}


class ProjectStartRequest(BaseModel):
    project_id: str
    phase_id: str | None = None
    user_id: str = "default"


class ProjectStepRequest(BaseModel):
    project_id: str
    user_id: str = "default"


@app.get("/project-specs")
def list_project_specs():
    """List all available project specifications from the registry"""
    return {"projects": project_registry.list_all()}


@app.get("/project-specs/{project_id}")
def get_project_spec(project_id: str):
    """Get full project specification from registry"""
    project = project_registry.get(project_id)
    if not project:
        return {"error": f"Project '{project_id}' not found"}
    return project.to_dict()


@app.get("/project-specs/{project_id}/phases")
def get_project_phases(project_id: str):
    """Get all phases for a project"""
    project = project_registry.get(project_id)
    if not project:
        return {"error": f"Project '{project_id}' not found"}
    return {
        "project": project.name,
        "phases": [p.to_dict() for p in project.phases]
    }


@app.get("/project-specs/{project_id}/phases/{phase_id}")
def get_project_phase(project_id: str, phase_id: str):
    """Get specific phase details"""
    project = project_registry.get(project_id)
    if not project:
        return {"error": f"Project '{project_id}' not found"}
    phase = project.get_phase(phase_id)
    if not phase:
        return {"error": f"Phase '{phase_id}' not found in project"}
    return phase.to_dict()


@app.get("/project-specs/{project_id}/persona/{persona}")
def get_project_persona_role(project_id: str, persona: str):
    """Get what a specific persona contributes to this project"""
    project = project_registry.get(project_id)
    if not project:
        return {"error": f"Project '{project_id}' not found"}
    role = project.get_persona_role(persona)
    if not role:
        return {"error": f"No role defined for '{persona}' in this project"}
    return {
        "project": project.name,
        "role": role.to_dict()
    }


@app.get("/project-specs/{project_id}/safety")
def get_project_safety(project_id: str):
    """Get safety constraints for a project"""
    project = project_registry.get(project_id)
    if not project:
        return {"error": f"Project '{project_id}' not found"}
    return {
        "project": project.name,
        "what_it_does_not_do": project.what_it_does_not_do,
        "safety_constraints": [c.to_dict() for c in project.safety_constraints]
    }


@app.post("/project-specs/start")
def start_project_build(req: ProjectStartRequest):
    """Start building a project from the beginning or a specific phase"""
    project = project_registry.get(req.project_id)
    if not project:
        return {"error": f"Project '{req.project_id}' not found"}
    
    if req.phase_id:
        phase = project.get_phase(req.phase_id)
        if not phase:
            return {"error": f"Phase '{req.phase_id}' not found"}
    else:
        phase = project.phases[0] if project.phases else None
        if not phase:
            return {"error": "Project has no phases defined"}
    
    first_module = phase.modules[0] if phase.modules else None
    first_step = first_module.steps[0] if first_module and first_module.steps else None
    
    user_project_progress[req.user_id] = {
        "project_id": req.project_id,
        "project_name": project.name,
        "phase_id": phase.id,
        "phase_name": phase.name,
        "module_id": first_module.id if first_module else None,
        "module_name": first_module.name if first_module else None,
        "step_index": 0,
        "step_id": first_step.id if first_step else None
    }
    
    return {
        "status": "started",
        "project": project.name,
        "big_picture": project.big_picture,
        "phase": phase.name,
        "phase_purpose": phase.purpose,
        "first_module": first_module.name if first_module else None,
        "first_step": first_step.to_dict() if first_step else None,
        "what_it_does_not_do": project.what_it_does_not_do
    }


@app.get("/project-specs/progress/{user_id}")
def get_project_progress(user_id: str):
    """Get current project build progress"""
    progress = user_project_progress.get(user_id)
    if not progress:
        return {"status": "no_active_project", "message": "No project in progress"}
    return {"status": "in_progress", "progress": progress}


@app.post("/project-specs/next-step")
def get_next_project_step(req: ProjectStepRequest):
    """Get the next step in current project build"""
    progress = user_project_progress.get(req.user_id)
    if not progress:
        return {"error": "No project in progress. Use /project-specs/start first."}
    
    project = project_registry.get(progress["project_id"])
    if not project:
        return {"error": "Project not found"}
    
    phase = project.get_phase(progress["phase_id"])
    if not phase:
        return {"error": "Phase not found"}
    
    current_module = None
    module_index = 0
    for i, m in enumerate(phase.modules):
        if m.id == progress["module_id"]:
            current_module = m
            module_index = i
            break
    
    if not current_module:
        return {"error": "Module not found"}
    
    next_step_index = progress["step_index"] + 1
    
    if next_step_index < len(current_module.steps):
        next_step = current_module.steps[next_step_index]
        progress["step_index"] = next_step_index
        progress["step_id"] = next_step.id
        return {
            "status": "next_step",
            "module": current_module.name,
            "step": next_step.to_dict(),
            "step_number": next_step_index + 1,
            "total_steps": len(current_module.steps)
        }
    
    if module_index + 1 < len(phase.modules):
        next_module = phase.modules[module_index + 1]
        first_step = next_module.steps[0] if next_module.steps else None
        progress["module_id"] = next_module.id
        progress["module_name"] = next_module.name
        progress["step_index"] = 0
        progress["step_id"] = first_step.id if first_step else None
        return {
            "status": "new_module",
            "module": next_module.name,
            "module_description": next_module.description,
            "completion_test": current_module.completion_test,
            "step": first_step.to_dict() if first_step else None
        }
    
    phase_index = 0
    for i, p in enumerate(project.phases):
        if p.id == phase.id:
            phase_index = i
            break
    
    if phase_index + 1 < len(project.phases):
        next_phase = project.phases[phase_index + 1]
        first_module = next_phase.modules[0] if next_phase.modules else None
        first_step = first_module.steps[0] if first_module and first_module.steps else None
        progress["phase_id"] = next_phase.id
        progress["phase_name"] = next_phase.name
        progress["module_id"] = first_module.id if first_module else None
        progress["module_name"] = first_module.name if first_module else None
        progress["step_index"] = 0
        progress["step_id"] = first_step.id if first_step else None
        return {
            "status": "new_phase",
            "phase": next_phase.name,
            "phase_purpose": next_phase.purpose,
            "simulation_only": next_phase.simulation_only,
            "first_module": first_module.name if first_module else None,
            "step": first_step.to_dict() if first_step else None
        }
    
    del user_project_progress[req.user_id]
    return {
        "status": "project_complete",
        "project": project.name,
        "message": "You've completed all phases! Time to reflect on what you built."
    }


@app.get("/project-specs/for-persona/{persona}")
def get_projects_for_persona(persona: str):
    """Get all projects where this persona has a defined role"""
    projects = project_registry.get_for_persona(persona)
    return {
        "persona": persona,
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "purpose": p.purpose,
                "role": role.to_dict() if (role := p.get_persona_role(persona)) else None
            }
            for p in projects
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE SYSTEM API - How AIs access and use knowledge
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/knowledge/philosophy")
def get_knowledge_philosophy():
    """Get the knowledge philosophy - how AIs think and learn"""
    return KNOWLEDGE_PHILOSOPHY


@app.get("/knowledge/sources")
def get_knowledge_sources():
    """Get all knowledge source categories"""
    return {"sources": [s.to_dict() for s in KNOWLEDGE_SOURCES]}


@app.get("/knowledge/sources/{persona}")
def get_knowledge_sources_by_persona(persona: str):
    """Get knowledge sources relevant to a specific persona"""
    sources = get_sources_for_persona(persona)
    if not sources:
        return {"error": f"No sources found for persona '{persona}'"}
    return {"persona": persona, "sources": sources}


@app.get("/knowledge/boundaries")
def get_knowledge_boundaries():
    """Get knowledge boundaries - what AIs will NOT do"""
    return KNOWLEDGE_BOUNDARIES


class CreatePackRequest(BaseModel):
    name: str
    description: str
    owner: str = "default"


class AddItemRequest(BaseModel):
    pack_id: str
    title: str
    content: str
    source: str
    category: str


class SearchPacksRequest(BaseModel):
    query: str
    owner: str | None = None


@app.get("/knowledge/packs")
def list_knowledge_packs(owner: str | None = None):
    """List all custom knowledge packs"""
    packs = knowledge_pack_registry.list_packs(owner)
    return {"packs": packs}


@app.post("/knowledge/packs/create")
def create_knowledge_pack(req: CreatePackRequest):
    """Create a new custom knowledge pack"""
    pack = knowledge_pack_registry.create_pack(req.name, req.description, req.owner)
    return {"status": "created", "pack": pack.to_dict()}


@app.get("/knowledge/packs/{pack_id}")
def get_knowledge_pack(pack_id: str):
    """Get a specific knowledge pack with its items"""
    pack = knowledge_pack_registry.get_pack(pack_id)
    if not pack:
        return {"error": f"Pack '{pack_id}' not found"}
    return pack.to_dict_full()


@app.post("/knowledge/packs/add-item")
def add_item_to_pack(req: AddItemRequest):
    """Add a knowledge item to a pack"""
    item = knowledge_pack_registry.add_item_to_pack(
        req.pack_id, req.title, req.content, req.source, req.category
    )
    if not item:
        return {"error": f"Pack '{req.pack_id}' not found"}
    return {"status": "added", "item": item.to_dict()}


@app.delete("/knowledge/packs/{pack_id}")
def delete_knowledge_pack(pack_id: str):
    """Delete a knowledge pack"""
    success = knowledge_pack_registry.delete_pack(pack_id)
    if not success:
        return {"error": f"Pack '{pack_id}' not found"}
    return {"status": "deleted", "pack_id": pack_id}


@app.post("/knowledge/search")
def search_knowledge_packs(req: SearchPacksRequest):
    """Search across custom knowledge packs"""
    results = knowledge_pack_registry.search_all_packs(req.query, req.owner)
    return {"query": req.query, "results": results}


# ─────────────────────────────────────────────────────────────
# SYSTEM SPECS ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/specs")
def get_all_specs():
    """Get complete system specifications overview"""
    return {
        "title": "ATLAS-PRIME Technical & Functional Specifications",
        "summary": CORE_ARCHITECTURE["one_line_summary"],
        "sections": [
            {"id": "architecture", "name": "Core Architecture", "endpoint": "/specs/architecture"},
            {"id": "council", "name": "Tri-Core Council", "endpoint": "/specs/council"},
            {"id": "intelligence", "name": "Intelligence Specs", "endpoint": "/specs/intelligence"},
            {"id": "knowledge-spectrum", "name": "Knowledge Spectrum", "endpoint": "/specs/knowledge-spectrum"},
            {"id": "teaching", "name": "Teaching System", "endpoint": "/specs/teaching"},
            {"id": "autonomy", "name": "Autonomy & Boundaries", "endpoint": "/specs/autonomy"},
            {"id": "personality", "name": "Personality & Voice", "endpoint": "/specs/personality"},
            {"id": "capabilities", "name": "Multimodal Capabilities", "endpoint": "/specs/capabilities"},
            {"id": "security", "name": "Security & Ethics", "endpoint": "/specs/security"},
            {"id": "evolution", "name": "Update & Evolution", "endpoint": "/specs/evolution"}
        ]
    }


@app.get("/specs/architecture")
def get_architecture_specs():
    """Get core architecture specifications"""
    return {
        "section": "Core Architecture",
        "architecture": CORE_ARCHITECTURE,
        "council_structure": {
            "members": list(TRI_CORE_COUNCIL.keys()),
            "council_mode": TRI_CORE_COUNCIL.get("council_mode")
        }
    }


@app.get("/specs/council")
def get_council_specs():
    """Get Tri-Core Council specifications"""
    return {
        "section": "Tri-Core Council",
        "personas": {
            "ajani": TRI_CORE_COUNCIL["ajani"],
            "minerva": TRI_CORE_COUNCIL["minerva"],
            "hermes": TRI_CORE_COUNCIL["hermes"]
        },
        "council_mode": TRI_CORE_COUNCIL["council_mode"]
    }


@app.get("/specs/council/{persona}")
def get_persona_spec(persona: str):
    """Get specs for a specific persona"""
    persona = persona.lower()
    if persona not in TRI_CORE_COUNCIL:
        return {"error": f"Unknown persona: {persona}"}
    return {
        "persona": persona,
        "specs": TRI_CORE_COUNCIL[persona]
    }


@app.get("/specs/intelligence")
def get_intelligence_specs():
    """Get reasoning and learning intelligence specs"""
    return {
        "section": "Intelligence Specifications",
        "cognitive": COGNITIVE_CAPABILITIES,
        "learning": LEARNING_INTELLIGENCE
    }


@app.get("/specs/teaching")
def get_teaching_specs():
    """Get teaching system specifications (the LEGO-style secret sauce)"""
    return {
        "section": "Teaching System",
        "teaching": TEACHING_SYSTEM,
        "assessment": ASSESSMENT_SYSTEM
    }


@app.get("/specs/autonomy")
def get_autonomy_specs():
    """Get autonomy level and system boundaries"""
    return {
        "section": "Autonomy & Boundaries",
        "autonomy": AUTONOMY_SPECS,
        "boundaries": SYSTEM_BOUNDARIES
    }


@app.get("/specs/personality")
def get_personality_specs():
    """Get personality and expression specifications"""
    return {
        "section": "Personality & Expression",
        "personality": PERSONALITY_SPECS,
        "behavioral_traits": BEHAVIORAL_TRAITS
    }


@app.get("/specs/capabilities")
def get_capabilities_specs():
    """Get multimodal capabilities and hardware awareness"""
    return {
        "section": "Capabilities & Hardware",
        "multimodal": MULTIMODAL_CAPABILITIES,
        "hardware": HARDWARE_AWARENESS
    }


@app.get("/specs/security")
def get_security_specs():
    """Get security and ethics specifications (Hermes Layer)"""
    return {
        "section": "Security & Ethics",
        "security": SECURITY_SPECS,
        "ethics": ETHICS_LAYER
    }


@app.get("/specs/knowledge-spectrum")
def get_knowledge_spectrum_specs():
    """Get knowledge spectrum - all domains the AIs understand"""
    return {
        "section": "Knowledge Spectrum",
        "spectrum": KNOWLEDGE_SPECTRUM
    }


@app.get("/specs/evolution")
def get_evolution_specs():
    """Get update and evolution specifications"""
    return {
        "section": "Update & Evolution",
        "evolution": EVOLUTION_SPECS
    }


class ProgressUpdate(BaseModel):
    field: str | None = None
    lesson_id: str | None = None
    status: str | None = None
    current_step: int | None = None
    mastery_level: float | None = None
    time_spent_minutes: int | None = None
    notes: str | None = None


class KnowledgePackCreate(BaseModel):
    name: str
    description: str | None = None
    category: str = "general"
    persona_scope: str = "all"
    content: str
    source_type: str = "text"


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    category: str = "general"
    goal: str | None = None
    parts_list: str | None = None
    assigned_personas: str = "all"
    tags: str | None = None


class ProjectStepCreate(BaseModel):
    step_number: int
    title: str
    description: str | None = None
    instructions: str | None = None
    parts_needed: str | None = None
    checkpoint: str | None = None
    is_milestone: bool = False


@app.get("/progress")
def get_user_progress(user_id: str = "default_user"):
    """Get user's overall learning progress"""
    if SessionLocal is None:
        return {"error": "Database not configured", "fallback": True, "user_id": user_id}
    
    db = SessionLocal()
    try:
        user = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        if not user:
            user = UserProgress(user_id=user_id)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        lessons = db.query(LessonProgress).filter(LessonProgress.user_id == user_id).all()
        
        return {
            "user_id": user.user_id,
            "current_field": user.current_field,
            "current_lesson": user.current_lesson,
            "total_lessons_completed": user.total_lessons_completed,
            "total_checkpoints_passed": user.total_checkpoints_passed,
            "learning_style": user.learning_style,
            "lessons": [
                {
                    "field": l.field,
                    "lesson_id": l.lesson_id,
                    "lesson_title": l.lesson_title,
                    "status": l.status,
                    "current_step": l.current_step,
                    "total_steps": l.total_steps,
                    "mastery_level": l.mastery_level,
                    "time_spent_minutes": l.time_spent_minutes
                } for l in lessons
            ]
        }
    finally:
        db.close()


@app.post("/progress/lesson")
def update_lesson_progress(update: ProgressUpdate, user_id: str = "default_user"):
    """Update progress on a specific lesson"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        lesson = db.query(LessonProgress).filter(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id == update.lesson_id
        ).first()
        
        if not lesson:
            lesson = LessonProgress(
                user_id=user_id,
                field=update.field or "general",
                lesson_id=update.lesson_id or "unknown",
                lesson_title=update.lesson_id or "Untitled Lesson"
            )
            db.add(lesson)
        
        if update.status:
            lesson.status = update.status
            if update.status == "in_progress" and not lesson.started_at:
                from datetime import datetime
                lesson.started_at = datetime.utcnow()
            elif update.status == "completed" and not lesson.completed_at:
                from datetime import datetime
                lesson.completed_at = datetime.utcnow()
        
        if update.current_step is not None:
            lesson.current_step = update.current_step
        if update.mastery_level is not None:
            lesson.mastery_level = update.mastery_level
        if update.time_spent_minutes is not None:
            lesson.time_spent_minutes += update.time_spent_minutes
        if update.notes:
            lesson.notes = update.notes
        
        user = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        if user:
            user.current_field = update.field or user.current_field
            user.current_lesson = update.lesson_id or user.current_lesson
            if update.status == "completed":
                user.total_lessons_completed += 1
        
        db.commit()
        return {"success": True, "lesson_id": lesson.lesson_id, "status": lesson.status}
    finally:
        db.close()


@app.get("/knowledge-packs")
def list_knowledge_packs(user_id: str = "default_user"):
    """List all custom knowledge packs"""
    if SessionLocal is None:
        return {"packs": [], "fallback": True}
    
    db = SessionLocal()
    try:
        packs = db.query(KnowledgePack).filter(KnowledgePack.user_id == user_id).all()
        return {
            "packs": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category,
                    "persona_scope": p.persona_scope,
                    "source_type": p.source_type,
                    "is_active": p.is_active,
                    "created_at": p.created_at.isoformat()
                } for p in packs
            ]
        }
    finally:
        db.close()


@app.post("/knowledge-packs")
def create_knowledge_pack(pack: KnowledgePackCreate, user_id: str = "default_user"):
    """Create a new custom knowledge pack"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        new_pack = KnowledgePack(
            user_id=user_id,
            name=pack.name,
            description=pack.description,
            category=pack.category,
            persona_scope=pack.persona_scope,
            content=pack.content,
            source_type=pack.source_type
        )
        db.add(new_pack)
        db.commit()
        db.refresh(new_pack)
        return {"success": True, "id": new_pack.id, "name": new_pack.name}
    finally:
        db.close()


@app.post("/knowledge-packs/upload")
async def upload_knowledge_pack(
    file: UploadFile = File(...),
    name: str = "Uploaded Pack",
    category: str = "general",
    persona_scope: str = "all",
    user_id: str = "default_user"
):
    """Upload a file as a knowledge pack"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    content = await file.read()
    content_str = content.decode("utf-8", errors="ignore")
    
    db = SessionLocal()
    try:
        new_pack = KnowledgePack(
            user_id=user_id,
            name=name,
            category=category,
            persona_scope=persona_scope,
            content=content_str,
            source_type="file",
            source_filename=file.filename
        )
        db.add(new_pack)
        db.commit()
        db.refresh(new_pack)
        return {"success": True, "id": new_pack.id, "name": new_pack.name, "filename": file.filename}
    finally:
        db.close()


@app.delete("/knowledge-packs/{pack_id}")
def delete_knowledge_pack(pack_id: int, user_id: str = "default_user"):
    """Delete a knowledge pack"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        pack = db.query(KnowledgePack).filter(
            KnowledgePack.id == pack_id,
            KnowledgePack.user_id == user_id
        ).first()
        if pack:
            db.delete(pack)
            db.commit()
            return {"success": True, "deleted_id": pack_id}
        return {"error": "Pack not found"}
    finally:
        db.close()


@app.get("/projects")
def list_projects(user_id: str = "default_user"):
    """List all personal projects"""
    if SessionLocal is None:
        return {"projects": [], "fallback": True}
    
    db = SessionLocal()
    try:
        projects = db.query(PersonalProject).filter(PersonalProject.user_id == user_id).all()
        return {
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category,
                    "status": p.status,
                    "priority": p.priority,
                    "current_phase": p.current_phase,
                    "assigned_personas": p.assigned_personas,
                    "tags": p.tags,
                    "created_at": p.created_at.isoformat(),
                    "steps_count": len(p.steps),
                    "steps_completed": len([s for s in p.steps if s.status == "completed"])
                } for p in projects
            ]
        }
    finally:
        db.close()


@app.post("/projects")
def create_project(project: ProjectCreate, user_id: str = "default_user"):
    """Create a new personal project with LEGO build system"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        new_project = PersonalProject(
            user_id=user_id,
            name=project.name,
            description=project.description,
            category=project.category,
            goal=project.goal,
            parts_list=project.parts_list,
            assigned_personas=project.assigned_personas,
            tags=project.tags
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return {"success": True, "id": new_project.id, "name": new_project.name}
    finally:
        db.close()


@app.get("/projects/{project_id}")
def get_project(project_id: int, user_id: str = "default_user"):
    """Get a project with all its steps"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        project = db.query(PersonalProject).filter(
            PersonalProject.id == project_id,
            PersonalProject.user_id == user_id
        ).first()
        
        if not project:
            return {"error": "Project not found"}
        
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "category": project.category,
            "status": project.status,
            "priority": project.priority,
            "goal": project.goal,
            "parts_list": project.parts_list,
            "current_phase": project.current_phase,
            "assigned_personas": project.assigned_personas,
            "tags": project.tags,
            "notes": project.notes,
            "created_at": project.created_at.isoformat(),
            "steps": [
                {
                    "id": s.id,
                    "step_number": s.step_number,
                    "title": s.title,
                    "description": s.description,
                    "instructions": s.instructions,
                    "parts_needed": s.parts_needed,
                    "checkpoint": s.checkpoint,
                    "status": s.status,
                    "is_milestone": s.is_milestone
                } for s in sorted(project.steps, key=lambda x: x.step_number)
            ]
        }
    finally:
        db.close()


@app.post("/projects/{project_id}/steps")
def add_project_step(project_id: int, step: ProjectStepCreate, user_id: str = "default_user"):
    """Add a LEGO-style step to a project"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        project = db.query(PersonalProject).filter(
            PersonalProject.id == project_id,
            PersonalProject.user_id == user_id
        ).first()
        
        if not project:
            return {"error": "Project not found"}
        
        new_step = ProjectStep(
            project_id=project_id,
            step_number=step.step_number,
            title=step.title,
            description=step.description,
            instructions=step.instructions,
            parts_needed=step.parts_needed,
            checkpoint=step.checkpoint,
            is_milestone=step.is_milestone
        )
        db.add(new_step)
        db.commit()
        db.refresh(new_step)
        return {"success": True, "id": new_step.id, "step_number": new_step.step_number}
    finally:
        db.close()


@app.put("/projects/{project_id}/steps/{step_id}/complete")
def complete_project_step(project_id: int, step_id: int, user_id: str = "default_user"):
    """Mark a project step as completed"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        step = db.query(ProjectStep).filter(
            ProjectStep.id == step_id,
            ProjectStep.project_id == project_id
        ).first()
        
        if not step:
            return {"error": "Step not found"}
        
        from datetime import datetime
        step.status = "completed"
        step.completed_at = datetime.utcnow()
        db.commit()
        return {"success": True, "step_id": step_id, "status": "completed"}
    finally:
        db.close()


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, user_id: str = "default_user"):
    """Delete a project and all its steps"""
    if SessionLocal is None:
        return {"error": "Database not configured"}
    
    db = SessionLocal()
    try:
        project = db.query(PersonalProject).filter(
            PersonalProject.id == project_id,
            PersonalProject.user_id == user_id
        ).first()
        if project:
            db.delete(project)
            db.commit()
            return {"success": True, "deleted_id": project_id}
        return {"error": "Project not found"}
    finally:
        db.close()


LEGO_LESSONS = {
    "intro_to_systems_thinking": {
        "id": "intro_to_systems_thinking",
        "title": "Systems Thinking: See the Whole Picture",
        "field": "engineering",
        "persona": "ajani",
        "difficulty": "beginner",
        "goal": "Learn to see how parts connect to make a whole system",
        "parts_list": [
            "Pencil and paper",
            "Any complex object nearby (phone, remote, toy)"
        ],
        "steps": [
            {
                "step": 1,
                "title": "Pick Your Subject",
                "instruction": "Grab something nearby - your phone, a TV remote, or even a bicycle. This is your 'system' to study.",
                "visual": "Pick up the object. Turn it around. Look at it like you're seeing it for the first time.",
                "checkpoint": "You have an object in hand and you're curious about how it works."
            },
            {
                "step": 2,
                "title": "List the Parts",
                "instruction": "Write down every part you can see. Screen, buttons, battery door, speaker holes. Don't worry about what's inside yet.",
                "visual": "Make a simple list: Part 1, Part 2, Part 3...",
                "checkpoint": "You have at least 5 parts listed."
            },
            {
                "step": 3,
                "title": "Draw the Connections",
                "instruction": "Now draw arrows between parts that 'talk' to each other. Button → Screen (pressing changes what you see). Battery → Everything (power flows).",
                "visual": "Your paper now looks like a web of connections.",
                "checkpoint": "You can point to at least 3 connections and explain what happens."
            },
            {
                "step": 4,
                "title": "Find the Hidden Parts",
                "instruction": "What parts can't you see but MUST exist? A processor, wires, software. Add these to your diagram in a different color.",
                "visual": "Add boxes labeled '???' for things you suspect exist inside.",
                "checkpoint": "You've identified at least 2 hidden parts that make the visible parts work."
            },
            {
                "step": 5,
                "title": "Ask 'What Happens If?'",
                "instruction": "Systems thinking means asking: 'What breaks if I remove this part?' Pick any part and trace what stops working.",
                "visual": "Cross out a part. Follow the arrows. See the cascade.",
                "checkpoint": "You can explain a failure chain: 'If X breaks, then Y stops, which means Z can't happen.'"
            }
        ],
        "test": {
            "type": "application",
            "prompt": "Look at a different object. Can you draw its system diagram in under 3 minutes?",
            "success_criteria": "You identified parts, connections, and at least one hidden component."
        },
        "upgrade_paths": [
            "feedback_loops",
            "failure_analysis", 
            "system_optimization"
        ]
    },
    "intro_to_storytelling": {
        "id": "intro_to_storytelling",
        "title": "The Bones of a Story",
        "field": "culture",
        "persona": "minerva",
        "difficulty": "beginner",
        "goal": "Understand the skeleton that holds every story together",
        "parts_list": [
            "Your imagination",
            "A character you care about (real or invented)",
            "A problem that matters"
        ],
        "steps": [
            {
                "step": 1,
                "title": "The Character",
                "instruction": "Every story starts with someone who WANTS something. Not just needs - WANTS. Write one sentence: '[Name] wants [specific thing] because [deep reason].'",
                "visual": "Example: 'Maya wants to find her missing brother because he's the only one who believed in her.'",
                "checkpoint": "Your character's want is specific and emotional, not vague."
            },
            {
                "step": 2,
                "title": "The Obstacle",
                "instruction": "What stands in the way? Make it hard. Not impossible, but HARD. The bigger the obstacle, the more we care.",
                "visual": "Example: 'The last place her brother was seen is a city that doesn't appear on any map.'",
                "checkpoint": "Your obstacle makes the reader think 'How could they possibly overcome this?'"
            },
            {
                "step": 3,
                "title": "The Price",
                "instruction": "What will your character have to sacrifice or risk to try? Stories have weight when something is at stake.",
                "visual": "Example: 'To enter the hidden city, Maya must give up her memories of her brother - the very thing she's trying to save.'",
                "checkpoint": "The price creates a painful choice, not an easy decision."
            },
            {
                "step": 4,
                "title": "The Change",
                "instruction": "By the end, your character is different. Not just in situation - in WHO THEY ARE. What do they learn about themselves?",
                "visual": "Example: 'Maya learns that holding on too tight can push things away - and letting go is the only way to truly keep someone.'",
                "checkpoint": "The change is internal, not just external."
            }
        ],
        "test": {
            "type": "creation",
            "prompt": "In 4 sentences, pitch a story using this structure: Want → Obstacle → Price → Change.",
            "success_criteria": "Each element is present and they connect emotionally."
        },
        "upgrade_paths": [
            "character_arcs",
            "world_building",
            "theme_development"
        ]
    },
    "intro_to_patterns": {
        "id": "intro_to_patterns",
        "title": "Pattern Recognition: See What Others Miss",
        "field": "logic",
        "persona": "hermes",
        "difficulty": "beginner",
        "goal": "Train your mind to spot patterns hiding in plain sight",
        "parts_list": [
            "Your eyes",
            "A notebook for pattern hunting",
            "Curiosity about the ordinary"
        ],
        "steps": [
            {
                "step": 1,
                "title": "The Obvious Pattern",
                "instruction": "Look at this sequence: 2, 4, 6, 8, _. Easy, right? It's 10. But here's the trick - what RULE describes this pattern?",
                "visual": "Don't just find the answer. Find the RECIPE.",
                "checkpoint": "You said 'add 2 each time' or 'each number is 2 more than the previous.'"
            },
            {
                "step": 2,
                "title": "The Hidden Pattern",
                "instruction": "Now try this: 1, 1, 2, 3, 5, 8, _. This is the Fibonacci sequence - each number is the sum of the two before it.",
                "visual": "1+1=2, 1+2=3, 2+3=5, 3+5=8... so next is 5+8=13.",
                "checkpoint": "You can generate the next 3 numbers without looking them up."
            },
            {
                "step": 3,
                "title": "Patterns in the Wild",
                "instruction": "Look around your room. Find 3 patterns: repeating shapes, colors, or arrangements. Patterns are everywhere - floor tiles, book spines, window grids.",
                "visual": "Take a photo or sketch each pattern you find.",
                "checkpoint": "You've identified at least 3 different patterns in your environment."
            },
            {
                "step": 4,
                "title": "Break the Pattern",
                "instruction": "Here's the master skill: find where a pattern BREAKS. Anomalies are where interesting things hide. Look at your found patterns - is there a tile that's crooked? A book that doesn't fit?",
                "visual": "Circle the break. Ask: 'Why is this different?'",
                "checkpoint": "You found at least one break and have a theory about why it exists."
            }
        ],
        "test": {
            "type": "observation",
            "prompt": "Spend 5 minutes pattern-hunting somewhere new. Report back with: 1 pattern you found, 1 pattern break, and why the break matters.",
            "success_criteria": "You demonstrated active pattern-seeking behavior."
        },
        "upgrade_paths": [
            "mathematical_sequences",
            "visual_pattern_analysis",
            "behavioral_patterns"
        ]
    }
}


@app.get("/lego-lessons")
def list_lego_lessons():
    """List all LEGO-style lessons"""
    return {
        "lessons": [
            {
                "id": l["id"],
                "title": l["title"],
                "field": l["field"],
                "persona": l["persona"],
                "difficulty": l["difficulty"],
                "goal": l["goal"],
                "steps_count": len(l["steps"])
            } for l in LEGO_LESSONS.values()
        ]
    }


@app.get("/lego-lessons/{lesson_id}")
def get_lego_lesson(lesson_id: str):
    """Get a complete LEGO-style lesson with all steps"""
    if lesson_id not in LEGO_LESSONS:
        return {"error": "Lesson not found"}
    return LEGO_LESSONS[lesson_id]


@app.get("/lego-lessons/{lesson_id}/step/{step_number}")
def get_lego_lesson_step(lesson_id: str, step_number: int):
    """Get a specific step from a LEGO lesson"""
    if lesson_id not in LEGO_LESSONS:
        return {"error": "Lesson not found"}
    
    lesson = LEGO_LESSONS[lesson_id]
    for step in lesson["steps"]:
        if step["step"] == step_number:
            return {
                "lesson_id": lesson_id,
                "lesson_title": lesson["title"],
                "total_steps": len(lesson["steps"]),
                **step
            }
    return {"error": "Step not found"}


# ==================== SAVED PROJECTS STORAGE ====================


# ==================== REGISTER ROUTE MODULES ====================

app.include_router(chat_router)
app.include_router(design_router)
app.include_router(conversations_router)
app.include_router(tts_router)
app.include_router(user_data_router)
app.include_router(lesson_plans_router)
app.include_router(ai_routing_router)
