"""
Design Engine API — Plugin-Based Tri-Core Engineering Pipeline.

Endpoints:
- GET  /design-engine/plugins          — List available project type plugins
- POST /design-engine/project          — Create a new project (persisted)
- GET  /design-engine/projects         — List all saved projects
- POST /design-engine/dream            — Generate unvalidated concept variants
- POST /design-engine/constraints      — Extract engineering constraints with persona analysis
- POST /design-engine/iterate          — Plugin-driven design iteration
- POST /design-engine/validate         — Run 5-check validation gate
- GET  /design-engine/defaults/{type}  — Get default constraints for a plugin
- POST /design-engine/parts            — Get parts list for a project type
- POST /design-engine/tests            — Get acceptance tests for a project type
"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from .agents import ajani_engineer, minerva_ethics, hermes_security
from .plugins.registry import load_plugins

router = APIRouter(prefix="/design-engine", tags=["design-engine"])

PLUGINS = load_plugins()

DATABASE_URL = os.environ.get("DATABASE_URL")
_pool = None


def _get_conn():
    global _pool
    if not DATABASE_URL:
        return None
    if _pool is None:
        from psycopg2 import pool
        _pool = pool.SimpleConnectionPool(1, 5, DATABASE_URL)
    return _pool.getconn()


def _put_conn(conn):
    if _pool and conn:
        _pool.putconn(conn)


def _init_db():
    conn = _get_conn()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS design_engine_projects (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                project_type TEXT NOT NULL,
                constraints JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        _put_conn(conn)


_init_db()


class ProjectInput(BaseModel):
    name: str
    description: str
    project_type: Optional[str] = None


class ConstraintInput(BaseModel):
    name: Optional[str] = None
    project_type: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    population: Optional[int] = 3
    scale: Optional[str] = None
    energy: Optional[str] = None
    materials: Optional[List[str]] = None
    fabrication: Optional[List[str]] = None
    physics: Optional[str] = None


@router.get("/plugins")
def list_plugins():
    return {
        "plugins": [
            {
                "key": p.key,
                "display_name": p.display_name,
                "default_constraints": p.default_constraints()
            }
            for p in PLUGINS.values()
        ]
    }


@router.get("/defaults/{project_type}")
def get_defaults(project_type: str):
    plugin = PLUGINS.get(project_type)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Unknown project type: {project_type}")
    return {
        "project_type": project_type,
        "display_name": plugin.display_name,
        "default_constraints": plugin.default_constraints()
    }


@router.post("/project")
def create_project(project: ProjectInput):
    if project.project_type and project.project_type not in PLUGINS:
        raise HTTPException(status_code=400, detail=f"Unknown project type: {project.project_type}")

    conn = _get_conn()
    if not conn:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO design_engine_projects (name, description, project_type) VALUES (%s, %s, %s) RETURNING id, created_at",
            (project.name, project.description, project.project_type or "generic")
        )
        row = cur.fetchone()
        conn.commit()
        return {
            "id": row[0],
            "name": project.name,
            "description": project.description,
            "project_type": project.project_type or "generic",
            "created_at": str(row[1])
        }
    finally:
        _put_conn(conn)


@router.get("/projects")
def list_projects():
    conn = _get_conn()
    if not conn:
        return {"projects": []}
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, project_type, created_at FROM design_engine_projects ORDER BY created_at DESC LIMIT 50")
        rows = cur.fetchall()
        return {
            "projects": [
                {"id": r[0], "name": r[1], "description": r[2], "project_type": r[3], "created_at": str(r[4])}
                for r in rows
            ]
        }
    finally:
        _put_conn(conn)


@router.post("/dream")
def dream_mode(project: ProjectInput):
    ideas = []
    for i in range(5):
        ideas.append({
            "concept": f"{project.name} Variant {i+1}",
            "description": f"Expanded concept based on: {project.description}"
        })
    return {
        "mode": "Dream Mode",
        "warning": "Unvalidated concepts — these need constraint extraction before advancing",
        "project_name": project.name,
        "ideas": ideas
    }


@router.post("/constraints")
def extract_constraints(project: ProjectInput):
    result = {
        "mode": "Constraint Extraction",
        "project_name": project.name,
        "required_fields": [
            "Define physical dimensions (scale)",
            "Define energy/power source",
            "Define material types",
            "Define fabrication steps",
            "Define governing physics principle"
        ],
        "agents": {
            "ajani": ajani_engineer(project.description),
            "minerva": minerva_ethics(project.description),
            "hermes": hermes_security(project.description)
        }
    }

    if project.project_type and project.project_type in PLUGINS:
        plugin = PLUGINS[project.project_type]
        result["plugin"] = plugin.display_name
        result["default_constraints"] = plugin.default_constraints()

    return result


@router.post("/iterate")
def iterate_design(data: ConstraintInput):
    project_type = data.project_type
    population = data.population or 3

    if project_type and project_type in PLUGINS:
        plugin = PLUGINS[project_type]
        constraints_dict = data.constraints or plugin.default_constraints()
        variants = []
        for i in range(population):
            variants.append(plugin.generate_variant(i, constraints_dict))
        return {
            "mode": "Plugin Iteration",
            "plugin": plugin.display_name,
            "population": population,
            "variants": variants,
            "parts_list": plugin.parts_list(constraints_dict),
            "acceptance_tests": plugin.acceptance_tests(constraints_dict)
        }
    else:
        import random
        variants = []
        for i in range(population):
            score = random.uniform(60, 95)
            variants.append({
                "name": f"Design Variant {i+1}",
                "performance": round(score, 2),
                "safety": round(random.uniform(70, 95), 2),
                "manufacturability": round(random.uniform(65, 90), 2),
                "cost": round(random.uniform(50, 500), 2),
                "weight": round(random.uniform(0.5, 10), 2),
                "complexity": round(random.uniform(30, 70), 2),
                "notes": "Generic variant (no plugin). Select a project type for domain-specific generation."
            })
        return {
            "mode": "Generic Iteration",
            "population": population,
            "constraint_summary": {
                "scale": data.scale or "undefined",
                "energy": data.energy or "undefined",
                "materials": data.materials or [],
                "fabrication": data.fabrication or [],
                "physics": data.physics or "undefined"
            },
            "variants": variants
        }


@router.post("/validate")
def validate_project(data: ConstraintInput):
    if data.project_type and data.project_type in PLUGINS:
        plugin = PLUGINS[data.project_type]
        constraints_dict = data.constraints or {}
        defaults = plugin.default_constraints()
        filled = sum(1 for k in defaults if constraints_dict.get(k) is not None)
        total = len(defaults)

        if filled == total:
            tier = "T1_PROTOTYPE_READY"
            tier_label = "Prototype-Ready"
            confidence = "HIGH"
        elif filled >= total * 0.6:
            tier = "T2_SIMULATION_ONLY"
            tier_label = "Simulation-Only"
            confidence = "MEDIUM"
        else:
            tier = "T4_CONCEPTUAL"
            tier_label = "Conceptual / Blocked"
            confidence = "LOW"

        checks = {k: constraints_dict.get(k) is not None for k in defaults}
        return {
            "mode": "Plugin Validation Gate",
            "name": data.name or "unnamed",
            "plugin": plugin.display_name,
            "checks": checks,
            "score": f"{filled}/{total}",
            "passed": filled,
            "total": total,
            "tier": tier,
            "tier_label": tier_label,
            "confidence": confidence,
            "blueprint_allowed": filled == total,
            "parts_list": plugin.parts_list(constraints_dict),
            "acceptance_tests": plugin.acceptance_tests(constraints_dict)
        }
    else:
        checks = {
            "scale": data.scale is not None,
            "energy": data.energy is not None,
            "materials": data.materials is not None and len(data.materials) > 0,
            "fabrication": data.fabrication is not None and len(data.fabrication) > 0,
            "physics": data.physics is not None
        }
        passed = sum(checks.values())

        if passed == 5:
            tier = "T1_PROTOTYPE_READY"
            tier_label = "Prototype-Ready"
            confidence = "HIGH"
        elif passed >= 3:
            tier = "T2_SIMULATION_ONLY"
            tier_label = "Simulation-Only"
            confidence = "MEDIUM"
        else:
            tier = "T4_CONCEPTUAL"
            tier_label = "Conceptual / Blocked"
            confidence = "LOW"

        return {
            "mode": "Validation Gate",
            "name": data.name or "unnamed",
            "checks": checks,
            "score": f"{passed}/5",
            "passed": passed,
            "total": 5,
            "tier": tier,
            "tier_label": tier_label,
            "confidence": confidence,
            "blueprint_allowed": passed == 5
        }


@router.post("/parts")
def get_parts(data: ConstraintInput):
    if not data.project_type or data.project_type not in PLUGINS:
        raise HTTPException(status_code=400, detail="project_type required and must match a plugin")
    plugin = PLUGINS[data.project_type]
    constraints_dict = data.constraints or plugin.default_constraints()
    return {
        "plugin": plugin.display_name,
        "parts_list": plugin.parts_list(constraints_dict)
    }


@router.post("/tests")
def get_tests(data: ConstraintInput):
    if not data.project_type or data.project_type not in PLUGINS:
        raise HTTPException(status_code=400, detail="project_type required and must match a plugin")
    plugin = PLUGINS[data.project_type]
    constraints_dict = data.constraints or plugin.default_constraints()
    return {
        "plugin": plugin.display_name,
        "acceptance_tests": plugin.acceptance_tests(constraints_dict)
    }
