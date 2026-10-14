import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';

const el = id => document.getElementById(id);
const viewport = el('viewport');
const renderer = new THREE.WebGLRenderer({antialias:true, powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
viewport.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color('#a9c7da');
const camera = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, .05, 20000);
const orbit = new OrbitControls(camera, renderer.domElement);
orbit.enableDamping = true;
const polygons = new THREE.Group(), splats = new THREE.Group();
scene.add(polygons, splats);
const splatMaterial = new THREE.ShaderMaterial({
  uniforms:{alphaFactor:{value:81}}, transparent:true, depthWrite:false,
  side:THREE.DoubleSide, toneMapped:false,
  vertexShader:`attribute vec4 rgba;attribute vec3 bary;varying vec4 vRGBA;varying vec3 vBary;
  void main(){vRGBA=rgba;vBary=bary;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`precision highp float;varying vec4 vRGBA;varying vec3 vBary;uniform float alphaFactor;
  void main(){float product=vBary.x*vBary.y*vBary.z;if(product<=0.0||vRGBA.a<=0.0)discard;
  gl_FragColor=vec4(vRGBA.rgb,min(.99,vRGBA.a*product*alphaFactor));}`
});
let ready=false, flying=false, loaded=0, metadata=null;
const keys=new Set(), clock=new THREE.Clock(), yawPitch=new THREE.Euler(0,0,0,'YXZ');
const forward=new THREE.Vector3(), right=new THREE.Vector3(), direction=new THREE.Vector3();
const loader=new THREE.TextureLoader();
async function buffer(path){const r=await fetch(path);if(!r.ok)throw Error(`データ読み込み失敗: ${path}`);return r.arrayBuffer();}
function meshGeometry(data){
  const h=new Uint32Array(data,0,4), n=h[2], f=h[3];
  if(h[0]!==0x56334452||h[1]!==1||data.byteLength!==16+32*n+12*f)throw Error('ポリゴンデータ長の不一致');
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(data,16,3*n),3));
  g.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(data,16+12*n,2*n),2));
  g.setAttribute('normal',new THREE.BufferAttribute(new Float32Array(data,16+20*n,3*n),3));
  g.setIndex(new THREE.BufferAttribute(new Uint32Array(data,16+32*n,3*f),1));g.computeBoundingSphere();return g;
}
function splatGeometry(data){
  const h=new Uint32Array(data,0,4), n=h[2];
  if(h[0]!==0x53534452||h[1]!==1||data.byteLength!==16+40*n)throw Error('Splatデータ長の不一致');
  const positions=new Float32Array(data,16,9*n), colors=new Uint8Array(data,16+36*n,4*n);
  const visible=[];for(let i=0;i<n;i++)if(colors[4*i+3]>0)visible.push(i);
  const xyz=new Float32Array(visible.length*9), rgba=new Uint8Array(visible.length*12), bary=new Uint8Array(visible.length*9);
  for(let k=0;k<visible.length;k++){const i=visible[k];xyz.set(positions.subarray(9*i,9*i+9),9*k);
    for(let v=0;v<3;v++){rgba.set(colors.subarray(4*i,4*i+4),12*k+4*v);bary[9*k+3*v+v]=255;}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(xyz,3));
  g.setAttribute('rgba',new THREE.BufferAttribute(rgba,4,true));g.setAttribute('bary',new THREE.BufferAttribute(bary,3,true));
  g.computeBoundingSphere();return g;
}
async function loadTile(tile){
  const [geometry, splatData, texture]=await Promise.all([buffer(tile.mesh),buffer(tile.splats),loader.loadAsync(tile.texture)]);
  texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=true;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  const p=new THREE.Mesh(meshGeometry(geometry),new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide}));
  p.name=tile.source;polygons.add(p);
  const s=new THREE.Mesh(splatGeometry(splatData),splatMaterial);s.name=tile.source;s.renderOrder=1;splats.add(s);
  loaded++;el('status').textContent=`読み込み ${loaded} / ${metadata.tiles.length} タイル`;
}
function reset(){
  if(!metadata)return;
  const lo=new THREE.Vector3(...metadata.bounds.min), hi=new THREE.Vector3(...metadata.bounds.max);
  const center=lo.clone().add(hi).multiplyScalar(.5), span=hi.clone().sub(lo);
  const r=Math.max(span.x,span.z,span.y,20);
  camera.position.copy(center).add(new THREE.Vector3(r*.55,r*.65,r*.8));camera.lookAt(center);
  orbit.target.copy(center);orbit.update();yawPitch.setFromQuaternion(camera.quaternion,'YXZ');
}
function setFlying(value){
  flying=value;orbit.enabled=!value;keys.clear();yawPitch.setFromQuaternion(camera.quaternion,'YXZ');
  el('fly').textContent=`自由移動 ${value?'ON':'OFF'}`;el('fly').classList.toggle('active',value);
  el('lockHint').textContent=value?'画面クリックでマウス視点操作 · Esc解除':'ドラッグで回転 · ホイールでズーム';
  if(!value&&document.pointerLockElement)document.exitPointerLock();
  if(!value){const d=camera.getWorldDirection(new THREE.Vector3());orbit.target.copy(camera.position).addScaledVector(d,30);orbit.update();}
}
el('polygons').addEventListener('change',e=>polygons.visible=e.target.checked);
el('splats').addEventListener('change',e=>splats.visible=e.target.checked);
el('fly').addEventListener('click',()=>setFlying(!flying));el('reset').addEventListener('click',reset);
el('speed').addEventListener('input',e=>el('speedValue').textContent=`${e.target.value} m/s`);
el('opacity').addEventListener('input',e=>{splatMaterial.uniforms.alphaFactor.value=+e.target.value;el('opacityValue').textContent=e.target.value;});
renderer.domElement.addEventListener('click',()=>{if(flying)renderer.domElement.requestPointerLock();});
document.addEventListener('mousemove',e=>{if(!flying||document.pointerLockElement!==renderer.domElement)return;
  yawPitch.y-=e.movementX*.002;yawPitch.x=THREE.MathUtils.clamp(yawPitch.x-e.movementY*.002,-Math.PI*.495,Math.PI*.495);
  camera.quaternion.setFromEuler(yawPitch);});
document.addEventListener('keydown',e=>{if(e.target instanceof HTMLInputElement)return;
  if(e.code==='Escape'&&document.pointerLockElement){document.exitPointerLock();keys.clear();}
  if(e.code==='KeyF'&&!e.repeat)setFlying(!flying);
  if(flying&&['KeyW','KeyA','KeyS','KeyD','KeyE','KeyQ','Space','ControlLeft','ShiftLeft','ShiftRight'].includes(e.code)){e.preventDefault();keys.add(e.code);}});
document.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>keys.clear());
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
renderer.setAnimationLoop(()=>{
  const dt=Math.min(clock.getDelta(),.1);
  if(flying){camera.getWorldDirection(forward);forward.y=0;forward.normalize();right.crossVectors(forward,camera.up).normalize();direction.set(0,0,0);
    if(keys.has('KeyW'))direction.add(forward);if(keys.has('KeyS'))direction.sub(forward);if(keys.has('KeyD'))direction.add(right);if(keys.has('KeyA'))direction.sub(right);
    if(keys.has('KeyE')||keys.has('Space'))direction.y+=1;if(keys.has('KeyQ')||keys.has('ControlLeft'))direction.y-=1;
    const speed=+el('speed').value*((keys.has('ShiftLeft')||keys.has('ShiftRight'))?4:1);if(direction.lengthSq())camera.position.addScaledVector(direction.normalize(),dt*speed);
  }else orbit.update();
  renderer.render(scene,camera);
});
window.r3dViewer={snapshot:()=>({ready,loaded,flying,pointerLocked:document.pointerLockElement===renderer.domElement,
  position:camera.position.toArray(),quaternion:camera.quaternion.toArray(),polygonsVisible:polygons.visible,splatsVisible:splats.visible,
  polygonTiles:polygons.children.length,splatTiles:splats.children.length,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles})};
try{
  const r=await fetch('./scene.json');if(!r.ok)throw Error('scene.jsonを読み込めません');metadata=await r.json();
  document.title=metadata.title;el('title').textContent=metadata.title;el('location').textContent=`${metadata.origin[0].toFixed(6)}, ${metadata.origin[1].toFixed(6)}`;
  const total=metadata.totals;el('counts').textContent=`${total.tiles} タイル · ポリゴン ${total.meshTriangles.toLocaleString()} 面 · Splat ${total.splatRecords.toLocaleString()}`;
  reset();const queue=metadata.tiles.slice();await Promise.all(Array.from({length:4},async()=>{while(queue.length)await loadTile(queue.shift());}));
  renderer.compile(scene,camera);ready=true;el('status').textContent='元のテクスチャ付きポリゴン + Splat · 読み込み完了';
}catch(error){el('error').textContent=String(error.message||error);el('status').textContent='読み込みに失敗しました';console.error(error);}
