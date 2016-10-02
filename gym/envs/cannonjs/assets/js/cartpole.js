var world;
var mass;
var timeStep = 1 / 60; // TODO: Consider half-steps for greater accuracy
var camera;
var scene;
var renderer;
var meshes = [];
var bodies = [];
var constraints = [];
var iter = 0;
var direction = 1;
var queue = new Queue;
// Cart Dimensions
var cartX = 4;
var cartY = 2;
var cartZ = 1;

// Pendulum Dimensions
var pendX = 0.5;
var pendY = 0.5;
var pendZ = 4;

var sepDist = 0.05; // Separation between cart/pole to prevent friction

initThree();
initCannon();

function initThree() {
    // Scene
    scene = new THREE.Scene();

    // Camera
    camera = new THREE.PerspectiveCamera(
        75, // Field of View
        window.innerWidth / window.innerHeight, // Aspect
        1, // Near frustum plane
        100 // Far frustum plane
    );

    camera.position.z = 4;
    camera.position.y = 12;
    camera.position.x = 0;
    camera.up = new CANNON.Vec3(0, 0, 1);
    camera.lookAt(new CANNON.Vec3(0,0,0));

    scene.add(camera);

    ////////////
    // Geometry
    var railGeometry = new THREE.BoxBufferGeometry(40, 0.2, 0.2);
    var railMaterial = new THREE.MeshPhongMaterial({
        color: 0x2E5FFF,
        specular: 0x009900,
        shininess: 30,
        shading: THREE.SmoothShading
    });
    var railMesh = new THREE.Mesh(railGeometry, railMaterial);
    scene.add(railMesh);

    // Cart
    var cartGeometry = new THREE.BoxBufferGeometry(
        cartX, cartY, cartZ
    );
    var texture = new THREE.TextureLoader()
        .load('textures/crate.gif');
    var cartMaterial = new THREE.MeshBasicMaterial(
        { map: texture }
    );
    var cartMesh = new THREE.Mesh(cartGeometry, cartMaterial);
    scene.add(cartMesh);
    meshes.push(cartMesh);

    // Pendulum
    pendulumGeometry = new THREE.BoxBufferGeometry(
        pendX, pendY, pendZ
    );
    pendulumMesh = new THREE.Mesh( pendulumGeometry, cartMaterial );
    pendulumMesh.position.x = 0
    pendulumMesh.position.y = (cartY / 2) + (pendY / 2) + sepDist;
    pendulumMesh.position.z = (pendZ / 2) - (cartZ / 2);
    scene.add(pendulumMesh);
    meshes.push(pendulumMesh);

    /////////
    // Lights
    scene.add(new THREE.AmbientLight(0x111111));
    var directionalLight = new THREE.DirectionalLight(0xffffff, 0.3);
    directionalLight.position.x = 0;
    directionalLight.position.y = 5;
    directionalLight.position.z = 2;
    directionalLight.position.normalize();
    scene.add( directionalLight );

    // Leave alone
    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild(renderer.domElement);
    window.addEventListener('resize', onWindowResize, false);
}

function initCannon() {
    world = new CANNON.World();
    world.gravity.set(0, 0, -9.81);
    world.broadphase = new CANNON.NaiveBroadphase();
    world.solver.iterations = 5;

    reset();
    /////////
    // Bodys

    // Cart
    shape = new CANNON.Box(
        new CANNON.Vec3(cartX / 2.0, cartY / 2.0, cartZ / 2.0)
    );
    cartBody = new CANNON.Body({
        mass: 4,
        linearFactor: new CANNON.Vec3(1, 0, 0), // Restrict motion to x axis
        angularFactor: new CANNON.Vec3(0, 0, 0) // Prevent rotation
    });
    cartBody.addShape(shape);
    cartBody.linearDamping = 0.9;
    world.addBody(cartBody);
    bodies.push(cartBody);

    // Pendulum
    pendulumShape = new CANNON.Box(
        new CANNON.Vec3(pendX / 2.0, pendY / 2.0, pendZ / 2.0)
    );
    pendulumBody = new CANNON.Body({
        mass: 1,
        angularFactor: new CANNON.Vec3(0, 1, 0)
    });
    pendulumBody.addShape(pendulumShape);
    pendulumBody.position.x = 0
    pendulumBody.position.y = (cartY / 2.0) + (pendY / 2.0);
    pendulumBody.position.z = (pendZ / 2.0) - (cartZ / 2.0);
    pendulumBody.angularDamping = 0.01;
    pendulumBody.linearDamping = 0.01;
    world.addBody(pendulumBody);
    bodies.push(pendulumBody);

    // Update mesh position to match bodies
    syncViewWithPhysics();

    ///////////////
    // Constraints

    var axis = new CANNON.Vec3(0, 1, 0);
    var p2p = new CANNON.PointToPointConstraint(
        cartBody,
        new CANNON.Vec3(0, (cartY / 2.0) + (sepDist / 2.0) , 0),
        pendulumBody,
        new CANNON.Vec3(0, -((pendY / 2.0) + (sepDist / 2.0)), -(pendZ / 2.0) + (cartZ / 2.0))
    );

    world.addConstraint(p2p);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

function syncViewWithPhysics() {
    // Copy coordinates from Cannon.js to Three.js
    for (var i = 0; i < meshes.length; i++) {
        var mesh = meshes[i];
        var body = bodies[i];
        mesh.position.copy(body.position);
        mesh.quaternion.copy(body.quaternion);
    }
}

function updatePhysics() {
    // Step the physics world
    world.step(timeStep);
    syncViewWithPhysics();
}

function step(action) {
    setTimeout(function(){
        runOneStep(action);
    }, 0);
}

function reset() {

    // // Clean out old objects
    // for (var i = 0; i < constraints.length; i++) {
    //     var constraint = constraints[i];
    //     world.removeConstraint(constraint);
    // }

    // for (var i = 0; i < bodies.length; i++) {
    //     var body = bodies[i];
    //     world.removeBody(body);
    // }

}

function runOneStep(action) {

    iter++;

    // Apply force to center
    var direction = action ? -1 : 1;
    var bodyPoint = new CANNON.Vec3(0, 0, 0);
    var newtons = 24 * direction;
    var force = new CANNON.Vec3(newtons, 0, 0);
    bodies[0].applyForce(force, bodyPoint);

    var axis = new CANNON.Vec3(0, 1, 0);
    var axisAndAngle = bodies[1].quaternion.toAxisAngle(axis);
    var angle = axisAndAngle[1];
    var output = {
        x: meshes[0].position.x,
        theta: angle
    };

    queue.enqueue(output);

    updatePhysics();
    renderer.render( scene, camera );
}

// Debug by opening cartpole.html locally and uncommenting
// window.setInterval(function() {runOneStep();}, 16);
