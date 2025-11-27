from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os, json, base64

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DESIGNS_FILE = 'designs.json'
if not os.path.exists(DESIGNS_FILE):
    with open(DESIGNS_FILE, 'w') as f:
        json.dump([], f)

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Serve the main HTML
html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>3D Cake Customizer</title>
<style>
:root{--bg:#f7f7fb;--panel:#ffffff;--accent:#ff6b81}
html,body{height:100%;margin:0;font-family:Inter,system-ui,Arial;background:var(--bg)}
#app{display:grid;grid-template-columns:360px 1fr;gap:16px;height:100vh;padding:16px}
.panel{background:var(--panel);border-radius:12px;padding:12px;box-shadow:0 6px 18px rgba(10,10,20,0.06);overflow:auto}
h1{font-size:18px;margin:6px 0}
label{display:block;font-size:13px;margin:8px 0 4px}
input[type=range]{width:100%}
select,input,button{width:100%;padding:8px;border-radius:8px;border:1px solid #eee;margin-bottom:8px}
#renderer{width:100%;height:100%;border-radius:12px}
.row{display:flex;gap:8px}
.thumb{width:64px;height:64px;border-radius:8px;object-fit:cover;margin:6px;cursor:pointer;border:2px solid transparent}
.thumb.selected{border-color:var(--accent)}
.controls-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
footer{font-size:12px;color:#666;margin-top:8px}
</style>
</head>
<body>
<div id="app">
  <!-- left panel -->
  <aside class="panel">
    <h1>3D Cake Customizer</h1>
    <label>Shape</label>
    <select id="shape"><option value="round">Round</option><option value="square">Square</option></select>
    <label>Tiers (1-3)</label>
    <input id="tiers" type="range" min="1" max="3" value="1">
    <label>Size</label>
    <input id="size" type="range" min="0.6" max="1.6" step="0.05" value="1">
    <label>Frosting Color</label>
    <input id="color" type="color" value="#ffccdd">
    <label>Toppings</label>
    <div class="row">
      <select id="toppingType"><option value="sprinkles">Sprinkles</option><option value="cherry">Cherry</option><option value="none">None</option></select>
      <button id="applyTopping">Apply</button>
    </div>
    <label>Message (top)</label>
    <input id="message" placeholder="Happy Birthday!">
    <button id="applyMessage">Apply Message</button>
    <label>Upload image (maps to top)</label>
    <input id="upload" type="file" accept="image/*">
    <div class="controls-grid">
      <button id="save">Save Design</button>
      <button id="export">Export PNG</button>
    </div>
    <h1 style="margin-top:12px">Gallery (server)</h1>
    <div id="gallery"></div>
    <footer>Tip: drag to rotate, scroll to zoom. Saved designs are stored on the server.</footer>
  </aside>

  <!-- 3D viewer -->
  <main class="panel" id="viewer">
    <div id="renderer"></div>
  </main>
</div>

<script type="module">
import * as THREE from 'https://unpkg.com/three@0.152.2/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.152.2/examples/jsm/controls/OrbitControls.js';

// Scene setup
const container = document.getElementById('renderer');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf7f7fb);
const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
camera.position.set(2.5, 2, 3);
const renderer = new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer:true});
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
container.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Lights
scene.add(new THREE.HemisphereLight(0xffffff, 0x8888aa, 0.9));
const dir = new THREE.DirectionalLight(0xffffff, 0.6);
dir.position.set(5,10,2);
dir.castShadow = true;
scene.add(dir);

// Ground
const groundMat = new THREE.MeshPhysicalMaterial({color:0xffffff,roughness:1});
const ground = new THREE.Mesh(new THREE.PlaneGeometry(20,20), groundMat);
ground.rotation.x = -Math.PI/2;
ground.position.y = -0.01;
scene.add(ground);

// Cake
let cakeGroup = new THREE.Group();
scene.add(cakeGroup);

// Helper: canvas texture for top
function makeTopTexture({message = '', font = '48px sans-serif', bgcolor='#ffffff', image=null}){
  const size = 1024;
  const cv = document.createElement('canvas'); cv.width = cv.height = size;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = bgcolor; ctx.fillRect(0,0,size,size);
  if(image){
    const img = new Image();
    img.src = image;
    img.onload = ()=>{ ctx.drawImage(img,0,0,size,size); };
  }
  ctx.fillStyle = '#222'; ctx.textAlign = 'center'; ctx.font = font; ctx.fillText(message, size/2, size/2+16);
  const tex = new THREE.CanvasTexture(cv); tex.needsUpdate = true;
  return tex;
}

