"""
Dragon-Scale Forge (Web Canvas + Local Processing)
---------------------------------------------------
A creative tool for sketching and processing artwork through:
- Canvas drawing interface
- Clean → Remix → Polish → Export pipeline
- Hermes-style capability tokens
- Capsule-based project tracking
- Multiple style packs and fidelity levels
- High-resolution export (4K-12K)

Run standalone:
  uvicorn atlas_core_new.tools.dragon_scale_forge:app --reload --port 5001
"""

from __future__ import annotations

import base64
import io
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal, Tuple
from uuid import uuid4

import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from itsdangerous import TimestampSigner, BadSignature

# ============================================================
# CONFIG
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "ds_data"
CAPSULES_DIR = DATA_DIR / "capsules"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
AUDIT_DIR = DATA_DIR / "audit"
TOKENS_DIR = DATA_DIR / "tokens"

for d in (DATA_DIR, CAPSULES_DIR, ARTIFACTS_DIR, AUDIT_DIR, TOKENS_DIR):
    d.mkdir(parents=True, exist_ok=True)

DEFAULT_MAX_FIDELITY_AI = 40
HUMAN_REQUIRED_OVER = 50

TIERS: Dict[str, Tuple[int, int]] = {
    "4K": (3840, 2160),
    "6K": (6016, 3384),
    "8K": (7680, 4320),
    "10K": (10240, 5760),
    "12K": (12288, 6912),
}

DS_VERSION = "dragon-scale-1.0"
SIGNER = TimestampSigner(os.environ.get("DS_HERMES_SECRET", "dragon-scale-hermes-dev-secret"))


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# ============================================================
# HERMES: Capability Tokens + Audit
# ============================================================
@dataclass
class TokenConstraints:
    max_fidelity: int = DEFAULT_MAX_FIDELITY_AI
    allowed_style_packs: List[str] = None  # if None/empty => allow all


@dataclass
class CapabilityToken:
    token_id: str
    issued_to: str
    capabilities: List[str]
    scope: Literal["LOCAL_ONLY", "CLOUD_OK"]
    exp_ts: str
    constraints: TokenConstraints


def issue_token(
    issued_to: str,
    capabilities: List[str],
    scope: str = "LOCAL_ONLY",
    minutes: int = 60,
    max_fidelity: int = DEFAULT_MAX_FIDELITY_AI,
    allowed_style_packs: Optional[List[str]] = None,
) -> str:
    token_id = new_id("tok")
    exp_ts = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()
    tok = CapabilityToken(
        token_id=token_id,
        issued_to=issued_to,
        capabilities=capabilities,
        scope=scope,  # type: ignore
        exp_ts=exp_ts,
        constraints=TokenConstraints(
            max_fidelity=int(max_fidelity),
            allowed_style_packs=allowed_style_packs or [],
        ),
    )
    write_json(TOKENS_DIR / f"{token_id}.json", {
        "token_id": tok.token_id,
        "issued_to": tok.issued_to,
        "capabilities": tok.capabilities,
        "scope": tok.scope,
        "exp_ts": tok.exp_ts,
        "constraints": {
            "max_fidelity": tok.constraints.max_fidelity,
            "allowed_style_packs": tok.constraints.allowed_style_packs,
        }
    })
    signed = SIGNER.sign(token_id.encode("utf-8")).decode("utf-8")
    return signed


def verify_token(signed_token: str) -> CapabilityToken:
    try:
        token_id = SIGNER.unsign(signed_token.encode("utf-8")).decode("utf-8")
    except BadSignature as e:
        raise PermissionError("Invalid capability token.") from e

    path = TOKENS_DIR / f"{token_id}.json"
    if not path.exists():
        raise PermissionError("Token not found.")

    data = read_json(path)
    exp_ts = datetime.fromisoformat(data["exp_ts"])
    if datetime.utcnow() > exp_ts:
        raise PermissionError("Token expired.")

    return CapabilityToken(
        token_id=data["token_id"],
        issued_to=data["issued_to"],
        capabilities=list(data["capabilities"]),
        scope=data["scope"],
        exp_ts=data["exp_ts"],
        constraints=TokenConstraints(
            max_fidelity=int(data["constraints"]["max_fidelity"]),
            allowed_style_packs=list(data["constraints"]["allowed_style_packs"] or []),
        ),
    )


