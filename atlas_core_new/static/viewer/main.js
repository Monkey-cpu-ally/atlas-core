import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { PROJECTS, EXPORT_PRESETS } from "/viewer/assets/projects.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf2f5f8);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 2000);
camera.position.set(4.5, 3.0, 5.2);

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0.4, 0);
controls.minDistance = 1.5;
controls.maxDistance = 12;

scene.add(new THREE.AmbientLight(0xffffff, 1.1));
const key = new THREE.DirectionalLight(0xffffff, 1.4);
key.position.set(6, 10, 6);
scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 0.7);
fill.position.set(-6, 4, 2);
scene.add(fill);
const rim = new THREE.DirectionalLight(0xffffff, 0.9);
rim.position.set(0, 6, -8);
scene.add(rim);

const grid = new THREE.GridHelper(50, 100, 0xd0d5da, 0xe0e5ea);
grid.position.y = -0.6;
scene.add(grid);

const root = new THREE.Group();
scene.add(root);

const projectSelect = document.getElementById("project");
const slidersDiv = document.getElementById("sliders");
const resetBtn = document.getElementById("reset");
const shotBtn = document.getElementById("shot");
const exportBtn = document.getElementById("export");
const statusDiv = document.getElementById("status");
const badgeInfo = document.getElementById("badgeInfo");
const statsInfo = document.getElementById("statsInfo");
const domainLabel = document.getElementById("projectDomain");
const partInfo = document.getElementById("partInfo");
const action1 = document.getElementById("action1");
const action2 = document.getElementById("action2");

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

let selected = null;
let selectedOriginalMat = null;

const highlightMat = new THREE.MeshStandardMaterial({
  color: 0x00a6ff,
  emissive: 0x0055aa,
  emissiveIntensity: 0.9,
  metalness: 0.2,
  roughness: 0.35
});

function showPartInfo(mesh) {
  var meta = mesh.userData.meta || {};
  var name = meta.name || mesh.name || "Unnamed Part";
  var fn = meta.function || "\u2014";
  var material = meta.material || "\u2014";
  var tool = meta.tool || "\u2014";

  partInfo.innerHTML =
    "<b>Part:</b> " + name + "<br/>" +
    "<b>Function:</b> " + fn + "<br/>" +
    "<b>Material:</b> " + material + "<br/>" +
    "<b>Tool:</b> " + tool;
}

function findMetaParent(obj) {
  var current = obj;
  while (current) {
    if (current.userData && current.userData.meta) return current;
    current = current.parent;
  }
  return obj;
}

function pick(event) {
  var rect = renderer.domElement.getBoundingClientRect();
  var x = (event.clientX - rect.left) / rect.width * 2 - 1;
  var y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  mouse.set(x, y);

  raycaster.setFromCamera(mouse, camera);

  var hits = raycaster.intersectObjects(root.children, true);
  if (!hits.length) return;

  var mesh = hits[0].object;

  if (selected) {
    selected.material = selectedOriginalMat;
    selected = null;
    selectedOriginalMat = null;
  }

  if (mesh && mesh.isMesh) {
    selected = mesh;
    selectedOriginalMat = mesh.material;
    mesh.material = highlightMat;

    var metaObj = findMetaParent(mesh);
    showPartInfo(metaObj);
  }
}

renderer.domElement.addEventListener("pointerdown", pick);

function setProjectActions() {
  if (currentProjectKey === "metal_flower") {
    action1.textContent = "Deploy";
    action2.textContent = "Retract";
    action1.onclick = function() { setParam("open", 1.0); };
    action2.onclick = function() { setParam("open", 0.0); };
  } else if (currentProjectKey === "medusa_arms") {
    action1.textContent = "Extend";
    action2.textContent = "Curl";
    action1.onclick = function() { setParam("explode", 1.0); setParam("bend", 0.0); };
    action2.onclick = function() { setParam("explode", 0.2); setParam("bend", 1.0); };
  } else if (currentProjectKey === "green_bot") {
    action1.textContent = "Self-Test";
    action2.textContent = "Walk Demo";
    action1.onclick = function() { statusDiv.textContent = "Self-Test: Motors OK \u2022 Sensors OK \u2022 Power OK (sim)"; };
    action2.onclick = function() { statusDiv.textContent = "Walk Demo: Next upgrade adds gait animation."; };
  } else {
    action1.textContent = "Action 1";
    action2.textContent = "Action 2";
    action1.onclick = null;
    action2.onclick = null;
  }
}

let currentProjectKey = projectSelect.value;
let currentProject = null;
let params = {};
let sliderEls = {};

function buildSliders(def) {
  slidersDiv.innerHTML = "";
  sliderEls = {};
  params = {};

  def.controls.forEach(ctrl => {
    const row = document.createElement("div");
    row.className = "row";

    const label = document.createElement("label");
    const valSpan = document.createElement("span");
    valSpan.className = "val";
    valSpan.id = "val_" + ctrl.key;
    valSpan.textContent = parseFloat(ctrl.value).toFixed(ctrl.step < 1 ? 2 : 0);
    label.textContent = ctrl.label + " ";
    label.appendChild(valSpan);
    row.appendChild(label);

    const input = document.createElement("input");
    input.type = "range";
    input.min = ctrl.min;
    input.max = ctrl.max;
    input.step = ctrl.step;
    input.value = ctrl.value;

    params[ctrl.key] = parseFloat(ctrl.value);
    sliderEls[ctrl.key] = input;

    input.addEventListener("input", () => {
      const v = parseFloat(input.value);
      params[ctrl.key] = v;
      valSpan.textContent = v.toFixed(ctrl.step < 1 ? 2 : 0);
      if (currentProject && currentProject.update) currentProject.update(params);
    });

    row.appendChild(input);
    slidersDiv.appendChild(row);
  });
}

