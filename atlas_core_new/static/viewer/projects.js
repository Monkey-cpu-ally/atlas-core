import * as THREE from "three";

const matMetal   = new THREE.MeshStandardMaterial({ color: 0x7a8590, metalness: 0.8, roughness: 0.28 });
const matDark    = new THREE.MeshStandardMaterial({ color: 0x3a3e44, metalness: 0.7, roughness: 0.4 });
const matCore    = new THREE.MeshStandardMaterial({ color: 0x4a5058, metalness: 0.75, roughness: 0.35 });
const matBronze  = new THREE.MeshStandardMaterial({ color: 0x8a7050, metalness: 0.5, roughness: 0.55 });
const matGreen   = new THREE.MeshStandardMaterial({ color: 0x3a8a4a, metalness: 0.3, roughness: 0.6 });
const matBlack   = new THREE.MeshStandardMaterial({ color: 0x1e2228, metalness: 0.5, roughness: 0.6 });
const matRed     = new THREE.MeshStandardMaterial({ color: 0x9a3030, metalness: 0.3, roughness: 0.6 });
const matBlue    = new THREE.MeshStandardMaterial({ color: 0x3060a0, metalness: 0.4, roughness: 0.5 });
const matOrange  = new THREE.MeshStandardMaterial({ color: 0xc07020, metalness: 0.3, roughness: 0.5 });
const matSilver  = new THREE.MeshStandardMaterial({ color: 0xaab0b8, metalness: 0.9, roughness: 0.2 });
const matCopper  = new THREE.MeshStandardMaterial({ color: 0xb07040, metalness: 0.7, roughness: 0.35 });
const matTeal    = new THREE.MeshStandardMaterial({ color: 0x308080, metalness: 0.4, roughness: 0.5 });
const matAmber   = new THREE.MeshStandardMaterial({ color: 0xd4920a, metalness: 0.4, roughness: 0.4 });
const matGunmetal = new THREE.MeshStandardMaterial({ color: 0x2d3138, metalness: 0.85, roughness: 0.3 });
const matMesh    = new THREE.MeshStandardMaterial({ color: 0x1a1e24, metalness: 0.6, roughness: 0.7 });
const matEdgeTrim = new THREE.MeshStandardMaterial({ color: 0xc87828, metalness: 0.55, roughness: 0.35 });
const matPetal   = new THREE.MeshStandardMaterial({ color: 0xbfc6cd, metalness: 0.65, roughness: 0.35 });
const matTrim    = new THREE.MeshStandardMaterial({ color: 0xd08a1a, metalness: 0.35, roughness: 0.45 });
const matGlow    = new THREE.MeshStandardMaterial({ color: 0x9ad1ff, emissive: 0x2a8cff, emissiveIntensity: 1.4, metalness: 0.1, roughness: 0.7 });