// Build cake
function buildCake(settings){
  cakeGroup.clear();
  const {shape, tiers, size, color, topping} = settings;
  const tierHeight = 0.35 * size;
  const baseRadius = 0.9 * size;
  const textures = {};
  textures.top = makeTopTexture({message:settings.message, bgcolor:color, image:settings.topImage});
  for(let i=0;i<tiers;i++){
    const y = i * (tierHeight + 0.02) + tierHeight/2;
    let geom;
    if(shape==='round') geom = new THREE.CylinderGeometry(baseRadius*(1-i*0.18), baseRadius*(1-i*0.18), tierHeight, 64);
    else geom = new THREE.BoxGeometry(baseRadius*2*(1-i*0.18), tierHeight, baseRadius*2*(1-i*0.18));
    const mat = new THREE.MeshStandardMaterial({color:color, metalness:0.05, roughness:0.6});
    if(i===tiers-1){
      if(shape==='square'){
        const mats=[]; for(let k=0;k<6;k++) mats.push(new THREE.MeshStandardMaterial({color:color,roughness:0.6}));
        mats[4]=new THREE.MeshStandardMaterial({map:textures.top});
        const mesh=new THREE.Mesh(geom,mats); mesh.position.y=y; cakeGroup.add(mesh);
      } else {
        const mesh = new THREE.Mesh(geom, mat); mesh.position.y=y; cakeGroup.add(mesh);
        const disk = new THREE.CircleGeometry(baseRadius*(1-i*0.18)-0.01,64);
        const diskMesh = new THREE.Mesh(disk,new THREE.MeshStandardMaterial({map:textures.top}));
        diskMesh.rotation.x=-Math.PI/2; diskMesh.position.y=y + tierHeight/2 + 0.001; cakeGroup.add(diskMesh);
      }
    } else { const mesh=new THREE.Mesh(geom, mat); mesh.position.y=y; cakeGroup.add(mesh);}
  }
  if(topping==='sprinkles'){
    const sprinkles=new THREE.Group();
    const count=160*size;
    for(let i=0;i<count;i++){
      const s=0.01+Math.random()*0.02;
      const g=new THREE.SphereGeometry(s,6,6);
      const m=new THREE.MeshStandardMaterial({color:new THREE.Color(Math.random(),Math.random(),Math.random()),metalness:0.1,roughness:0.7});
      const mesh=new THREE.Mesh(g,m);
      const angle=Math.random()*Math.PI*2;
      const r=(baseRadius-0.05*(Math.random()))*(0.6+Math.random()*0.4);
      mesh.position.x=Math.cos(angle)*r;
      mesh.position.z=Math.sin(angle)*r;
      mesh.position.y=tiers*(tierHeight)-(tierHeight/2)+0.02+Math.random()*0.02;
      sprinkles.add(mesh);
    }
    cakeGroup.add(sprinkles);
  } else if(topping==='cherry'){
    const cherry = new THREE.Mesh(new THREE.SphereGeometry(0.06,16,16), new THREE.MeshStandardMaterial({color:'#c11'}));
    cherry.position.set(0, tiers*(tierHeight)-(tierHeight/2)+0.07, 0);
    cakeGroup.add(cherry);
  }
  cakeGroup.position.y=0.15;
  const box=new THREE.Box3().setFromObject(cakeGroup);
  const sizeBox=box.getSize(new THREE.Vector3()).length();
  const center=box.getCenter(new THREE.Vector3());
  controls.target.copy(center);
  camera.position.set(center.x+sizeBox*1.2, center.y+sizeBox*0.8, center.z+sizeBox*1.2);
}

// Initial state
const state = {shape:'round', tiers:1, size:1, color:'#ffccdd', topping:'sprinkles', message:'', topImage:null};
buildCake(state);

const $ = id=>document.getElementById(id);
$('shape').addEventListener('change',e=>{state.shape=e.target.value;buildCake(state);});
$('tiers').addEventListener('input',e=>{state.tiers=parseInt(e.target.value);buildCake(state);});
$('size').addEventListener('input',e=>{state.size=parseFloat(e.target.value);buildCake(state);});
$('color').addEventListener('input',e=>{state.color=e.target.value;buildCake(state);});
$('applyTopping').addEventListener('click',()=>{state.topping=$('toppingType').value;buildCake(state);});
$('applyMessage').addEventListener('click',()=>{state.message=$('message').value;buildCake(state);});

$('upload').addEventListener('change', ev=>{
  const f=ev.target.files[0]; if(!f) return;
  const reader=new FileReader();
  reader.onload=()=>{state.topImage=reader.result; buildCake(state);}
  reader.readAsDataURL(f);
});

// Save to server
$('save').addEventListener('click', async ()=>{
  const res = await fetch('/save_design',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(state)});
  const data = await res.json();
  alert(data.message);
  loadGallery();
});

// Export PNG
$('export').addEventListener('click', ()=>{
  renderer.render(scene,camera);
  const url = renderer.domElement.toDataURL('image/png');
  const a=document.createElement('a'); a.href=url; a.download='cake.png'; a.click();
});

// Load gallery from server
async function loadGallery(){
  const wrap=$('gallery'); wrap.innerHTML='';
  const res=await fetch('/gallery');
  const designs=await res.json();
  designs.forEach(d=>{
    const img=document.createElement('img');
    img.src=d.topImagePath?d.topImagePath:d.thumbnail;
    img.className='thumb';
    img.title=new Date(d.savedAt||Date.now()).toLocaleString();
    wrap.appendChild(img);
  });
}
loadGallery();

function onWindowResize(){camera.aspect=container.clientWidth/container.clientHeight;camera.updateProjectionMatrix();renderer.setSize(container.clientWidth,container.clientHeight);}
window.addEventListener('resize', onWindowResize);
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);}
animate();
</script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(html)

@app.route('/save_design', methods=['POST'])
def save_design():
    data = request.get_json()
    if data.get('topImage'):
        if data['topImage'].startswith('data:image'):
            header, encoded = data['topImage'].split(',',1)
            filename = f"{len(os.listdir(UPLOAD_FOLDER))}_{int(request.content_length)}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath,'wb') as f:
                f.write(base64.b64decode(encoded))
            data['topImagePath'] = f'/uploads/{filename}'
            data.pop('topImage')
    with open(DESIGNS_FILE,'r') as f: designs = json.load(f)
    data['savedAt'] = data.get('savedAt') or int(request.content_length)
    designs.append(data)
    with open(DESIGNS_FILE,'w') as f: json.dump(designs,f)
    return jsonify({'status':'ok','message':'Design saved on server!'})

@app.route('/gallery')
def gallery():
    with open(DESIGNS_FILE,'r') as f: designs=json.load(f)
    return jsonify(designs)

if __name__ == '__main__':
    app.run(debug=True)