function setParam(key, value) {
  const v = typeof value === "number" ? value : parseFloat(value);
  params[key] = v;
  if (sliderEls[key]) {
    sliderEls[key].value = v;
    const valEl = document.getElementById("val_" + key);
    if (valEl) {
      const step = parseFloat(sliderEls[key].step);
      valEl.textContent = v.toFixed(step < 1 ? 2 : 0);
    }
  }
  if (currentProject && currentProject.update) currentProject.update(params);
}

function clearRoot() {
  while (root.children.length) root.remove(root.children[0]);
}

function loadProject(key) {
  try {
  currentProjectKey = key;
  clearRoot();

  const def = PROJECTS[key];
  if (!def) return;

  buildSliders(def);
  currentProject = def.build(root, params);
  if (currentProject && currentProject.update) currentProject.update(params);

  const safetyColors = { LOW: "#4ade80", MEDIUM: "#f97316", HIGH: "#ef4444" };
  const domainColors = { ROBOTICS: "#818cf8", ENERGY: "#fbbf24", MATERIALS: "#22d3ee", UI_SYSTEM: "#a855f7" };
  const sc = safetyColors[def.safety] || "#888";
  const dc = domainColors[def.domain] || "#888";

  badgeInfo.innerHTML =
    '<span style="color:' + dc + ';font-weight:700;">' + def.domain + '</span>' +
    ' &middot; <span style="color:' + sc + ';font-weight:700;">' + def.safety + ' SAFETY</span>' +
    ' &middot; v1.0';

  statsInfo.textContent = def.info + " | " + def.materials;
  domainLabel.textContent = def.domain;
  domainLabel.style.color = dc;
  statusDiv.textContent = "";

  partInfo.innerHTML =
    "<b>Part:</b> None<br/>" +
    "<b>Function:</b> \u2014<br/>" +
    "<b>Material:</b> \u2014<br/>" +
    "<b>Tool:</b> \u2014";

  if (selected) {
    selected.material = selectedOriginalMat;
    selected = null;
    selectedOriginalMat = null;
  }

  setProjectActions();
  } catch(err) {
    console.error("loadProject error:", err);
    statusDiv.textContent = "ERROR: " + err.message;
    statsInfo.textContent = "Error loading: " + err.message;
  }
}

function downloadScreenshot() {
  renderer.render(scene, camera);
  const dataURL = renderer.domElement.toDataURL("image/png");
  const a = document.createElement("a");
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  a.href = dataURL;
  a.download = currentProjectKey + "_" + ts + ".png";
  a.click();
}

function resetView() {
  camera.position.set(4.5, 3.0, 5.2);
  controls.target.set(0, 0.4, 0);
  controls.update();
}

function sleep(ms) {
  return new Promise(function(res) { setTimeout(res, ms); });
}

function formatStepName(i) {
  return "step_" + String(i).padStart(2, "0") + ".png";
}

async function exportStepsZip() {
  const preset = EXPORT_PRESETS[currentProjectKey];
  if (!preset) {
    statusDiv.textContent = "No export preset for this project yet.";
    return;
  }

  exportBtn.disabled = true;
  projectSelect.disabled = true;
  shotBtn.disabled = true;
  resetBtn.disabled = true;

  const zip = new window.JSZip();
  const folder = zip.folder(currentProjectKey + "_steps");
  const steps = preset.steps;
  const total = steps.length;

  statusDiv.textContent = "Exporting " + total + " steps...";

  for (let i = 0; i < total; i++) {
    const stepParams = steps[i];
    Object.keys(stepParams).forEach(function(k) {
      if (k !== "visible") setParam(k, stepParams[k]);
    });

    if (stepParams.visible && currentProject.parts) {
      const v = stepParams.visible;
      var partNames = ["hub", "ring", "capsule", "sealRing", "tendrils"];
      partNames.forEach(function(name) {
        if (currentProject.parts[name]) {
          currentProject.parts[name].visible = v[name] !== false;
        }
      });
      if (currentProject.parts.petals) {
        const petalCount = typeof v.petals === "number" ? v.petals : currentProject.parts.petals.length;
        currentProject.parts.petals.forEach(function(p, idx) {
          p.visible = idx < petalCount;
        });
      }
    } else if (currentProject.parts) {
      var resetNames = ["hub", "ring", "capsule", "sealRing", "tendrils"];
      resetNames.forEach(function(name) {
        if (currentProject.parts[name]) currentProject.parts[name].visible = true;
      });
      if (currentProject.parts.petals) {
        currentProject.parts.petals.forEach(function(p) { p.visible = true; });
      }
    }

    await sleep(50);
    renderer.render(scene, camera);

    const dataURL = renderer.domElement.toDataURL("image/png");
    const base64 = dataURL.split(",")[1];
    folder.file(formatStepName(i + 1), base64, { base64: true });

    statusDiv.textContent = "Capturing step " + (i + 1) + "/" + total + "...";
  }

  statusDiv.textContent = "Packaging ZIP...";
  const blob = await zip.generateAsync({ type: "blob" });

  const a = document.createElement("a");
  const ts = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  a.href = URL.createObjectURL(blob);
  a.download = currentProjectKey + "_manual_steps_" + ts + ".zip";
  a.click();

  exportBtn.disabled = false;
  projectSelect.disabled = false;
  shotBtn.disabled = false;
  resetBtn.disabled = false;
  statusDiv.textContent = "Done. " + total + " steps exported as ZIP.";
}

projectSelect.addEventListener("change", function(e) { loadProject(e.target.value); });
resetBtn.addEventListener("click", resetView);
shotBtn.addEventListener("click", downloadScreenshot);
exportBtn.addEventListener("click", exportStepsZip);

loadProject(currentProjectKey);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", function() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