function buildMetalFlower(root, params) {
  const parts = {
    hub: null,
    ring: null,
    capsule: null,
    sealRing: null,
    tendrils: null,
    petals: []
  };
  let currentPetalCount = 0;

  function rebuild(p) {
    while (root.children.length) root.remove(root.children[0]);
    const pc = p.petals || 8;
    currentPetalCount = pc;

    const g = new THREE.Group();
    root.add(g);

    parts.hub = new THREE.Group();
    parts.hub.name = "hub";
    parts.hub.userData.meta = {
      name: "Hub Core",
      function: "Anchor all petals + cam mechanism",
      material: "Alloy core (prototype: aluminum)",
      tool: "Hex key set / torque driver"
    };

    var baseFloor = new THREE.Mesh(
      new THREE.CylinderGeometry(1.55, 1.65, 0.08, 6),
      matGunmetal
    );
    baseFloor.rotation.x = Math.PI / 2;
    baseFloor.position.z = -0.18;
    parts.hub.add(baseFloor);

    var baseLower = new THREE.Mesh(
      new THREE.CylinderGeometry(1.40, 1.55, 0.14, 6),
      matCore
    );
    baseLower.rotation.x = Math.PI / 2;
    baseLower.position.z = -0.07;
    parts.hub.add(baseLower);

    var baseUpper = new THREE.Mesh(
      new THREE.CylinderGeometry(1.20, 1.40, 0.12, 6),
      matDark
    );
    baseUpper.rotation.x = Math.PI / 2;
    baseUpper.position.z = 0.06;
    parts.hub.add(baseUpper);

    for (var s = 0; s < 6; s++) {
      var sa = (s / 6) * Math.PI * 2;
      var plateW = 0.95;
      var plateH = 0.22;
      var plateGeo = new THREE.BoxGeometry(plateW, plateH, 0.06);
      var plate = new THREE.Mesh(plateGeo, matGunmetal);
      plate.position.set(Math.cos(sa) * 1.22, Math.sin(sa) * 1.22, -0.07);
      plate.rotation.z = sa;
      parts.hub.add(plate);

      var grooveL = new THREE.Mesh(
        new THREE.BoxGeometry(0.02, plateH + 0.02, 0.07),
        matBlack
      );
      grooveL.position.set(
        Math.cos(sa) * 1.22 + Math.cos(sa + Math.PI / 2) * plateW * 0.48,
        Math.sin(sa) * 1.22 + Math.sin(sa + Math.PI / 2) * plateW * 0.48,
        -0.07
      );
      grooveL.rotation.z = sa;
      parts.hub.add(grooveL);
    }

    var lipLower = new THREE.Mesh(
      new THREE.TorusGeometry(1.48, 0.025, 8, 48),
      matAmber
    );
    lipLower.rotation.x = Math.PI / 2;
    lipLower.position.z = -0.14;
    parts.hub.add(lipLower);

    var lipUpper = new THREE.Mesh(
      new THREE.TorusGeometry(1.30, 0.02, 8, 48),
      matAmber
    );
    lipUpper.rotation.x = Math.PI / 2;
    lipUpper.position.z = 0.0;
    parts.hub.add(lipUpper);

    g.add(parts.hub);

    parts.ring = new THREE.Group();
    parts.ring.name = "ring";
    parts.ring.userData.meta = {
      name: "Cam Ring",
      function: "Drives petal opening/closing",
      material: "Steel/Alloy ring",
      tool: "Bearing grease + torque driver"
    };

    var camRingMain = new THREE.Mesh(
      new THREE.TorusGeometry(0.95, 0.07, 16, 64),
      matGunmetal
    );
    camRingMain.rotation.x = Math.PI / 2;
    parts.ring.add(camRingMain);

    var camRingAmber = new THREE.Mesh(
      new THREE.TorusGeometry(0.95, 0.035, 8, 64),
      matAmber
    );
    camRingAmber.rotation.x = Math.PI / 2;
    camRingAmber.position.z = 0.06;
    parts.ring.add(camRingAmber);

    for (var n = 0; n < pc; n++) {
      var na = (n / pc) * Math.PI * 2;
      var lug = new THREE.Mesh(
        new THREE.BoxGeometry(0.08, 0.06, 0.1),
        matBlack
      );
      lug.position.set(Math.cos(na) * 0.95, Math.sin(na) * 0.95, 0);
      lug.rotation.z = na;
      parts.ring.add(lug);
    }

    parts.ring.position.z = 0.14;
    g.add(parts.ring);

    parts.capsule = new THREE.Group();
    parts.capsule.name = "capsule";
    parts.capsule.userData.meta = {
      name: "Central Capsule",
      function: "Houses sensor core + power distribution",
      material: "Hardened alloy shell, amber seals",
      tool: "Spanner wrench + seal press"
    };

    var capLower = new THREE.Mesh(
      new THREE.CylinderGeometry(0.38, 0.44, 0.5, 8),
      matGunmetal
    );
    capLower.rotation.x = Math.PI / 2;
    capLower.position.z = -0.1;
    parts.capsule.add(capLower);

    var capMid = new THREE.Mesh(
      new THREE.CylinderGeometry(0.34, 0.38, 0.5, 8),
      matDark
    );
    capMid.rotation.x = Math.PI / 2;
    capMid.position.z = 0.35;
    parts.capsule.add(capMid);

    var capUpper = new THREE.Mesh(
      new THREE.CylinderGeometry(0.28, 0.34, 0.4, 8),
      matGunmetal
    );
    capUpper.rotation.x = Math.PI / 2;
    capUpper.position.z = 0.75;
    parts.capsule.add(capUpper);

    var capDome = new THREE.Mesh(
      new THREE.SphereGeometry(0.28, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2),
      matCore
    );
    capDome.rotation.x = -Math.PI / 2;
    capDome.position.z = 0.95;
    parts.capsule.add(capDome);

    var lensOuter = new THREE.Mesh(
      new THREE.CylinderGeometry(0.16, 0.16, 0.05, 24),
      matSilver
    );
    lensOuter.rotation.x = Math.PI / 2;
    lensOuter.position.z = 0.98;
    parts.capsule.add(lensOuter);

    var lensInner = new THREE.Mesh(
      new THREE.CylinderGeometry(0.10, 0.10, 0.06, 24),
      matBlack
    );
    lensInner.rotation.x = Math.PI / 2;
    lensInner.position.z = 1.0;
    parts.capsule.add(lensInner);

    var bandPositions = [-0.25, -0.05, 0.15, 0.40, 0.60, 0.80];
    for (var b = 0; b < bandPositions.length; b++) {
      var bz = bandPositions[b];
      var br = 0.42 - b * 0.02;
      var band = new THREE.Mesh(
        new THREE.TorusGeometry(br, 0.025, 8, 32),
        matAmber
      );
      band.rotation.x = Math.PI / 2;
      band.position.z = bz;
      parts.capsule.add(band);
    }

    for (var v = 0; v < 8; v++) {
      var va = (v / 8) * Math.PI * 2;
      var vent = new THREE.Mesh(
        new THREE.BoxGeometry(0.03, 0.6, 0.04),
        matBlack
      );
      vent.position.set(Math.cos(va) * 0.36, Math.sin(va) * 0.36, 0.35);
      vent.rotation.z = va;
      parts.capsule.add(vent);
    }

    parts.capsule.position.z = 0.3;
    g.add(parts.capsule);

    parts.sealRing = new THREE.Group();
    parts.sealRing.name = "sealRing";
    parts.sealRing.userData.meta = {
      name: "Seal Ring",
      function: "Weather seal + inner bearing race",
      material: "Copper alloy gasket",
      tool: "Seal press + alignment jig"
    };

    var innerSeal = new THREE.Mesh(
      new THREE.TorusGeometry(0.52, 0.04, 12, 40),
      matEdgeTrim
    );
    innerSeal.rotation.x = Math.PI / 2;
    parts.sealRing.add(innerSeal);

    var sealPlate = new THREE.Mesh(
      new THREE.CylinderGeometry(0.56, 0.56, 0.05, 32),
      matDark
    );
    sealPlate.rotation.x = Math.PI / 2;
    parts.sealRing.add(sealPlate);

    parts.sealRing.position.z = 0.16;
    g.add(parts.sealRing);

    parts.tendrils = new THREE.Group();
    parts.tendrils.name = "tendrils";
    parts.tendrils.userData.meta = {
      name: "Tendril Assembly",
      function: "Flexible power/data conduits between petals",
      material: "Copper braid + amber insulation",
      tool: "Cable guides + heat shrink"
    };

    for (var t = 0; t < pc; t++) {
      var ta = ((t + 0.5) / pc) * Math.PI * 2;
      for (var strand = 0; strand < 4; strand++) {
        var segs = 5 + strand;
        var baseR = 0.55 + strand * 0.06;
        var rise = 0.25 + strand * 0.15;
        for (var ss = 0; ss < segs; ss++) {
          var frac = ss / (segs - 1);
          var curl = frac * 1.2;
          var r = baseR + frac * 0.35;
          var thickness = 0.045 - frac * 0.02;
          var segMesh = new THREE.Mesh(
            new THREE.CylinderGeometry(thickness, thickness + 0.01, 0.12, 6),
            strand < 2 ? matAmber : matEdgeTrim
          );
          segMesh.position.set(
            Math.cos(ta + curl * 0.25) * r,
            Math.sin(ta + curl * 0.25) * r,
            rise + ss * 0.1
          );
          var outAngle = ta + frac * 0.4;
          segMesh.rotation.set(
            Math.sin(outAngle) * curl * 0.6,
            0,
            -Math.cos(outAngle) * curl * 0.6 + ta
          );
          parts.tendrils.add(segMesh);
        }
      }
    }
    g.add(parts.tendrils);

    parts.petals = [];

    var petalShape = new THREE.Shape();
    petalShape.moveTo(0.0, 0.0);
    petalShape.quadraticCurveTo(0.22, 0.15, 0.20, 0.45);
    petalShape.quadraticCurveTo(0.18, 0.85, 0.00, 1.00);
    petalShape.quadraticCurveTo(-0.18, 0.85, -0.20, 0.45);
    petalShape.quadraticCurveTo(-0.22, 0.15, 0.0, 0.0);

    var petalGeo = new THREE.ExtrudeGeometry(petalShape, {
      depth: 0.06,
      bevelEnabled: true,
      bevelThickness: 0.015,
      bevelSize: 0.01,
      bevelSegments: 2
    });
    petalGeo.center();

    var trimShape = new THREE.Shape();
    trimShape.moveTo(0.0, 0.02);
    trimShape.quadraticCurveTo(0.18, 0.16, 0.16, 0.45);
    trimShape.quadraticCurveTo(0.14, 0.78, 0.00, 0.90);
    trimShape.quadraticCurveTo(-0.14, 0.78, -0.16, 0.45);
    trimShape.quadraticCurveTo(-0.18, 0.16, 0.0, 0.02);

    var trimGeo = new THREE.ExtrudeGeometry(trimShape, {
      depth: 0.02,
      bevelEnabled: false
    });
    trimGeo.center();

    var pinGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.2, 12);
    var bushGeo = new THREE.TorusGeometry(0.06, 0.02, 8, 16);

    for (var i = 0; i < pc; i++) {
      var angle = (i / pc) * Math.PI * 2;
      var petal = new THREE.Group();
      petal.name = "petal_" + (i + 1);

      petal.userData.meta = {
        name: "Petal Plate " + (i + 1),
        function: "Protective shell + deployment surface",
        material: "Composite/Alloy plate",
        tool: "Pin punch + small hammer"
      };

      var petalBody = new THREE.Mesh(petalGeo, matPetal);
      petalBody.rotation.x = Math.PI / 2;
      petalBody.position.set(0, 0.45, 0);
      petal.add(petalBody);

      var petalTrimMesh = new THREE.Mesh(trimGeo, matTrim);
      petalTrimMesh.rotation.x = Math.PI / 2;
      petalTrimMesh.position.set(0, 0.47, 0.03);
      petal.add(petalTrimMesh);

      var glowStrip = new THREE.Mesh(
        new THREE.BoxGeometry(0.04, 0.75, 0.01),
        matGlow
      );
      glowStrip.position.set(0, 0.55, 0.05);
      petal.add(glowStrip);

      var pin = new THREE.Mesh(pinGeo, matBronze);
      pin.rotation.x = Math.PI / 2;
      pin.position.set(0, 0.04, 0);
      petal.add(pin);

      var bush = new THREE.Mesh(bushGeo, matBronze);
      bush.position.set(0, 0.04, 0);
      petal.add(bush);

      petal.position.set(Math.cos(angle) * 0.72, Math.sin(angle) * 0.72, 0.18);
      petal.rotation.z = angle;
      petal.userData.baseAngle = angle;
      g.add(petal);
      parts.petals.push(petal);
    }
  }

  rebuild(params);

  return {
    parts,
    update(p) {
      var pc = p.petals || 8;
      if (pc !== currentPetalCount) {
        rebuild(p);
      }

      var open = p.open || 0;
      var explode = p.explode || 0;
      var scale = p.scale || 1;

      root.scale.set(scale, scale, scale);

      parts.hub.position.z = -explode * 0.2;
      parts.ring.position.z = 0.14 + explode * 0.3;
      parts.ring.rotation.z = open * Math.PI * 0.45;
      parts.capsule.position.z = 0.3 + explode * 0.8;
      parts.sealRing.position.z = 0.16 + explode * 0.4;
      parts.tendrils.position.z = explode * 0.25;

      parts.petals.forEach(function(petal) {
        var a = petal.userData.baseAngle;
        var radial = 0.72 + explode * 0.6;
        petal.position.x = Math.cos(a) * radial;
        petal.position.y = Math.sin(a) * radial;
        petal.rotation.x = -open * 0.85;
        petal.position.z = 0.18 + explode * 0.3;
      });
    }
  };
}

