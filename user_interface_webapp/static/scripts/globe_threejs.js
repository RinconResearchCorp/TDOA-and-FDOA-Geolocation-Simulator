import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import ThreeGlobe from 'three-globe';

let scene, camera, renderer, globe, controls;

function init() {
    // create a scene
    scene = new THREE.Scene();

    // create a camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 2;

    // renderer
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('three-container').appendChild(renderer.domElement);

    // globe rendering
    globe = new ThreeGlobe()
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg');
    scene.add(globe);

    // add controls for the globe
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableZoom = true;

    // resize listener 
    window.addEventListener('resize', onWindowResize, false);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

export { init, animate, globe };