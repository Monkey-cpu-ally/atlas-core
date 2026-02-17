from __future__ import annotations

import os
import json
import re
import uuid
import zipfile
from datetime import datetime
from typing import List, Dict, Optional, Any

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from .schemas import BlueprintPacket
from .validation import validate_packet

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

router = APIRouter(prefix="/atlas", tags=["Atlas Storage"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_ROOT = os.path.join(BASE_DIR, "blueprint_engine", "atlas_storage", "ATLAS_BLUEPRINTS")
os.makedirs(STORAGE_ROOT, exist_ok=True)


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "project"


def now_z() -> str:
    return datetime.utcnow().isoformat() + "Z"


def project_dir(project_slug: str, version: str) -> str:
    vslug = "v" + re.sub(r"[^0-9a-zA-Z]+", "_", version).strip("_")
    return os.path.join(STORAGE_ROOT, project_slug, vslug)


def ensure_project_folders(pdir: str) -> Dict[str, str]:
    paths = {
        "root": pdir,
        "cad": os.path.join(pdir, "cad"),
        "renders": os.path.join(pdir, "renders"),
        "manual": os.path.join(pdir, "manual"),
        "testing": os.path.join(pdir, "testing"),
    }
    for p in paths.values():
        os.makedirs(p, exist_ok=True)
    return paths


def write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_steps_images(renders_dir: str) -> List[str]:
    if not os.path.exists(renders_dir):
        return []
    files = [fn for fn in os.listdir(renders_dir) if fn.lower().endswith((".png", ".jpg", ".jpeg"))]

    def key(fn: str):
        m = re.search(r"(\d+)", fn)
        return int(m.group(1)) if m else 10**9

    return [os.path.join(renders_dir, f) for f in sorted(files, key=key)]


def draw_wrapped_text(c_obj: canvas.Canvas, text: str, x: float, y: float, max_width: float, leading: float = 12):
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c_obj.stringWidth(test, "Helvetica", 10) <= max_width:
            line = test
        else:
            c_obj.setFont("Helvetica", 10)
            c_obj.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c_obj.setFont("Helvetica", 10)
        c_obj.drawString(x, y, line)
        y -= leading
    return y


def generate_manual_pdf(packet: BlueprintPacket, ppaths: Dict[str, str]) -> str:
    renders_dir = ppaths["renders"]
    manual_dir = ppaths["manual"]
    step_images = list_steps_images(renders_dir)

    pdf_path = os.path.join(manual_dir, f"{slugify(packet.title)}_{packet.version}_manual.pdf")

    c_obj = canvas.Canvas(pdf_path, pagesize=letter)
    W, H = letter

    c_obj.setFont("Helvetica-Bold", 20)
    c_obj.drawString(1 * inch, H - 1.2 * inch, packet.title)

    c_obj.setFont("Helvetica", 12)
    c_obj.drawString(1 * inch, H - 1.6 * inch, f"Version: {packet.version}")
    c_obj.drawString(1 * inch, H - 1.85 * inch, f"Domain: {packet.domain} | Safety Tier: {packet.safety_tier}")
    c_obj.drawString(1 * inch, H - 2.1 * inch, f"Created: {packet.created_at}")

    c_obj.setFont("Helvetica-Bold", 14)
    c_obj.drawString(1 * inch, H - 2.7 * inch, "What it does (6th-grade):")
    y = H - 3.0 * inch
    y = draw_wrapped_text(c_obj, packet.objective, 1 * inch, y, W - 2 * inch)

    c_obj.setFont("Helvetica-Bold", 14)
    c_obj.drawString(1 * inch, y - 0.3 * inch, "Rules / Assumptions:")
    y -= 0.6 * inch
    for a in packet.assumptions[:8]:
        y = draw_wrapped_text(c_obj, f"- {a}", 1 * inch, y, W - 2 * inch, leading=12)
        if y < 1.2 * inch:
            break

    c_obj.showPage()

    c_obj.setFont("Helvetica-Bold", 16)
    c_obj.drawString(1 * inch, H - 1.0 * inch, "System Overview")

    c_obj.setFont("Helvetica-Bold", 12)
    c_obj.drawString(1 * inch, H - 1.45 * inch, "Modules:")
    y = H - 1.7 * inch
    c_obj.setFont("Helvetica", 10)
    for m in packet.architecture[:10]:
        y = draw_wrapped_text(c_obj, f"- {m.name}: {m.purpose}", 1 * inch, y, W - 2 * inch, leading=12)
        if y < 4.8 * inch:
            break

    c_obj.setFont("Helvetica-Bold", 12)
    c_obj.drawString(1 * inch, 4.55 * inch, "Materials (top picks):")
    y2 = 4.3 * inch
    c_obj.setFont("Helvetica", 10)
    for ms in packet.materials[:6]:
        y2 = draw_wrapped_text(c_obj, f"- {ms.name} — {ms.use}", 1 * inch, y2, W - 2 * inch, leading=12)
        if y2 < 2.6 * inch:
            break

    c_obj.setFont("Helvetica-Bold", 12)
    c_obj.drawString(1 * inch, 2.45 * inch, "Tools:")
    y3 = 2.2 * inch
    c_obj.setFont("Helvetica", 10)
    for t in packet.tools[:8]:
        y3 = draw_wrapped_text(c_obj, f"- {t.name}: {t.purpose}", 1 * inch, y3, W - 2 * inch, leading=12)
        if y3 < 0.9 * inch:
            break

    c_obj.showPage()

    step_map = {s.step: s for s in packet.fabrication_steps}

    for idx, img_path in enumerate(step_images, start=1):
        step_obj = step_map.get(idx)

        c_obj.setFont("Helvetica-Bold", 16)
        title = step_obj.title if step_obj else f"Assembly Step {idx}"
        c_obj.drawString(1 * inch, H - 1.0 * inch, f"STEP {idx} — {title}")

        img_x = 1 * inch
        img_y = 3.0 * inch
        img_w = 4.1 * inch
        img_h = 5.3 * inch

        try:
            img = ImageReader(img_path)
            c_obj.rect(img_x, img_y, img_w, img_h)
            c_obj.drawImage(img, img_x + 6, img_y + 6, img_w - 12, img_h - 12,
                            preserveAspectRatio=True, anchor='c', mask='auto')
        except Exception:
            c_obj.rect(img_x, img_y, img_w, img_h)
            c_obj.setFont("Helvetica", 10)
            c_obj.drawString(img_x + 10, img_y + img_h - 20, "Image load failed")

        panel_x = 5.3 * inch
        panel_y_top = H - 1.45 * inch
        panel_w = W - panel_x - 1 * inch

        c_obj.setFont("Helvetica-Bold", 12)
        c_obj.drawString(panel_x, panel_y_top, "Add These (guide):")
        y = panel_y_top - 0.25 * inch
        c_obj.setFont("Helvetica", 10)

        for comp in packet.components[:6]:
            y = draw_wrapped_text(c_obj, f"- {comp.qty}x {comp.name} ({comp.role})", panel_x, y, panel_w, leading=12)
            if y < 4.0 * inch:
                break

        c_obj.setFont("Helvetica-Bold", 12)
        c_obj.drawString(1 * inch, 2.6 * inch, "Do This:")
        y = 2.35 * inch
        c_obj.setFont("Helvetica", 10)
        if step_obj:
            for ins in step_obj.instructions[:6]:
                y = draw_wrapped_text(c_obj, f"- {ins}", 1 * inch, y, W - 2 * inch, leading=12)
                if y < 1.35 * inch:
                    break
        else:
            y = draw_wrapped_text(c_obj, "- Follow the picture and attach the part shown.", 1 * inch, y, W - 2 * inch, leading=12)

        c_obj.setFont("Helvetica-Bold", 12)
        c_obj.drawString(1 * inch, 1.25 * inch, "Check It:")
        y = 1.0 * inch
        c_obj.setFont("Helvetica", 10)
        if step_obj:
            for ver in step_obj.verification[:3]:
                y = draw_wrapped_text(c_obj, f"- {ver}", 1 * inch, y, W - 2 * inch, leading=12)
        else:
            draw_wrapped_text(c_obj, "- It should fit cleanly and move smoothly (no rubbing).", 1 * inch, y, W - 2 * inch, leading=12)

        c_obj.showPage()

    c_obj.setFont("Helvetica-Bold", 16)
    c_obj.drawString(1 * inch, H - 1.0 * inch, "Testing + Common Failures")

    c_obj.setFont("Helvetica-Bold", 12)
    c_obj.drawString(1 * inch, H - 1.5 * inch, "Test Plan:")
    y = H - 1.75 * inch
    c_obj.setFont("Helvetica", 10)
    for t in packet.test_plan:
        y = draw_wrapped_text(c_obj, f"- {t}", 1 * inch, y, W - 2 * inch, leading=12)
        if y < 4.2 * inch:
            break

    c_obj.setFont("Helvetica-Bold", 12)
    c_obj.drawString(1 * inch, 4.0 * inch, "Failure Modes + Fixes:")
    y = 3.75 * inch
    c_obj.setFont("Helvetica", 10)
    for fm in packet.failure_modes[:6]:
        y = draw_wrapped_text(c_obj, f"- {fm.mode} (sev: {fm.severity})", 1 * inch, y, W - 2 * inch, leading=12)
        y = draw_wrapped_text(c_obj, f"  Cause: {fm.cause}", 1.2 * inch, y, W - 2.2 * inch, leading=12)
        y = draw_wrapped_text(c_obj, f"  Fix: {fm.mitigation}", 1.2 * inch, y, W - 2.2 * inch, leading=12)
        y -= 6
        if y < 1.1 * inch:
            break

    c_obj.save()
    return pdf_path


@router.post("/projects")
def create_project(packet: BlueprintPacket):
    if not packet.blueprint_id:
        packet.blueprint_id = str(uuid.uuid4())
    if not packet.created_at:
        packet.created_at = now_z()

    issues = validate_packet(packet)
    ok = len(issues) == 0

    proj_slug = slugify(packet.title)
    pdir = project_dir(proj_slug, packet.version)
    paths = ensure_project_folders(pdir)

    project_json_path = os.path.join(paths["root"], "project.json")
    write_json(project_json_path, packet.model_dump())

    validation_path = os.path.join(paths["root"], "validation.json")
    write_json(validation_path, {"ok": ok, "issues": issues})

    bom_path = os.path.join(paths["root"], "bom.csv")
    with open(bom_path, "w", encoding="utf-8") as f:
        f.write("name,qty,role,notes\n")
        for comp in packet.components:
            notes_clean = (comp.notes or "").replace(",", ";")
            f.write(f"{comp.name},{comp.qty},{comp.role},{notes_clean}\n")
        for mat in packet.materials:
            f.write(f"{mat.name},1,{mat.use},{mat.justification.replace(',', ';')}\n")

    return {
        "status": "stored",
        "project_slug": proj_slug,
        "version_folder": os.path.basename(paths["root"]),
        "paths": {
            "project_json": f"/atlas/projects/{proj_slug}/{os.path.basename(paths['root'])}",
            "renders_dir": f"/atlas/projects/{proj_slug}/{os.path.basename(paths['root'])}/renders",
            "manual_dir": f"/atlas/projects/{proj_slug}/{os.path.basename(paths['root'])}/manual",
        },
        "validation": {"ok": ok, "issues": issues}
    }


@router.post("/projects/{project_slug}/{version}/renders")
async def upload_renders(project_slug: str, version: str, files: List[UploadFile] = File(...)):
    pdir = project_dir(project_slug, version)
    paths = ensure_project_folders(pdir)

    saved = []
    for f in files:
        fn = os.path.basename(f.filename or "unknown.png")
        if not fn.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        out = os.path.join(paths["renders"], fn)
        with open(out, "wb") as w:
            w.write(await f.read())
        saved.append(fn)

    if not saved:
        raise HTTPException(status_code=400, detail="No valid image files uploaded (.png/.jpg/.jpeg).")

    return {"status": "ok", "saved": sorted(saved)}


@router.post("/projects/{project_slug}/{version}/manual")
def build_manual(project_slug: str, version: str):
    pdir = project_dir(project_slug, version)
    paths = ensure_project_folders(pdir)

    project_json = os.path.join(paths["root"], "project.json")
    if not os.path.exists(project_json):
        raise HTTPException(status_code=404, detail="project.json not found. Create project first.")

    packet = BlueprintPacket(**read_json(project_json))

    pdf_path = generate_manual_pdf(packet, paths)
    return {"status": "ok", "pdf_path": f"/atlas/projects/{project_slug}/{os.path.basename(paths['root'])}/manual.pdf"}


@router.get("/projects/{project_slug}/{version}/manual.pdf")
def download_manual(project_slug: str, version: str):
    pdir = project_dir(project_slug, version)
    paths = ensure_project_folders(pdir)
    pdfs = [f for f in os.listdir(paths["manual"]) if f.lower().endswith(".pdf")]
    if not pdfs:
        raise HTTPException(status_code=404, detail="No manual PDF found. Generate it first.")
    pdfs.sort()
    pdf_path = os.path.join(paths["manual"], pdfs[-1])
    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))


