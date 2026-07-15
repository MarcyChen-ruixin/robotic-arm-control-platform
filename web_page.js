/**
 * RoArm portfolio front-end.
 * Talks only to the local Flask arm API. No parent-system WebSocket,
 * system-control, or USB/data services.
 */

let scene, camera, renderer;
let link1, link2;
let roarmAngles = [0.0, 0.0, 1.57, 3.14];

function updateAngleLabels(angles) {
  for (let i = 0; i < 4; i++) {
    const el = document.getElementById(`angle-${i}`);
    if (el && angles[i] !== undefined) {
      el.textContent = `${angles[i].toFixed(2)} rad`;
    }
  }
}

function setModeBadge(mode) {
  const badge = document.getElementById("mode-badge");
  if (!badge) return;
  if (mode === "hardware") {
    badge.textContent = "Hardware Mode";
    badge.classList.add("hardware");
  } else {
    badge.textContent = "Simulation Mode";
    badge.classList.remove("hardware");
  }
}

function showFeedback(data) {
  const box = document.getElementById("arm-feedback");
  if (box) {
    box.textContent = JSON.stringify(data, null, 2);
  }
  if (data && data.mode) {
    setModeBadge(data.mode);
  }
  if (data && Array.isArray(data.angles)) {
    roarmAngles = data.angles;
    updateAngleLabels(roarmAngles);
    drawArm3D(roarmAngles);
  }
}

function init3DArm() {
  const container = document.getElementById("roarm-3d-container");
  if (!container || typeof THREE === "undefined") {
    return;
  }

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0e14);

  camera = new THREE.PerspectiveCamera(
    45,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  );
  camera.position.set(50, 50, 80);
  camera.lookAt(scene.position);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AxesHelper(50));

  const material = new THREE.MeshBasicMaterial({ color: 0x3d8bfd });
  link1 = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 20, 12), material);
  link2 = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 18, 12), material.clone());
  link2.material.color.set(0x3dd68c);
  scene.add(link1);
  scene.add(link2);

  window.addEventListener("resize", () => {
    if (!container || !camera || !renderer) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });

  animate();
}

function drawArm3D(joint_rads) {
  if (!link1 || !link2) return;

  const base = joint_rads[0];
  const shoulder = joint_rads[1];
  const elbow = joint_rads[2];

  const H_base = 5;
  const L_base2shoulder = 5;
  const L1 = 20;
  const L2 = 18;

  const p0 = new THREE.Vector3(0, 0, H_base + L_base2shoulder);
  const p1 = new THREE.Vector3(
    L1 * Math.sin(shoulder) * Math.cos(base),
    L1 * Math.sin(shoulder) * Math.sin(base),
    p0.z + L1 * Math.cos(shoulder)
  );

  const total_angle = shoulder + elbow;
  const p2 = new THREE.Vector3(
    p1.x + L2 * Math.sin(total_angle) * Math.cos(base),
    p1.y + L2 * Math.sin(total_angle) * Math.sin(base),
    p1.z + L2 * Math.cos(total_angle)
  );

  const mid1 = new THREE.Vector3().addVectors(p0, p1).multiplyScalar(0.5);
  const dir1 = new THREE.Vector3().subVectors(p1, p0).normalize();
  link1.position.copy(mid1);
  link1.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir1);

  const mid2 = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
  const dir2 = new THREE.Vector3().subVectors(p2, p1).normalize();
  link2.position.copy(mid2);
  link2.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir2);
}

function animate() {
  requestAnimationFrame(animate);
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

function adjustJoint(joint, dir) {
  fetch("/arm_control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ joint: joint, dir: dir }),
  })
    .then((res) => res.json())
    .then(showFeedback)
    .catch((err) => {
      showFeedback({ error: String(err) });
    });
}

function getFeedback() {
  fetch("/arm_feedback")
    .then((res) => res.json())
    .then(showFeedback)
    .catch((err) => {
      showFeedback({ error: String(err) });
    });
}

function resetArm() {
  fetch("/arm_reset", { method: "POST" })
    .then((res) => res.json())
    .then(showFeedback)
    .catch((err) => {
      showFeedback({ error: String(err) });
    });
}

function toggleLed() {
  fetch("/arm_led", { method: "POST" })
    .then((res) => res.json())
    .then(showFeedback)
    .catch((err) => {
      showFeedback({ error: String(err) });
    });
}

function refreshStatus() {
  fetch("/arm_status")
    .then((res) => res.json())
    .then(showFeedback)
    .catch(() => {
      setModeBadge("simulation");
    });
}

window.addEventListener("DOMContentLoaded", () => {
  init3DArm();
  updateAngleLabels(roarmAngles);
  drawArm3D(roarmAngles);
  refreshStatus();
});
