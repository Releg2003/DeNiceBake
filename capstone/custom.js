const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, (window.innerWidth-300)/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth-300, window.innerHeight);
document.getElementById("preview").appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
camera.position.set(3,3,4);
controls.update();

const light = new THREE.DirectionalLight(0xffffff,1);
light.position.set(5,5,5);
scene.add(light);

let cake;
function createCake() {
    if(cake) scene.remove(cake);
    const shape = document.getElementById('shape').value;
    const size = document.getElementById('size').value;
    const flavor = document.getElementById('flavor').value;

    const colorMap = { vanilla:0xf3e5ab, chocolate:0x5c3a21, strawberry:0xffb6c1 };
    let height = 1;
    let radius = size==="small"?0.8:size==="medium"?1.1:1.4;

    let geometry;
    if(shape==="round") geometry = new THREE.CylinderGeometry(radius,radius,height,32);
    else geometry = new THREE.BoxGeometry(radius*2,height,radius*2);

    const material = new THREE.MeshStandardMaterial({color: colorMap[flavor]});
    cake = new THREE.Mesh(geometry, material);
    scene.add(cake);
}

// Update cake on input change
['shape','size','flavor'].forEach(id=>{
    document.getElementById(id).addEventListener('change', createCake);
});

createCake();

function animate(){
    requestAnimationFrame(animate);
    if(cake) cake.rotation.y +=0.01;
    renderer.render(scene,camera);
}
animate();

window.addEventListener('resize',()=>{
    camera.aspect=(window.innerWidth-300)/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth-300,window.innerHeight);
});