function buildGreenBot(root, params) {
  let chassis, wheels, sensorArray, seedPod, solarPanel;
  const wheelPositions = [
    { x: -0.65, z: -0.7 }, { x: 0.65, z: -0.7 },
    { x: -0.65, z: 0.7 }, { x: 0.65, z: 0.7 },
    { x: -0.65, z: 0 }, { x: 0.65, z: 0 }
  ];

  while (root.children.length) root.remove(root.children[0]);

  const chassisGeo = new THREE.BoxGeometry(1.2, 0.35, 1.8);
  chassis = new THREE.Mesh(chassisGeo, matGreen);
  chassis.position.y = 0.45;
  root.add(chassis);

  const deckGeo = new THREE.BoxGeometry(1.0, 0.08, 1.5);
  const deck = new THREE.Mesh(deckGeo, matDark);
  deck.position.set(0, 0.66, 0);
  root.add(deck);

  wheels = [];
  const wheelGeo = new THREE.CylinderGeometry(0.22, 0.22, 0.12, 24);
  const axleGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.2, 12);
  wheelPositions.forEach(wp => {
    const wg = new THREE.Group();
    const wheel = new THREE.Mesh(wheelGeo, matBlack);
    wheel.rotation.z = Math.PI / 2;
    wg.add(wheel);
    const axle = new THREE.Mesh(axleGeo, matSilver);
    axle.rotation.z = Math.PI / 2;
    wg.add(axle);
    wg.position.set(wp.x, 0.22, wp.z);
    wg.userData.baseX = wp.x;
    wg.userData.baseZ = wp.z;
    root.add(wg);
    wheels.push(wg);
  });

  sensorArray = new THREE.Group();
  const sensorMast = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.5, 12), matSilver);
  sensorMast.position.set(0, 0.25, 0);
  sensorArray.add(sensorMast);
  const sensorHead = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 12), matTeal);
  sensorHead.position.set(0, 0.55, 0);
  sensorArray.add(sensorHead);
  for (let i = 0; i < 3; i++) {
    const probe = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.25, 8), matCopper);
    probe.position.set(Math.cos(i * 2.1) * 0.08, 0.1, Math.sin(i * 2.1) * 0.08);
    probe.rotation.x = 0.3;
    sensorArray.add(probe);
  }
  sensorArray.position.set(0.3, 0.7, -0.5);
  root.add(sensorArray);

  seedPod = new THREE.Group();
  const podBody = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.15, 0.4, 20), matOrange);
  podBody.position.y = 0.2;
  seedPod.add(podBody);
  const podCap = new THREE.Mesh(new THREE.SphereGeometry(0.15, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), matDark);
  podCap.position.y = 0.4;
  seedPod.add(podCap);
  const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.1, 0.12, 12), matMetal);
  nozzle.position.y = 0;
  seedPod.add(nozzle);
  seedPod.position.set(-0.3, 0.7, 0.55);
  root.add(seedPod);

  solarPanel = new THREE.Group();
  const panelBase = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.03, 0.5), matBlue);
  panelBase.position.y = 0.15;
  solarPanel.add(panelBase);
  const panelArm = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.3, 8), matSilver);
  panelArm.position.y = 0;
  solarPanel.add(panelArm);
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 4; c++) {
      const cell = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.005, 0.12), matBlue);
      cell.position.set(-0.28 + c * 0.18, 0.17, -0.14 + r * 0.14);
      solarPanel.add(cell);
    }
  }
  solarPanel.position.set(0, 0.7, 0);
  root.add(solarPanel);

  return {
    update(p) {
      const explode = p.explode || 0;
      const height = p.height || 0.65;
      const bend = p.bend || 0.25;
      const scale = p.scale || 1;

      root.scale.set(scale, scale, scale);
      chassis.position.y = 0.45 + explode * 0.4;
      deck.position.y = 0.66 + explode * 0.6;

      wheels.forEach(w => {
        w.position.x = w.userData.baseX * (1 + explode * 0.5);
        w.position.y = 0.22 - explode * 0.2;
      });

      sensorArray.position.y = 0.7 + explode * 0.8 + (height - 0.65) * 0.5;
      sensorArray.rotation.z = bend * 0.3;
      seedPod.position.y = 0.7 + explode * 0.6;
      solarPanel.position.y = 0.7 + explode * 1.0;
      solarPanel.rotation.x = bend * 0.4;
    }
  };
}