def enforce(tok: CapabilityToken, cap: str) -> None:
    if cap not in tok.capabilities:
        raise PermissionError(f"Missing capability: {cap}")


def enforce_fidelity(tok: CapabilityToken, fidelity: int, caller: str) -> None:
    fidelity = int(fidelity)
    if fidelity > tok.constraints.max_fidelity:
        raise PermissionError(f"Fidelity {fidelity} exceeds token max {tok.constraints.max_fidelity}")
    if caller in ("ajani", "minerva") and fidelity > DEFAULT_MAX_FIDELITY_AI:
        raise PermissionError("AI caller cannot exceed default max fidelity.")


def enforce_style(tok: CapabilityToken, style_id: str) -> None:
    allow = tok.constraints.allowed_style_packs or []
    if allow and style_id not in allow:
        raise PermissionError(f"Style '{style_id}' not allowed.")


def audit(event: Dict[str, Any]) -> str:
    audit_id = new_id("audit")
    event = {**event, "audit_id": audit_id, "ts": now_iso()}
    write_json(AUDIT_DIR / f"{audit_id}.json", event)
    return audit_id


# ============================================================
# IDEA CAPSULES (append-only)
# ============================================================
def capsule_path(capsule_id: str) -> Path:
    return CAPSULES_DIR / f"{capsule_id}.json"


def new_capsule(title: str, creator: str, intent_text: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
    cap = {
        "capsule_id": new_id("capsule"),
        "created_at": now_iso(),
        "creator": creator,
        "title": title,
        "intent_text": intent_text or None,
        "constraints": {
            "keep_silhouette": True,
            "lock_proportions": True,
            "forbid_new_shapes": False,
            "protected_regions": [],
        },
        "fidelity_policy": {
            "default_max_fidelity_ai": DEFAULT_MAX_FIDELITY_AI,
            "human_required_over": HUMAN_REQUIRED_OVER,
        },
        "inputs": {},
        "blueprint": None,
        "versions": [],
        "exports": [],
        "tags": tags or [],
    }
    write_json(capsule_path(cap["capsule_id"]), cap)
    return cap


def load_capsule(capsule_id: str) -> Dict[str, Any]:
    path = capsule_path(capsule_id)
    if not path.exists():
        raise FileNotFoundError("Capsule not found.")
    return read_json(path)


def save_capsule(cap: Dict[str, Any]) -> None:
    write_json(capsule_path(cap["capsule_id"]), cap)


def append_version(cap: Dict[str, Any], version: Dict[str, Any]) -> Dict[str, Any]:
    cap["versions"].append(version)
    save_capsule(cap)
    return cap


# ============================================================
# DRAGON-SCALE IMAGE OPS (Scale-I Local, fully usable)
# ============================================================
def pil_from_data_url(data_url: str) -> Image.Image:
    if "," not in data_url:
        raise ValueError("Invalid data URL.")
    header, b64 = data_url.split(",", 1)
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.alpha_composite(img)
    return bg.convert("RGB")


def to_cv(img: Image.Image) -> np.ndarray:
    arr = np.array(img)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def from_cv(arr_bgr: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(arr_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def extract_edges(img: Image.Image) -> Image.Image:
    arr = to_cv(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 60, 160)
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    inv = 255 - edges
    out = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)
    return from_cv(out)


def clean_line_art(edge_img: Image.Image, line_weight: float = 1.2) -> Image.Image:
    img = edge_img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=3))
    arr = np.array(img)
    _, thr = cv2.threshold(arr, 220, 255, cv2.THRESH_BINARY)

    if line_weight > 1.0:
        k = int(min(5, max(1, round((line_weight - 1.0) * 3 + 1))))
        kernel = np.ones((k, k), np.uint8)
        thr = cv2.erode(thr, kernel, iterations=1)

    return Image.fromarray(thr).convert("RGB")


