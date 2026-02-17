from __future__ import annotations
from fastapi import APIRouter
from .schemas import BlueprintRequest
from .libraries import MATERIALS_DB, COMPONENTS_DB, TOOLS_DB
from .templates import TEMPLATES
from .validation import validate_packet

router = APIRouter(prefix="/blueprint-engine", tags=["Blueprint Engine"])


@router.get("/libraries")
def libraries():
    return {
        "materials": {k: v for k, v in MATERIALS_DB.items()},
        "components": {k: v for k, v in COMPONENTS_DB.items()},
        "tools": {k: v for k, v in TOOLS_DB.items()},
    }


@router.get("/projects")
def list_projects():
    return {
        "projects": [
            {"key": "GREEN_BOT", "title": "Green Bot — Eco Terraform Rover", "domain": "ROBOTICS", "safety": "MEDIUM"},
            {"key": "MEDUSA_ARMS", "title": "Medusa Arms — Modular Tentacle Manipulators", "domain": "ROBOTICS", "safety": "MEDIUM"},
            {"key": "METAL_FLOWERS", "title": "Metal Flowers — Deployable Geo-Seed Sculptures", "domain": "MATERIALS", "safety": "LOW"},
            {"key": "HYDROGEN_POWER", "title": "Hydrogen Power Module — PEM Fuel Cell Pack", "domain": "ENERGY", "safety": "HIGH"},
            {"key": "MORPHING_STRUCTURES", "title": "Morphing Structures — Compliant + Smart Material Demo", "domain": "MATERIALS", "safety": "MEDIUM"},
            {"key": "ATOMIC_UI", "title": "Atomic UI System — Blueprint Viewer Components", "domain": "UI_SYSTEM", "safety": "LOW"},
        ]
    }


@router.post("/generate")
def generate_blueprint(req: BlueprintRequest):
    template_fn = TEMPLATES.get(req.project_key)
    if not template_fn:
        return {"error": f"Unknown project key: {req.project_key}"}
    packet = template_fn(req.version, req.constraints)
    issues = validate_packet(packet)
    return {
        "packet": packet.model_dump(),
        "validation": {
            "ok": len(issues) == 0,
            "issues": issues,
        }
    }