function buildMedusaArms(root, params) {
  const armCount = 6;
  let arms = [];
  let baseHub;
  let currentSegCount = 0;

  function rebuild(p) {
    while (root.children.length) root.remove(root.children[0]);
    const segCount = p.segments || 12;
    currentSegCount = segCount;

    const hubGeo = new THREE.CylinderGeometry(0.4, 0.45, 0.3, 32);
    baseHub = new THREE.Mesh(hubGeo, matDark);
    baseHub.position.y = 0.15;
    root.add(baseHub);

    const mountGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.08, 32);
    const mount = new THREE.Mesh(mountGeo, matMetal);
    mount.position.y = 0;
    root.add(mount);

    arms = [];
    for (let a = 0; a < armCount; a++) {
      const angle = (a / armCount) * Math.PI * 2;
      const arm = new THREE.Group();

      const segments = [];
      for (let s = 0; s < segCount; s++) {
        const radius = 0.08 - s * 0.004;
        const r = Math.max(radius, 0.02);
        const segGeo = new THREE.CylinderGeometry(r, r + 0.005, 0.12, 12);
        const seg = new THREE.Mesh(segGeo, s % 2 === 0 ? matMetal : matCopper);
        seg.position.y = s * 0.13;
        segments.push(seg);
        arm.add(seg);

        if (s < segCount - 1) {
          const jointGeo = new THREE.SphereGeometry(r * 0.8, 8, 6);
          const joint = new THREE.Mesh(jointGeo, matDark);
          joint.position.y = s * 0.13 + 0.065;
          arm.add(joint);
        }
      }

      const tipGeo = new THREE.ConeGeometry(0.025, 0.08, 8);
      const tip = new THREE.Mesh(tipGeo, matTeal);
      tip.position.y = segCount * 0.13;
      arm.add(tip);

      arm.position.set(Math.cos(angle) * 0.35, 0.3, Math.sin(angle) * 0.35);
      arm.userData.baseAngle = angle;
      arm.userData.segments = segments;
      root.add(arm);
      arms.push(arm);
    }
  }

  rebuild(params);

  return {
    update(p) {
      const bend = p.bend || 0;
      const explode = p.explode || 0;
      const scale = p.scale || 1;
      const segCount = p.segments || 12;

      if (segCount !== currentSegCount) {
        rebuild(p);
      }

      root.scale.set(scale, scale, scale);
      baseHub.position.y = 0.15 + explode * 0.3;

      arms.forEach((arm) => {
        const a = arm.userData.baseAngle;
        const radial = 0.35 + explode * 0.5;
        arm.position.x = Math.cos(a) * radial;
        arm.position.z = Math.sin(a) * radial;
        arm.position.y = 0.3 + explode * 0.2;

        arm.rotation.x = Math.sin(a) * bend * 0.6;
        arm.rotation.z = -Math.cos(a) * bend * 0.6;

        arm.userData.segments.forEach((seg, i) => {
          seg.position.y = i * (0.13 + explode * 0.06);
        });
      });
    }
  };
}

