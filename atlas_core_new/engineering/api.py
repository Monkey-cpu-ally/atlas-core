"""
Build → Prove → Lock API — Engineering Doctrine Endpoints.

Provides:
- /engineering/truth-doc — Full feature specification document
- /engineering/truth-doc/{feature_id} — Single feature spec
- /engineering/architecture — 4-layer architecture map
- /engineering/refusal/summary — Failure handling summary
- /engineering/refusal/events — Recent refusal events
- /engineering/observability/health — System health summary
- /engineering/observability/events — Recent observability events
- /engineering/observability/crashes — Crash reports
- /engineering/pipeline — Release stage definitions + feature stages
- /engineering/dod — Definition of Done checklist status per feature
- /engineering/doctrine — Full Build → Prove → Lock doctrine
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from .truth_doc import TRUTH_DOC, ARCHITECTURE_LAYERS, RELEASE_STAGES, DESIGN_PHILOSOPHY
from .refusal_engine import get_recent_events as get_refusal_events, get_failure_summary
from .observability import (
    get_recent_events as get_obs_events,
    get_crash_reports,
    get_counters,
    get_health_summary,
    emit,
    EventCategory,
    EventLevel,
)
from .validation import ProjectSpec, validate_project, autofill_minimums
from .domain_packs import DOMAINS, domain_pack, build_minimum_build_card, apply_overrides
from .text_intake import detect_domain, extract_title, attach_user_constraints, detect_overrides, split_into_projects

router = APIRouter(prefix="/engineering", tags=["engineering-doctrine"])


@router.get("/doctrine")
def get_doctrine():
    return {
        "status": "ok",
        "doctrine": DESIGN_PHILOSOPHY,
        "release_stages": RELEASE_STAGES,
        "architecture_layers": ARCHITECTURE_LAYERS,
    }


@router.get("/truth-doc")
def get_truth_doc():
    emit("truth_doc_viewed", EventCategory.ACTION, feature_id="FEAT-SYSTEM")
    return {
        "status": "ok",
        "version": TRUTH_DOC["version"],
        "last_updated": TRUTH_DOC["last_updated"],
        "total_features": len(TRUTH_DOC["features"]),
        "features": TRUTH_DOC["features"],
    }


@router.get("/truth-doc/{feature_id}")
def get_feature_spec(feature_id: str):
    feature = next(
        (f for f in TRUTH_DOC["features"] if f["id"] == feature_id),
        None,
    )
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found in Truth Doc")
    return {"status": "ok", "feature": feature}


@router.get("/architecture")
def get_architecture():
    return {
        "status": "ok",
        "layers": ARCHITECTURE_LAYERS,
        "rule": "UI → App Logic → Services → Data. No layer may skip.",
    }


@router.get("/dod")
def get_definition_of_done():
    features = TRUTH_DOC["features"]
    summary = {
        "checklist": DESIGN_PHILOSOPHY["definition_of_done"],
        "total_features": len(features),
        "fully_passing": 0,
        "features": [],
    }

    for f in features:
        dod = f.get("dod_status", {})
        checks_passed = sum(1 for v in dod.values() if v is True)
        total_checks = len(dod)
        is_fully_passing = checks_passed == total_checks

        if is_fully_passing:
            summary["fully_passing"] += 1

        summary["features"].append({
            "id": f["id"],
            "name": f["name"],
            "release_stage": f["release_stage"],
            "checks_passed": checks_passed,
            "total_checks": total_checks,
            "passing": is_fully_passing,
            "details": dod,
        })

    return {"status": "ok", **summary}


@router.get("/pipeline")
def get_release_pipeline():
    features = TRUTH_DOC["features"]
    pipeline = {}

    for stage_id, stage_def in RELEASE_STAGES.items():
        stage_features = [f for f in features if f["release_stage"] == stage_id]
        pipeline[stage_id] = {
            **stage_def,
            "feature_count": len(stage_features),
            "features": [{"id": f["id"], "name": f["name"]} for f in stage_features],
        }

    return {
        "status": "ok",
        "stages": pipeline,
        "total_features": len(features),
    }


@router.get("/refusal/summary")
def refusal_summary():
    return {"status": "ok", **get_failure_summary()}


@router.get("/refusal/events")
def refusal_events(limit: int = 50):
    return {"status": "ok", "events": get_refusal_events(limit)}


@router.get("/observability/health")
def obs_health():
    return {"status": "ok", **get_health_summary()}


@router.get("/observability/events")
def obs_events(limit: int = 100, category: Optional[str] = None, level: Optional[str] = None):
    return {"status": "ok", "events": get_obs_events(limit, category, level)}


@router.get("/observability/crashes")
def obs_crashes(limit: int = 20):
    return {"status": "ok", "crashes": get_crash_reports(limit)}


@router.get("/observability/counters")
def obs_counters():
    return {"status": "ok", "counters": get_counters()}


@router.post("/validate")
def eng_validate(payload: ProjectSpec, autofill: bool = False):
    project = autofill_minimums(payload) if autofill else payload
    return validate_project(project).model_dump()


@router.get("/validate/schema")
def eng_validate_schema():
    return {
        "domains": ["materials", "robotics", "bio", "energy", "crypto"],
        "lab_domains": DOMAINS,
        "size_classes": ["micro", "handheld", "desktop", "room", "building"],
        "energy_sources": ["none", "battery", "wall", "solar", "other"],
        "tolerance_levels": ["loose", "normal", "tight"],
        "tiers": {
            1: "Conceptual Sandbox",
            2: "Prototype Ready",
            3: "Engineering Track",
            4: "Speculative / Blocked",
        },
    }


@router.get("/domains")
def eng_domains():
    return {"domains": DOMAINS}


@router.get("/domains/{domain}")
def eng_domain_pack(domain: str):
    if domain not in DOMAINS:
        raise HTTPException(status_code=404, detail=f"Unknown domain: {domain}. Available: {DOMAINS}")
    return domain_pack(domain)


@router.post("/suggest")
def eng_suggest(domain: str, title: str):
    if domain not in DOMAINS:
        raise HTTPException(status_code=404, detail=f"Unknown domain: {domain}. Available: {DOMAINS}")
    return build_minimum_build_card(domain=domain, title=title)


@router.post("/suggest-and-validate")
def eng_suggest_and_validate(domain: str, title: str, autofill: bool = True):
    if domain not in DOMAINS:
        raise HTTPException(status_code=404, detail=f"Unknown domain: {domain}. Available: {DOMAINS}")
    card = build_minimum_build_card(domain=domain, title=title)

    spec = ProjectSpec(**{
        "title": card["title"],
        "domain": card["domain"],
        "scale": card["scale"],
        "energy": card["energy"],
        "material": card["material"],
        "fabrication": card["fabrication"],
        "physics": card["physics"],
    })

    spec = autofill_minimums(spec) if autofill else spec
    report = validate_project(spec)

    return {
        "minimum_build_card": card,
        "validation_report": report.model_dump(),
    }


from pydantic import BaseModel as _BaseModel

class TextIntakePayload(_BaseModel):
    text: str

@router.post("/convert-from-text")
def eng_convert_from_text(payload: TextIntakePayload, autofill: bool = True):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required.")

    domain, meta = detect_domain(text)
    title = extract_title(text)

    card = build_minimum_build_card(domain=domain, title=title)

    overrides = detect_overrides(text)
    card = apply_overrides(card, overrides)
    card = attach_user_constraints(card, text)

    spec = ProjectSpec(**{
        "title": card["title"],
        "domain": card["domain"],
        "scale": card["scale"],
        "energy": card["energy"],
        "material": card["material"],
        "fabrication": card["fabrication"],
        "physics": card["physics"],
    })

    spec = autofill_minimums(spec) if autofill else spec
    report = validate_project(spec)

    return {
        "intake": meta,
        "minimum_build_card": card,
        "validation_report": report.model_dump(),
    }


@router.post("/convert-batch")
def eng_convert_batch(payload: TextIntakePayload, autofill: bool = True):
    raw_text = payload.text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Text is required.")

    blocks = split_into_projects(raw_text)
    results = []

    for block in blocks:
        domain, meta = detect_domain(block)
        title = extract_title(block)

        card = build_minimum_build_card(domain=domain, title=title)

        overrides = detect_overrides(block)
        card = apply_overrides(card, overrides)
        card = attach_user_constraints(card, block)

        spec = ProjectSpec(**{
            "title": card["title"],
            "domain": card["domain"],
            "scale": card["scale"],
            "energy": card["energy"],
            "material": card["material"],
            "fabrication": card["fabrication"],
            "physics": card["physics"],
        })

        spec = autofill_minimums(spec) if autofill else spec
        report = validate_project(spec)

        results.append({
            "input_text": block,
            "intake": meta,
            "minimum_build_card": card,
            "validation_report": report.model_dump(),
        })

    return {
        "count": len(results),
        "items": results,
    }


from .project_domain_map import get_project_domain, get_project_domain_info, get_all_mappings, get_domain_projects

@router.get("/project-domains")
def eng_project_domains():
    return {"mappings": get_all_mappings()}


@router.get("/project-domain/{project_id}")
def eng_project_domain(project_id: str):
    info = get_project_domain_info(project_id)
    if not info:
        return {"project_id": project_id, "domain": None, "rationale": None}
    return {"project_id": project_id, **info}


@router.post("/validate-project/{project_id}")
def eng_validate_research_project(project_id: str, persona: str = "ajani"):
    from atlas_core_new.db.session import SessionLocal
    from atlas_core_new.db.models import ResearchTracker, ResearchActivityLog
    from datetime import datetime

    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="Database not available.")

    db = SessionLocal()
    try:
        project = db.query(ResearchTracker).filter(
            ResearchTracker.project_id == project_id,
            ResearchTracker.persona == persona,
        ).first()

        if not project:
            project = db.query(ResearchTracker).filter(
                ResearchTracker.project_id == project_id,
            ).first()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

        domain_map_entry = get_project_domain_info(project_id) or {}
        domain = domain_map_entry.get("domain")
        if not domain:
            domain_info = detect_domain(project.project_name or project.codename or project_id)
            domain = domain_info[0]

        card = build_minimum_build_card(domain=domain, title=project.project_name or project.codename)

        project_overrides = domain_map_entry.get("overrides", {})
        if project_overrides:
            card = apply_overrides(card, project_overrides)

        design_notes = domain_map_entry.get("design_notes")
        if design_notes:
            card.setdefault("intake_notes", [])
            if isinstance(card["intake_notes"], list):
                card["intake_notes"].insert(0, design_notes)

        spec = ProjectSpec(**{
            "title": card["title"],
            "domain": card["domain"],
            "scale": card["scale"],
            "energy": card["energy"],
            "material": card["material"],
            "fabrication": card["fabrication"],
            "physics": card["physics"],
        })

        spec = autofill_minimums(spec)
        report = validate_project(spec)
        report_dict = report.model_dump()

        tier = report_dict["tier"]
        checks = report_dict.get("checks", [])
        checks_passed = sum(1 for c in checks if c.get("status") == "PASS")
        total_checks = len(checks)

        validation_data = {
            "scale_check": {"pass": False, "findings": ""},
            "energy_check": {"pass": False, "findings": ""},
            "material_check": {"pass": False, "findings": ""},
            "fabrication_check": {"pass": False, "findings": ""},
            "physics_check": {"pass": False, "findings": ""},
            "feasibility_tier": tier,
            "checks_passed": checks_passed,
            "total_checks": total_checks,
            "all_checks_passed": checks_passed == total_checks,
            "validated_at": datetime.utcnow().isoformat(),
            "domain": domain,
            "domain_rationale": (get_project_domain_info(project_id) or {}).get("rationale", "Auto-detected"),
            "tier_justification": report_dict.get("completion", ""),
            "critical_blockers": report_dict.get("blockers", []),
            "recommendations": report_dict.get("recommendations", []),
            "missing_fields": report_dict.get("missing_fields", []),
            "overall_score": report_dict.get("overall_score", 0),
            "build_card": card,
        }

        check_name_map = {
            "Scale": "scale_check",
            "Energy": "energy_check",
            "Material": "material_check",
            "Fabrication": "fabrication_check",
            "Physics": "physics_check",
        }
        for check in checks:
            key = check_name_map.get(check["name"])
            if key:
                validation_data[key] = {
                    "pass": check["status"] == "PASS",
                    "status": check["status"],
                    "score": check["score"],
                    "findings": "; ".join(check.get("notes", [])) or f"{check['name']} check: {check['status']}",
                    "issues": check.get("notes", []) if check["status"] != "PASS" else [],
                }

        project.engineering_validation = validation_data
        project.feasibility_tier = tier
        project.validation_status = "passed" if checks_passed == total_checks else "issues_found"
        project.last_validated_at = datetime.utcnow()

        tier_labels = {1: "Conceptual Sandbox", 2: "Prototype Ready", 3: "Engineering Track", 4: "Speculative / Blocked"}
        tier_label = tier_labels.get(tier, "Unknown")

        db.add(ResearchActivityLog(
            persona=project.persona,
            project_id=project_id,
            activity_type="engineering_validation",
            title=f"Domain Validation: {domain} — Tier {tier} ({tier_label})",
            description=(
                f"Domain: {domain}. Checks: {checks_passed}/{total_checks}. "
                f"Tier: {tier} ({tier_label}). Score: {report_dict.get('overall_score', 0):.0%}"
            ),
        ))

        db.commit()

        return {
            "status": "ok",
            "project_id": project_id,
            "persona": project.persona,
            "domain": domain,
            "feasibility_tier": tier,
            "tier_name": tier_label,
            "checks_passed": checks_passed,
            "total_checks": total_checks,
            "all_checks_passed": checks_passed == total_checks,
            "overall_score": report_dict.get("overall_score", 0),
            "validation": validation_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/validate-all-projects")
def eng_validate_all_projects():
    from atlas_core_new.db.session import SessionLocal
    from atlas_core_new.db.models import ResearchTracker
    from datetime import datetime

    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="Database not available.")

    db = SessionLocal()
    try:
        projects = db.query(ResearchTracker).filter(ResearchTracker.is_active == True).all()
        results = []
        for project in projects:
            try:
                domain_map_entry = get_project_domain_info(project.project_id) or {}
                domain = domain_map_entry.get("domain")
                if not domain:
                    domain_info = detect_domain(project.project_name or project.codename or project.project_id)
                    domain = domain_info[0]

                card = build_minimum_build_card(domain=domain, title=project.project_name or project.codename)
                proj_overrides = domain_map_entry.get("overrides", {})
                if proj_overrides:
                    card = apply_overrides(card, proj_overrides)

                spec = ProjectSpec(**{
                    "title": card["title"],
                    "domain": card["domain"],
                    "scale": card["scale"],
                    "energy": card["energy"],
                    "material": card["material"],
                    "fabrication": card["fabrication"],
                    "physics": card["physics"],
                })
                spec = autofill_minimums(spec)
                report = validate_project(spec)
                report_dict = report.model_dump()

                tier = report_dict["tier"]
                checks = report_dict.get("checks", [])
                checks_passed = sum(1 for c in checks if c.get("status") == "PASS")
                total_checks = len(checks)

                validation_data = {
                    "feasibility_tier": tier,
                    "checks_passed": checks_passed,
                    "total_checks": total_checks,
                    "all_checks_passed": checks_passed == total_checks,
                    "validated_at": datetime.utcnow().isoformat(),
                    "domain": domain,
                    "overall_score": report_dict.get("overall_score", 0),
                    "tier_justification": report_dict.get("completion", ""),
                    "critical_blockers": report_dict.get("blockers", []),
                    "recommendations": report_dict.get("recommendations", []),
                }

                check_name_map = {"Scale": "scale_check", "Energy": "energy_check", "Material": "material_check", "Fabrication": "fabrication_check", "Physics": "physics_check"}
                for check in checks:
                    key = check_name_map.get(check["name"])
                    if key:
                        validation_data[key] = {
                            "pass": check["status"] == "PASS",
                            "status": check["status"],
                            "score": check["score"],
                            "findings": "; ".join(check.get("notes", [])) or f"{check['name']}: {check['status']}",
                            "issues": check.get("notes", []) if check["status"] != "PASS" else [],
                        }

                project.engineering_validation = validation_data
                project.feasibility_tier = tier
                project.validation_status = "passed" if checks_passed == total_checks else "issues_found"
                project.last_validated_at = datetime.utcnow()

                results.append({"project_id": project.project_id, "persona": project.persona, "domain": domain, "tier": tier, "checks": f"{checks_passed}/{total_checks}", "status": "ok"})
            except Exception as e:
                results.append({"project_id": project.project_id, "persona": project.persona, "status": "error", "error": str(e)})

        db.commit()
        return {"status": "ok", "validated": len(results), "results": results}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