@router.get("/projects/{project_slug}/{version}/export.zip")
def export_zip(project_slug: str, version: str):
    pdir = project_dir(project_slug, version)
    if not os.path.exists(pdir):
        raise HTTPException(status_code=404, detail="Project version folder not found.")

    vslug = "v" + re.sub(r"[^0-9a-zA-Z]+", "_", version).strip("_")
    zip_name = f"{project_slug}_{vslug}_atlas_bundle.zip"
    zip_path = os.path.join(os.path.dirname(pdir), zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, file_list in os.walk(pdir):
            for fn in file_list:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, os.path.dirname(pdir))
                z.write(full, rel)

    return FileResponse(zip_path, media_type="application/zip", filename=zip_name)


@router.get("/projects")
def list_all_projects():
    if not os.path.exists(STORAGE_ROOT):
        return {"projects": []}
    projects = []
    for proj in sorted(os.listdir(STORAGE_ROOT)):
        proj_path = os.path.join(STORAGE_ROOT, proj)
        if not os.path.isdir(proj_path):
            continue
        versions = []
        for v in sorted(os.listdir(proj_path)):
            vpath = os.path.join(proj_path, v)
            if os.path.isdir(vpath):
                pjson = os.path.join(vpath, "project.json")
                has_renders = len(list_steps_images(os.path.join(vpath, "renders"))) > 0
                has_manual = any(f.endswith(".pdf") for f in os.listdir(os.path.join(vpath, "manual")) if os.path.exists(os.path.join(vpath, "manual")))
                meta = {}
                if os.path.exists(pjson):
                    try:
                        data = read_json(pjson)
                        meta = {"title": data.get("title", ""), "domain": data.get("domain", ""), "safety_tier": data.get("safety_tier", "")}
                    except Exception:
                        pass
                versions.append({"version": v, "has_renders": has_renders, "has_manual": has_manual, **meta})
        if versions:
            projects.append({"project_slug": proj, "versions": versions})
    return {"projects": projects}


@router.get("/projects/{project_slug}/{version}")
def get_project_detail(project_slug: str, version: str):
    pdir = project_dir(project_slug, version)
    paths = ensure_project_folders(pdir)

    pjson = os.path.join(paths["root"], "project.json")
    if not os.path.exists(pjson):
        raise HTTPException(status_code=404, detail="Project not found.")

    packet_data = read_json(pjson)
    renders = list_steps_images(paths["renders"])
    render_names = [os.path.basename(r) for r in renders]

    pdfs = [f for f in os.listdir(paths["manual"]) if f.lower().endswith(".pdf")]

    return {
        "packet": packet_data,
        "renders": render_names,
        "has_manual": len(pdfs) > 0,
        "render_count": len(renders),
    }