function buildMorphPanel(root, params) {
  let cells = [];
  let frame;
  let currentDensity = 0;

  function rebuild(p) {
    while (root.children.length) root.remove(root.children[0]);
    const density = p.density || 12;
    currentDensity = density;

    const frameGeo = new THREE.BoxGeometry(2.4, 0.06, 2.4);
    frame = new THREE.Mesh(frameGeo, matDark);
    frame.position.y = 0;
    root.add(frame);

    const edgeGeo = new THREE.BoxGeometry(2.5, 0.12, 0.06);
    [
      { x: 0, z: -1.22, rY: 0 },
      { x: 0, z: 1.22, rY: 0 },
      { x: -1.22, z: 0, rY: Math.PI / 2 },
      { x: 1.22, z: 0, rY: Math.PI / 2 }
    ].forEach((e) => {
      const edge = new THREE.Mesh(edgeGeo, matMetal);
      edge.position.set(e.x, 0.03, e.z);
      edge.rotation.y = e.rY;
      root.add(edge);
    });

    cells = [];
    const spacing = 2.2 / density;

    for (let r = 0; r < density; r++) {
      for (let c = 0; c < density; c++) {
        const cellGeo = new THREE.BoxGeometry(spacing * 0.85, 0.15, spacing * 0.85);
        const cell = new THREE.Mesh(cellGeo, (r + c) % 2 === 0 ? matSilver : matMetal);
        const x = -1.1 + c * spacing + spacing / 2;
        const z = -1.1 + r * spacing + spacing / 2;
        cell.position.set(x, 0.1, z);
        cell.userData.baseX = x;
        cell.userData.baseZ = z;
        cell.userData.row = r;
        cell.userData.col = c;
        root.add(cell);
        cells.push(cell);
      }
    }

    const actuatorGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.1, 6);
    cells.forEach(cell => {
      const act = new THREE.Mesh(actuatorGeo, matCopper);
      act.position.set(cell.userData.baseX, 0, cell.userData.baseZ);
      root.add(act);
    });
  }

  rebuild(params);

  return {
    update(p) {
      const morph = p.morph || 0;
      const explode = p.explode || 0;
      const scale = p.scale || 1;
      const density = p.density || 12;

      if (density !== currentDensity) {
        rebuild(p);
      }

      root.scale.set(scale, scale, scale);
      frame.position.y = -explode * 0.3;

      cells.forEach(cell => {
        const r = cell.userData.row;
        const c = cell.userData.col;
        const d = density;
        const cx = (c / (d - 1)) * 2 - 1;
        const cz = (r / (d - 1)) * 2 - 1;
        const dist = Math.sqrt(cx * cx + cz * cz);
        const wave = Math.sin(dist * Math.PI * 1.5) * morph;
        cell.position.y = 0.1 + wave * 0.4 + explode * 0.15;
        cell.rotation.x = wave * 0.2;
        cell.rotation.z = wave * 0.15;
      });
    }
  };
}