def apply_style(img: Image.Image, style_id: str, intensity: float = 1.0) -> Image.Image:
    x = img.copy()

    if style_id == "blueprint.clean":
        x = x.filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=2))
        x = ImageEnhance.Contrast(x).enhance(1.25)
        r, g, b = x.split()
        b = ImageEnhance.Brightness(b).enhance(1.10)
        g = ImageEnhance.Brightness(g).enhance(1.03)
        x = Image.merge("RGB", (r, g, b))

    elif style_id == "cinematic.noir":
        x = ImageOps.grayscale(x).convert("RGB")
        x = ImageEnhance.Contrast(x).enhance(1.4)
        x = x.filter(ImageFilter.GaussianBlur(radius=0.6))
        x = x.filter(ImageFilter.UnsharpMask(radius=2, percent=220, threshold=4))

    elif style_id == "graffiti.ink":
        x = ImageEnhance.Contrast(x).enhance(1.3)
        x = ImageEnhance.Color(x).enhance(1.35)
        x = x.filter(ImageFilter.UnsharpMask(radius=1, percent=190, threshold=2))

    elif style_id == "anime.cel":
        arr = to_cv(x)
        arr = cv2.bilateralFilter(arr, d=9, sigmaColor=75, sigmaSpace=75)
        y = from_cv(arr)
        y = ImageOps.posterize(y, bits=4)
        y = y.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=2))
        x = y

    else:
        x = ImageEnhance.Contrast(x).enhance(1.1)

    intensity = float(max(0.0, min(1.0, intensity)))
    return Image.blend(img, x, alpha=intensity)


def upscale(img: Image.Image, tier: str) -> Image.Image:
    w, h = TIERS[tier]
    return img.resize((w, h), Image.Resampling.LANCZOS)


def save_artifact_image(img: Image.Image, folder: Path, name: str) -> str:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    img.save(path, "PNG")
    return str(path)


def artifact_dir(bundle_id: str) -> Path:
    d = ARTIFACTS_DIR / bundle_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================
# FASTAPI APP + WEB CANVAS UI
# ============================================================
app = FastAPI(title="Dragon-Scale Forge (Web Canvas, Local)")

