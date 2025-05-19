let scene, camera, renderer, orbit, dragControls;
const objects = [];

function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xaaaaaa);

  const width = window.innerWidth;
  const height = window.innerHeight;

  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
  camera.position.set(0, 50, 100);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  document.getElementById('container').appendChild(renderer.domElement);

  orbit = new THREE.OrbitControls(camera, renderer.domElement);

  const ambient = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambient);

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(20, 50, 10);
  scene.add(dirLight);

  const grid = new THREE.GridHelper(200, 50);
  scene.add(grid);

  dragControls = new THREE.DragControls(objects, camera, renderer.domElement);
  dragControls.addEventListener('dragstart', function (event) { orbit.enabled = false; });
  dragControls.addEventListener('dragend', function (event) { orbit.enabled = true; });

  window.addEventListener('resize', onWindowResize);

  animate();
}

function onWindowResize() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

function loadSTL(buffer) {
  const loader = new THREE.STLLoader();
  const geometry = loader.parse(buffer);
  const material = new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.position.set(0, 0, 0);
  scene.add(mesh);
  objects.push(mesh);
  dragControls.transformGroup = true;
}

document.getElementById('file-input').addEventListener('change', function (event) {
  const files = event.target.files;
  Array.from(files).forEach(file => {
    const reader = new FileReader();
    reader.onload = function (e) {
      loadSTL(e.target.result);
    };
    reader.readAsArrayBuffer(file);
  });
});

init();