function buildHydrogenModule(root, params) {
  let tank, stack, cooler, controller, pipes;

  while (root.children.length) root.remove(root.children[0]);

  const baseGeo = new THREE.BoxGeometry(2.0, 0.12, 1.4);
  const base = new THREE.Mesh(baseGeo, matDark);
  base.position.y = 0;
  root.add(base);

  const tankGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.0, 24);
  tank = new THREE.Mesh(tankGeo, matBlue);
  tank.position.set(-0.55, 0.6, 0);
  root.add(tank);
  const tankCapTop = new THREE.Mesh(new THREE.SphereGeometry(0.3, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), matBlue);
  tankCapTop.position.set(-0.55, 1.1, 0);
  root.add(tankCapTop);
  const tankCapBot = new THREE.Mesh(new THREE.SphereGeometry(0.3, 16, 8, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), matBlue);
  tankCapBot.position.set(-0.55, 0.1, 0);
  root.add(tankCapBot);

  const valve = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.15, 12), matRed);
  valve.position.set(-0.55, 1.25, 0);
  root.add(valve);
  const valveWheel = new THREE.Mesh(new THREE.TorusGeometry(0.08, 0.015, 8, 16), matRed);
  valveWheel.position.set(-0.55, 1.35, 0);
  root.add(valveWheel);

  const warning = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.2, 0.01), matOrange);
  warning.position.set(-0.55, 0.7, 0.31);
  root.add(warning);

  stack = new THREE.Group();
  for (let i = 0; i < 6; i++) {
    const plateGeo = new THREE.BoxGeometry(0.5, 0.05, 0.6);
    const plate = new THREE.Mesh(plateGeo, i % 2 === 0 ? matSilver : matMetal);
    plate.position.y = i * 0.07;
    plate.userData.stackIdx = i;
    stack.add(plate);
  }
  const endPlateGeo = new THREE.BoxGeometry(0.54, 0.08, 0.64);
  const endPlateTop = new THREE.Mesh(endPlateGeo, matDark);
  endPlateTop.position.y = 6 * 0.07;
  stack.add(endPlateTop);
  const endPlateBot = new THREE.Mesh(endPlateGeo, matDark);
  endPlateBot.position.y = -0.04;
  stack.add(endPlateBot);
  stack.position.set(0.15, 0.12, 0);
  root.add(stack);

  cooler = new THREE.Group();
  const finCount = 8;
  for (let i = 0; i < finCount; i++) {
    const finGeo = new THREE.BoxGeometry(0.4, 0.3, 0.008);
    const fin = new THREE.Mesh(finGeo, matSilver);
    fin.position.z = -0.25 + i * (0.5 / finCount);
    fin.userData.finIdx = i;
    cooler.add(fin);
  }
  const coolerFrame = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.32, 0.02), matDark);
  coolerFrame.position.z = -0.28;
  cooler.add(coolerFrame);
  cooler.position.set(0.7, 0.28, 0);
  root.add(cooler);

  controller = new THREE.Group();
  const ctrlBox = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 0.15), matBlack);
  ctrlBox.position.y = 0.1;
  controller.add(ctrlBox);
  const screen = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.1, 0.005), matTeal);
  screen.position.set(0, 0.14, 0.078);
  controller.add(screen);
  for (let i = 0; i < 3; i++) {
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.012, 6, 4), matGreen);
    led.position.set(-0.08 + i * 0.08, 0.05, 0.078);
    controller.add(led);
  }
  controller.position.set(0.15, 0.56, -0.5);
  root.add(controller);

  pipes = [];
  const pipeGeo = new THREE.CylinderGeometry(0.025, 0.025, 0.6, 8);
  const pipe1 = new THREE.Mesh(pipeGeo, matCopper);
  pipe1.position.set(-0.2, 0.35, 0.15);
  pipe1.rotation.z = Math.PI / 2;
  root.add(pipe1);
  pipes.push(pipe1);
  const pipe2 = new THREE.Mesh(pipeGeo, matCopper);
  pipe2.position.set(-0.2, 0.35, -0.15);
  pipe2.rotation.z = Math.PI / 2;
  root.add(pipe2);
  pipes.push(pipe2);

  return {
    update(p) {
      const open = p.open || 0;
      const explode = p.explode || 0;
      const scale = p.scale || 1;

      root.scale.set(scale, scale, scale);

      tank.position.x = -0.55 - explode * 0.6;
      tank.position.y = 0.6 + explode * 0.3;

      stack.position.y = 0.12 + explode * 0.2;
      stack.children.forEach(child => {
        if (child.userData.stackIdx !== undefined) {
          child.position.y = child.userData.stackIdx * (0.07 + explode * 0.08);
        }
      });

      cooler.position.x = 0.7 + explode * 0.5;
      cooler.position.y = 0.28 + explode * 0.15;
      cooler.children.forEach(child => {
        if (child.userData.finIdx !== undefined) {
          child.position.z = -0.25 + child.userData.finIdx * (0.5 / 8) * (1 + explode * 0.6);
        }
      });

      controller.position.y = 0.56 + explode * 0.5;
      controller.position.z = -0.5 - explode * 0.3;

      valveWheel.rotation.x = open * Math.PI * 2;
      pipes.forEach((pipe, i) => {
        pipe.position.y = 0.35 + explode * 0.1 * (i + 1);
      });
    }
  };
}