INDEX_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Forge + Dragon-Scale (Web)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 0; background: #0b0b0f; color: #e8e8ee; }
    .wrap { display: grid; grid-template-columns: 1fr 360px; gap: 16px; padding: 16px; max-width: 1200px; margin: 0 auto; }
    .card { background: #12121a; border: 1px solid #222233; border-radius: 14px; padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
    canvas { width: 100%; height: 520px; background: #ffffff; border-radius: 12px; cursor: crosshair; }
    label { display:block; font-size: 12px; color: #b8b8c7; margin-top: 10px; }
    input, select, button, textarea { width: 100%; margin-top: 6px; padding: 10px; border-radius: 10px; border: 1px solid #2a2a3a; background: #0f0f16; color: #e8e8ee; }
    textarea { height: 80px; resize: vertical; }
    button { background: #2d5bff; border: 0; font-weight: 650; cursor: pointer; }
    button.secondary { background: #24243a; }
    button.danger { background: #a12b2b; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .small { font-size: 12px; color:#b8b8c7; }
    .outputs img { width: 100%; border-radius: 10px; border: 1px solid #2a2a3a; margin-top: 10px; }
    .pill { display:inline-block; padding: 4px 8px; border-radius: 999px; background:#1b1b2a; border:1px solid #2a2a3a; font-size:12px; color:#cfcfe6; }
    .hr { height:1px; background:#26263a; margin: 12px 0; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
        <div>
          <div style="font-size:18px; font-weight:800;">Forge Canvas</div>
          <div class="small">Sketch/paint → Clean → Remix → Polish → Export (Dragon-Scale organ)</div>
        </div>
        <span class="pill">Local Core</span>
      </div>

      <div class="hr"></div>

      <canvas id="c" width="2400" height="1500"></canvas>

      <div class="row" style="margin-top:12px;">
        <button class="secondary" onclick="clearCanvas()">Clear</button>
        <button class="danger" onclick="toggleEraser()">Eraser: <span id="eraserState">OFF</span></button>
      </div>

      <div class="row">
        <div>
          <label>Brush size</label>
          <input id="size" type="range" min="1" max="40" value="6" />
        </div>
        <div>
          <label>Color</label>
          <input id="color" type="color" value="#111111" />
        </div>
      </div>

      <div class="row">
        <div>
          <label>Brush preset</label>
          <select id="brushPreset">
            <option value="ink" selected>ink</option>
            <option value="pencil">pencil</option>
            <option value="paint">paint</option>
          </select>
        </div>
        <div>
          <label>Stabilizer (feel)</label>
          <input id="stab" type="range" min="0" max="0.9" step="0.01" value="0.55" />
        </div>
      </div>

      <label>Notes / Intent</label>
      <textarea id="intent" placeholder="Describe the idea you're sketching..."></textarea>

      <div class="row">
        <div>
          <label>Style pack</label>
          <select id="style">
            <option value="blueprint.clean">blueprint.clean</option>
            <option value="cinematic.noir">cinematic.noir</option>
            <option value="graffiti.ink">graffiti.ink</option>
            <option value="anime.cel">anime.cel</option>
          </select>
        </div>
        <div>
          <label>Fidelity (0–100)</label>
          <input id="fidelity" type="number" min="0" max="100" value="35" />
        </div>
      </div>

      <div class="row">
        <div>
          <label>Polish tier</label>
          <select id="tier">
            <option value="6K">6K</option>
            <option value="8K" selected>8K</option>
            <option value="10K">10K</option>
            <option value="12K">12K</option>
          </select>
        </div>
        <div>
          <label>Variants</label>
          <input id="variants" type="number" min="1" max="9" value="4" />
        </div>
      </div>

      <div class="row" style="margin-top:12px;">
        <button onclick="runAll()">Run ALL (Clean → Remix → Polish → Export)</button>
        <button class="secondary" onclick="makeCapsule()">New Capsule</button>
      </div>

      <div class="small" style="margin-top:10px;">
        Capsule: <span class="pill" id="capsuleId">none</span> &nbsp; Token: <span class="pill" id="tokenState">none</span>
      </div>
    </div>

    <div class="card">
      <div style="font-size:18px; font-weight:800;">Outputs</div>
      <div class="small">Your results (download links appear below)</div>
      <div class="hr"></div>
      <div id="status" class="small">Ready.</div>
      <div class="outputs" id="outputs"></div>
    </div>
  </div>

<script>
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d", { desynchronized: true });

/* ==============================
   Dragon-Scale Stroke Engine v1
   ============================== */

ctx.lineCap = "round";
ctx.lineJoin = "round";

function fillWhite() {
  ctx.save();
  ctx.globalCompositeOperation = "source-over";
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.restore();
}
fillWhite();

let eraser = false;
let drawing = false;

const BRUSHES = {
  pencil: { baseSize: 3.5, alpha: 0.55, hardness: 0.85, jitter: 0.15 },
  ink:    { baseSize: 5.5, alpha: 0.95, hardness: 1.00, jitter: 0.04 },
  paint:  { baseSize: 11.0, alpha: 0.35, hardness: 0.55, jitter: 0.18 }
};

let brushMode = "ink";
let points = [];
let lastT = 0;

let stabilizer = 0.55;
let velStabilizer = 0.40;
let minDistance = 0.6;
let maxPoints = 64;
let prediction = 0.15;

function clearCanvas() {
  fillWhite();
}

function toggleEraser() {
  eraser = !eraser;
  document.getElementById("eraserState").innerText = eraser ? "ON" : "OFF";
}

function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }

function pos(e) {
  const r = canvas.getBoundingClientRect();
  const x = (e.clientX - r.left) * (canvas.width / r.width);
  const y = (e.clientY - r.top) * (canvas.height / r.height);
  return { x, y };
}

function dist(a,b){
  const dx = a.x-b.x, dy=a.y-b.y;
  return Math.hypot(dx,dy);
}

function lerp(a,b,t){ return a + (b-a)*t; }

function smoothPoint(prev, cur, alpha){
  return {
    x: lerp(prev.x, cur.x, alpha),
    y: lerp(prev.y, cur.y, alpha),
    p: lerp(prev.p, cur.p, alpha),
    t: cur.t
  };
}

function addPoint(raw) {
  const t = raw.t;
  if (points.length === 0) {
    points.push(raw);
    return;
  }

  const last = points[points.length - 1];
  if (dist(last, raw) < minDistance) return;

  const dt = Math.max(1, t - last.t);
  const v = dist(last, raw) / dt;

  const vBoost = clamp(v * 0.020, 0, 0.35);
  const s = clamp(stabilizer + vBoost * velStabilizer, 0.05, 0.92);

  const alpha = 1.0 - s;

  const p = clamp(raw.p, 0.1, 1.0);
  const smoothed = smoothPoint(last, { ...raw, p }, alpha);

  const dx = smoothed.x - last.x;
  const dy = smoothed.y - last.y;
  smoothed.x += dx * prediction;
  smoothed.y += dy * prediction;

  points.push(smoothed);
  if (points.length > maxPoints) points.shift();
}

function drawStroke(color, sizeMul) {
  if (points.length < 2) return;

  const brush = BRUSHES[brushMode] || BRUSHES.ink;
  const baseSize = brush.baseSize * sizeMul;
  const baseAlpha = brush.alpha;
  const jitter = brush.jitter;

  ctx.save();

  if (eraser) {
    ctx.globalCompositeOperation = "destination-out";
    ctx.strokeStyle = "rgba(0,0,0,1)";
  } else {
    ctx.globalCompositeOperation = "source-over";
    ctx.strokeStyle = color;
  }

  for (let i = 1; i < points.length; i++) {
    const a = points[i-1];
    const b = points[i];

    const w = baseSize * lerp(0.55, 1.25, b.p);

    const jx = (Math.random() - 0.5) * jitter * w;
    const jy = (Math.random() - 0.5) * jitter * w;

    ctx.lineWidth = w;
    ctx.globalAlpha = eraser ? 1.0 : baseAlpha;

    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;

    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.quadraticCurveTo(a.x + jx, a.y + jy, mx, my);
    ctx.stroke();
  }

  ctx.restore();
}

function pointerPressure(e){
  const p = (typeof e.pressure === "number" && e.pressure > 0) ? e.pressure : 0.65;
  return clamp(p, 0.1, 1.0);
}

function setStatus(t) { document.getElementById("status").innerText = t; }

function currentColor() { return document.getElementById("color").value; }
function sizeMul() { return Number(document.getElementById("size").value) / 6; }

document.getElementById("brushPreset").addEventListener("change", (e)=>{
  brushMode = e.target.value;
});
document.getElementById("stab").addEventListener("input", (e)=>{
  stabilizer = Number(e.target.value);
});

canvas.addEventListener("pointerdown", (e) => {
  canvas.setPointerCapture(e.pointerId);
  drawing = true;
  points = [];
  lastT = performance.now();

  const p = pos(e);
  addPoint({ x: p.x, y: p.y, p: pointerPressure(e), t: performance.now() });
});

canvas.addEventListener("pointermove", (e) => {
  if (!drawing) return;
  const p = pos(e);
  addPoint({ x: p.x, y: p.y, p: pointerPressure(e), t: performance.now() });

  drawStroke(currentColor(), sizeMul());
});

canvas.addEventListener("pointerup", (e) => {
  drawing = false;
  points = [];
});
canvas.addEventListener("pointercancel", () => {
  drawing = false;
  points = [];
});

let capsuleId = null;
let token = null;

async function makeCapsule() {
  setStatus("Creating capsule + token...");
  const title = "Forge Sketch " + new Date().toISOString().slice(0,19).replace("T"," ");
  const intent = document.getElementById("intent").value || "";
  const fd = new FormData();
  fd.append("title", title);
  fd.append("creator", "human");
  fd.append("intent_text", intent);
  fd.append("tags", "forge,dragon-scale");

  const capRes = await fetch("/forge/capsule/new", { method:"POST", body: fd });
  const cap = await capRes.json();
  capsuleId = cap.capsule_id;
  document.getElementById("capsuleId").innerText = capsuleId;

  const tfd = new FormData();
  tfd.append("issued_to", "forge_web");
  tfd.append("capabilities", "DS_ALL");
  tfd.append("minutes", "240");
  tfd.append("max_fidelity", "80");
  const tokRes = await fetch("/hermes/token", { method:"POST", body: tfd });
  const tok = await tokRes.json();
  token = tok.token;
  document.getElementById("tokenState").innerText = "ok";
  setStatus("Capsule + token ready.");
}

function canvasDataURL() {
  return canvas.toDataURL("image/png");
}

function addImage(label, url) {
  const out = document.getElementById("outputs");
  const div = document.createElement("div");
  div.innerHTML = `<div class="small" style="margin-top:10px;">${label}</div>
                   <img src="${url}" />
                   <div class="small" style="margin-top:6px;"><a href="${url}" target="_blank" style="color:#8db0ff">Open/Download</a></div>`;
  out.appendChild(div);
}

async function runAll() {
  if (!capsuleId || !token) {
    await makeCapsule();
  }
  document.getElementById("outputs").innerHTML = "";
  setStatus("Running ALL: ingest → clean → remix → polish → export...");

  const style = document.getElementById("style").value;
  const fidelity = document.getElementById("fidelity").value;
  const tier = document.getElementById("tier").value;
  const n = document.getElementById("variants").value;
  const intent = document.getElementById("intent").value || "";

  const fd = new FormData();
  fd.append("cap_token", token);
  fd.append("caller", "human");
  fd.append("capsule_id", capsuleId);
  fd.append("data_url", canvasDataURL());
  fd.append("intent_text", intent);

  const res = await fetch("/forge/run_all", { method:"POST", body: fd });
  const j = await res.json();
  if (!res.ok) {
    setStatus("Error: " + (j.detail || "unknown"));
    return;
  }

  setStatus("Done.");
  addImage("CLEAN", j.clean_url);

  for (let i=0; i<j.variant_urls.length; i++) {
    addImage("VARIANT " + (i+1), j.variant_urls[i]);
  }

  addImage("POLISH", j.polish_url);
  addImage("EXPORT", j.export_url);
}

</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML)


@app.post("/hermes/token")
def api_issue_token(
    issued_to: str = Form(...),
    capabilities: str = Form(...),
    scope: str = Form("LOCAL_ONLY"),
    minutes: int = Form(60),
    max_fidelity: int = Form(DEFAULT_MAX_FIDELITY_AI),
    allowed_style_packs: str = Form(""),
):
    if capabilities.strip() == "DS_ALL":
        caps = [
            "DS_INGEST", "DS_REDRAW_CLEAN", "DS_REMIX_VARIANTS",
            "DS_POLISH", "DS_UPSCALE", "DS_EXPORT"
        ]
    else:
        caps = [c.strip() for c in capabilities.split(",") if c.strip()]

    allow = [s.strip() for s in allowed_style_packs.split(",") if s.strip()]
    tok = issue_token(
        issued_to=issued_to,
        capabilities=caps,
        scope=scope,
        minutes=minutes,
        max_fidelity=max_fidelity,
        allowed_style_packs=allow,
    )
    return {"token": tok, "caps": caps, "scope": scope, "max_fidelity": max_fidelity, "allowed_styles": allow}


@app.post("/forge/capsule/new")
def api_capsule_new(
    title: str = Form(...),
    creator: str = Form("human"),
    intent_text: str = Form(""),
    tags: str = Form(""),
):
    cap = new_capsule(
        title=title,
        creator=creator,
        intent_text=intent_text,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
    )
    return cap


@app.get("/forge/capsule/{capsule_id}")
def api_capsule_get(capsule_id: str):
    try:
        return load_capsule(capsule_id)
    except FileNotFoundError:
        raise HTTPException(404, "Capsule not found.")


@app.get("/file")
def api_file(path: str):
    p = Path(path)
    if not p.exists():
        raise HTTPException(404, "File not found.")
    return FileResponse(str(p))


# ============================================================
# "ALL" Pipeline Endpoint (Clean → Remix → Polish → Export)
# ============================================================
@app.post("/forge/run_all")
def forge_run_all(
    cap_token: str = Form(...),
    caller: str = Form("human"),
    capsule_id: str = Form(...),
    data_url: str = Form(...),
    intent_text: str = Form(""),
    style_id: str = Form("blueprint.clean"),
    fidelity: int = Form(35),
    variants: int = Form(4),
    tier: str = Form("8K"),
):
    try:
        tok = verify_token(cap_token)
        enforce(tok, "DS_INGEST")
        enforce(tok, "DS_REDRAW_CLEAN")
        enforce(tok, "DS_REMIX_VARIANTS")
        enforce(tok, "DS_POLISH")
        enforce(tok, "DS_EXPORT")
        enforce_fidelity(tok, int(fidelity), caller)
        enforce_style(tok, style_id)
    except PermissionError as e:
        raise HTTPException(403, str(e))

    try:
        cap = load_capsule(capsule_id)
    except FileNotFoundError:
        raise HTTPException(404, "Capsule not found.")

    bundle_upload_id = new_id("upload")
    up_dir = artifact_dir(bundle_upload_id)
    img = pil_from_data_url(data_url)

    original_ref = save_artifact_image(img, up_dir, "original.png")
    cap["inputs"]["original_sketch_ref"] = original_ref
    cap["intent_text"] = intent_text or cap.get("intent_text")

    edges = extract_edges(img)
    blueprint_id = new_id("bp")
    bp_dir = ARTIFACTS_DIR / blueprint_id
    bp_dir.mkdir(parents=True, exist_ok=True)
    edges_ref = save_artifact_image(edges, bp_dir, "edges.png")
    blueprint = {
        "blueprint_id": blueprint_id,
        "edges_image_ref": edges_ref,
        "layers_plan": {"base": "line_art"},
        "semantic_map_ref": None,
        "constraints_hint": {},
    }
    write_json(bp_dir / "blueprint.json", blueprint)
    cap["blueprint"] = blueprint

    audit_id_ingest = audit({
        "caller": caller, "op": "INGEST",
        "capsule_id": capsule_id,
        "blueprint_id": blueprint_id,
        "local_cloud": "LOCAL",
    })
    cap = append_version(cap, {
        "version_id": f"v_{blueprint_id}",
        "parent_version_id": cap["versions"][-1]["version_id"] if cap["versions"] else None,
        "operation": "INGEST",
        "caller": caller,
        "ds_version": DS_VERSION,
        "blueprint_ref": blueprint_id,
        "artifact_bundle_ref": None,
        "audit_id": audit_id_ingest,
        "fidelity": 0,
        "seed": None,
        "style_pack": None,
        "target_spec": None,
        "notes": None,
        "created_at": now_iso(),
    })

    line_weight = 1.2
    clean_img = clean_line_art(edges, line_weight=line_weight)

    clean_bundle_id = new_id("bundle")
    clean_dir = artifact_dir(clean_bundle_id)
    clean_ref = save_artifact_image(clean_img, clean_dir, "clean.png")
    write_json(clean_dir / "bundle.json", {
        "bundle_id": clean_bundle_id,
        "base_render_ref": clean_ref,
        "layers_refs": {"line_art": clean_ref},
        "metadata": {"ds_version": DS_VERSION, "operation": "CLEAN", "line_weight": line_weight},
    })

    audit_id_clean = audit({
        "caller": caller, "op": "CLEAN",
        "capsule_id": capsule_id,
        "bundle_id": clean_bundle_id,
        "local_cloud": "LOCAL",
    })
    cap = append_version(cap, {
        "version_id": f"v_{clean_bundle_id}",
        "parent_version_id": cap["versions"][-1]["version_id"],
        "operation": "CLEAN",
        "caller": caller,
        "ds_version": DS_VERSION,
        "blueprint_ref": blueprint_id,
        "artifact_bundle_ref": clean_bundle_id,
        "audit_id": audit_id_clean,
        "fidelity": 0,
        "seed": None,
        "style_pack": None,
        "target_spec": None,
        "notes": None,
        "created_at": now_iso(),
    })

    variants = int(max(1, min(9, variants)))
    fidelity = int(max(0, min(100, fidelity)))

    def variant_intensity(i: int) -> float:
        base_int = max(0.15, min(1.0, fidelity / 100.0))
        jitter = (i - (variants - 1) / 2) * (0.06 / max(1, variants - 1))
        return max(0.0, min(1.0, base_int + jitter))

    variant_urls: List[str] = []
    variant_ids: List[str] = []
    for i in range(variants):
        vid = new_id("bundle")
        vdir = artifact_dir(vid)

        styled = apply_style(clean_img, style_id=style_id, intensity=variant_intensity(i))
        vref = save_artifact_image(styled, vdir, f"variant_{i+1}.png")
        write_json(vdir / "bundle.json", {
            "bundle_id": vid,
            "base_render_ref": vref,
            "layers_refs": {"base": vref},
            "metadata": {
                "ds_version": DS_VERSION,
                "operation": "REMIX",
                "style_id": style_id,
                "fidelity": fidelity,
                "parent_bundle": clean_bundle_id,
            },
        })

        variant_ids.append(vid)
        variant_urls.append(f"/file?path={vref}")

    audit_id_remix = audit({
        "caller": caller, "op": "REMIX",
        "capsule_id": capsule_id,
        "base_bundle_id": clean_bundle_id,
        "variant_bundle_ids": variant_ids,
        "style_id": style_id,
        "fidelity": fidelity,
        "local_cloud": "LOCAL",
    })

    for vid in variant_ids:
        cap = append_version(cap, {
            "version_id": f"v_{vid}",
            "parent_version_id": cap["versions"][-1]["version_id"],
            "operation": "REMIX",
            "caller": caller,
            "ds_version": DS_VERSION,
            "blueprint_ref": blueprint_id,
            "artifact_bundle_ref": vid,
            "audit_id": audit_id_remix,
            "fidelity": fidelity,
            "seed": None,
            "style_pack": {"style_id": style_id, "params": {}},
            "target_spec": None,
            "notes": None,
            "created_at": now_iso(),
        })

    polish_base_ref = read_json(ARTIFACTS_DIR / variant_ids[0] / "bundle.json")["base_render_ref"]
    polish_base_img = Image.open(polish_base_ref).convert("RGB")

    if tier not in TIERS:
        tier = "8K"
    hi = upscale(polish_base_img, tier)
    hi = hi.filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=3))

    polish_id = new_id("bundle")
    pdir = artifact_dir(polish_id)
    polish_ref = save_artifact_image(hi, pdir, "polish.png")
    write_json(pdir / "bundle.json", {
        "bundle_id": polish_id,
        "base_render_ref": polish_ref,
        "layers_refs": {"polish": polish_ref},
        "metadata": {"ds_version": DS_VERSION, "operation": "POLISH", "tier": tier, "parent_bundle": variant_ids[0]},
    })

    audit_id_polish = audit({
        "caller": caller, "op": "POLISH",
        "capsule_id": capsule_id,
        "bundle_id": polish_id,
        "tier": tier,
        "local_cloud": "LOCAL",
    })
    cap = append_version(cap, {
        "version_id": f"v_{polish_id}",
        "parent_version_id": cap["versions"][-1]["version_id"],
        "operation": "POLISH",
        "caller": caller,
        "ds_version": DS_VERSION,
        "blueprint_ref": blueprint_id,
        "artifact_bundle_ref": polish_id,
        "audit_id": audit_id_polish,
        "fidelity": fidelity,
        "seed": None,
        "style_pack": {"style_id": style_id, "params": {"intensity": fidelity/100.0}},
        "target_spec": {"internal_res_tier": tier, "format": "PNG"},
        "notes": None,
        "created_at": now_iso(),
    })

    export_path = Path(polish_ref).with_name("export.png")
    Image.open(polish_ref).save(export_path, "PNG")

    audit_id_export = audit({
        "caller": caller, "op": "EXPORT",
        "capsule_id": capsule_id,
        "bundle_id": polish_id,
        "format": "PNG",
        "local_cloud": "LOCAL",
    })
    cap["exports"].append({
        "export_id": new_id("export"),
        "version_id": f"v_{polish_id}",
        "files": [str(export_path)],
        "format": "PNG",
        "audit_id": audit_id_export,
        "created_at": now_iso(),
    })
    save_capsule(cap)

    clean_url = f"/file?path={clean_ref}"
    polish_url = f"/file?path={polish_ref}"
    export_url = f"/file?path={str(export_path)}"

    return JSONResponse({
        "capsule_id": capsule_id,
        "clean_url": clean_url,
        "variant_urls": variant_urls,
        "polish_url": polish_url,
        "export_url": export_url,
        "tier": tier,
        "style_id": style_id,
        "fidelity": fidelity,
    })