export const PROJECTS = {
  metal_flower: {
    label: "Metal Flower Mark I",
    domain: "MATERIALS",
    safety: "LOW",
    info: "Pedestal + Cam Ring + Capsule + Tendrils + Armored Petals",
    materials: "6061-T6 Al / SS304 / Bronze / NiTi Mesh",
    controls: [
      { key: "open",    label: "Open / Close", min: 0, max: 1, step: 0.01, value: 0 },
      { key: "explode", label: "Explode View", min: 0, max: 1, step: 0.01, value: 0 },
      { key: "petals",  label: "Petal Count",  min: 4, max: 16, step: 1, value: 8 },
      { key: "scale",   label: "Scale",        min: 0.5, max: 2.0, step: 0.01, value: 1.0 }
    ],
    build: buildMetalFlower
  },

  green_bot: {
    label: "Green Bot Eco Rover",
    domain: "ROBOTICS",
    safety: "MEDIUM",
    info: "Chassis + 6 Wheels + Sensor Mast + Seed Pod + Solar Panel",
    materials: "HDPE / Stainless / CFRP / Si-PV",
    controls: [
      { key: "explode", label: "Explode View", min: 0, max: 1, step: 0.01, value: 0 },
      { key: "height",  label: "Sensor Height", min: 0.3, max: 1.0, step: 0.01, value: 0.65 },
      { key: "bend",    label: "Panel Tilt",    min: 0, max: 1, step: 0.01, value: 0.25 },
      { key: "scale",   label: "Scale",         min: 0.5, max: 2.0, step: 0.01, value: 1.0 }
    ],
    build: buildGreenBot
  },

  medusa_arms: {
    label: "Medusa Tentacle Arms",
    domain: "ROBOTICS",
    safety: "MEDIUM",
    info: "Base Hub + 6 Segmented Arms + Joint Spheres + Tips",
    materials: "Silicone / NiTi SMA / CFRP / TPU",
    controls: [
      { key: "segments", label: "Segments",     min: 4, max: 20, step: 1, value: 12 },
      { key: "bend",     label: "Arm Bend",     min: 0, max: 1, step: 0.01, value: 0 },
      { key: "explode",  label: "Explode View", min: 0, max: 1, step: 0.01, value: 0 },
      { key: "scale",    label: "Scale",        min: 0.5, max: 2.0, step: 0.01, value: 1.0 }
    ],
    build: buildMedusaArms
  },

  morph_panel: {
    label: "Morphing Structure Panel",
    domain: "MATERIALS",
    safety: "LOW",
    info: "Frame + Actuator Grid + Compliant Cells",
    materials: "6061-T6 Al / Nitinol / PEEK",
    controls: [
      { key: "density",  label: "Cell Density",  min: 4, max: 16, step: 1, value: 12 },
      { key: "morph",    label: "Morph Amount",   min: 0, max: 1, step: 0.01, value: 0 },
      { key: "explode",  label: "Explode View",   min: 0, max: 1, step: 0.01, value: 0 },
      { key: "scale",    label: "Scale",           min: 0.5, max: 2.0, step: 0.01, value: 1.0 }
    ],
    build: buildMorphPanel
  },

  hydrogen_module: {
    label: "Hydrogen Power Module",
    domain: "ENERGY",
    safety: "HIGH",
    info: "H2 Tank + PEM Stack + Cooler + Controller + Pipes",
    materials: "SS316L / Nafion / Graphite / Cu Piping",
    controls: [
      { key: "open",    label: "Valve Open",    min: 0, max: 1, step: 0.01, value: 0 },
      { key: "explode", label: "Explode View",  min: 0, max: 1, step: 0.01, value: 0 },
      { key: "scale",   label: "Scale",         min: 0.5, max: 2.0, step: 0.01, value: 1.0 }
    ],
    build: buildHydrogenModule
  }
};


export const EXPORT_PRESETS = {
  metal_flower: {
    steps: (() => {
      const steps = [];
      const petals = 8;
      const scale = 1.0;

      steps.push({ open: 0.0, explode: 0.8, petals, scale, visible: { hub: true,  ring: false, capsule: false, sealRing: false, tendrils: false, petals: 0 } });
      steps.push({ open: 0.0, explode: 0.8, petals, scale, visible: { hub: true,  ring: true,  capsule: false, sealRing: false, tendrils: false, petals: 0 } });
      steps.push({ open: 0.0, explode: 0.8, petals, scale, visible: { hub: true,  ring: true,  capsule: true,  sealRing: false, tendrils: false, petals: 0 } });
      steps.push({ open: 0.0, explode: 0.8, petals, scale, visible: { hub: true,  ring: true,  capsule: true,  sealRing: true,  tendrils: false, petals: 0 } });
      steps.push({ open: 0.0, explode: 0.8, petals, scale, visible: { hub: true,  ring: true,  capsule: true,  sealRing: true,  tendrils: true,  petals: 0 } });

      for (let i = 1; i <= petals; i++) {
        steps.push({ open: 0.0, explode: 0.8, petals, scale, visible: { hub: true, ring: true, capsule: true, sealRing: true, tendrils: true, petals: i } });
      }

      for (let i = 0; i < 10; i++) {
        const t = i / 9;
        steps.push({ open: 0.0, explode: 0.8 - t * 0.8, petals, scale });
      }

      for (let i = 0; i < 15; i++) {
        const t = i / 14;
        steps.push({ open: t, explode: 0.0, petals, scale });
      }

      for (let i = 0; i < 10; i++) {
        const t = i / 9;
        steps.push({ open: 1.0 - t, explode: 0.0, petals, scale });
      }

      steps.push({ open: 0.45, explode: 0.5, petals: 6, scale });
      steps.push({ open: 0.45, explode: 0.5, petals: 10, scale });
      steps.push({ open: 0.45, explode: 0.5, petals: 12, scale });

      [0.25, 0.50, 0.75, 1.00, 0.00].forEach(function(e) {
        steps.push({ open: 0.0, explode: e, petals, scale });
      });

      return steps.slice(0, 60);
    })()
  },

  green_bot: {
    steps: Array.from({ length: 16 }, function(_, i) {
      const t = i / 15;
      return { stance: 1.0, height: 0.65, bend: 0.25 + t * 0.35, explode: t * 0.8, scale: 1.0 };
    })
  },

  medusa_arms: {
    steps: Array.from({ length: 16 }, function(_, i) {
      const t = i / 15;
      return { segments: 12, bend: t, explode: t * 0.9, scale: 1.0 };
    })
  },

  morph_panel: {
    steps: Array.from({ length: 16 }, function(_, i) {
      const t = i / 15;
      return { density: 12, morph: t, explode: t * 0.8, scale: 1.0 };
    })
  },

  hydrogen_module: {
    steps: Array.from({ length: 12 }, function(_, i) {
      const t = i / 11;
      return { open: t * 0.6, explode: t, scale: 1.0 };
    })
  }
};
