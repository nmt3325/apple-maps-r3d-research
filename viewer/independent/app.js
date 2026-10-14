import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';
import {frameAt,coordinateAt,planTiles,validCoordinate} from './stream-planner.mjs';
import {TileStream} from './stream-controller.mjs';
import {loadStreamModel,renderStreamModel,disposeStreamModel} from './stream-scene.mjs';

const el = id => document.getElementById(id);
const viewport = el('viewport');
const panel=document.querySelector('.panel');
function collapsePanel(value){panel.classList.toggle('collapsed',value);el('panel-toggle').setAttribute('aria-expanded',String(!value));el('panel-toggle').textContent=value?'操作':'閉じる';}
collapsePanel(matchMedia('(pointer:coarse)').matches);
el('panel-toggle').addEventListener('click',()=>collapsePanel(!panel.classList.contains('collapsed')));
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
let stream=null,streamFrame=null,streamSupported=false,viewDistance=250,rebases=0;
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
  const [geometry, splatData, texture]=await Promise.all([buffer(tile.mesh),buffer(tile.splats),tile.texture?loader.loadAsync(tile.texture):null]);
  if(tile.triangles){
    if(!texture)throw Error('ポリゴンの元テクスチャがありません');
    texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=true;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
    const p=new THREE.Mesh(meshGeometry(geometry),new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide}));
    p.name=tile.source;polygons.add(p);
  }
  const s=new THREE.Mesh(splatGeometry(splatData),splatMaterial);s.name=tile.source;s.renderOrder=1;splats.add(s);
  loaded++;el('status').textContent=`読み込み ${loaded} / ${metadata.tiles.length} タイル`;
}
function reset(){
  if(!metadata)return;
  if(stream){camera.position.set(0,100,160);orbit.target.set(0,25,0);camera.lookAt(orbit.target);orbit.update();yawPitch.setFromQuaternion(camera.quaternion,'YXZ');stream.lastPlan=0;return;}
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
const picker=el('location-picker'),latInput=el('pick-lat'),lonInput=el('pick-lon'),radiusInput=el('pick-radius');
let map=null,marker=null,area=null,lastPlan=null,activeJob=null;
function updateMapPoint(lat,lon){
  lat=+lat;lon=+lon;if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>85.05112878||Math.abs(lon)>180)return;
  latInput.value=lat.toFixed(7);lonInput.value=lon.toFixed(7);
  if(map){const point=[lat,lon],radius=Number.isFinite(+radiusInput.value)&&+radiusInput.value>0?+radiusInput.value:40;
    if(marker)marker.setLatLng(point);else marker=L.marker(point,{draggable:true}).addTo(map).on('dragend',e=>updateMapPoint(e.target.getLatLng().lat,e.target.getLatLng().lng));
    if(area)area.setLatLng(point);else area=L.circle(point,{radius,color:'#55ddc4',weight:2,fillOpacity:.09}).addTo(map);area.setRadius(radius);}
  lastPlan=null;el('fetch-location').disabled=true;el('tile-preview').textContent='対象タイル数を再計算してください。';
}
el('pick-location').addEventListener('click',()=>{
  picker.hidden=false;el('error').textContent='';
  if(!map){map=L.map('pick-map').setView([metadata.origin[0],metadata.origin[1]],16);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
    map.on('click',e=>updateMapPoint(e.latlng.lat,e.latlng.lng));
  }
  const current=stream?coordinateAt(streamFrame,camera.position.toArray()):{lat:metadata.origin[0],lon:metadata.origin[1]};
  if(stream)radiusInput.value=viewDistance;updateMapPoint(current.lat,current.lon);if(stream)map.setView([current.lat,current.lon],16);
  requestAnimationFrame(()=>map.invalidateSize());
});
el('close-picker').addEventListener('click',()=>picker.hidden=true);
for(const input of [latInput,lonInput,radiusInput])input.addEventListener('input',()=>{lastPlan=null;el('fetch-location').disabled=true;el('tile-preview').textContent='対象タイル数を再計算してください。';
  if(input===latInput||input===lonInput){const lat=+latInput.value,lon=+lonInput.value;if(Number.isFinite(lat)&&Number.isFinite(lon)&&Math.abs(lat)<=85.05112878&&Math.abs(lon)<=180&&map){marker?.setLatLng([lat,lon]);area?.setLatLng([lat,lon]);}}
  else if(area&&Number.isFinite(+radiusInput.value)&&+radiusInput.value>0)area.setRadius(+radiusInput.value);});
for(const input of [latInput,lonInput])input.addEventListener('change',()=>{const lat=+latInput.value,lon=+lonInput.value;if(map&&Number.isFinite(lat)&&Number.isFinite(lon)&&Math.abs(lat)<=85.05112878&&Math.abs(lon)<=180)map.panTo([lat,lon]);});
async function postJSON(path,body){const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await response.json();if(!response.ok)throw Error(data.error||'サーバーで処理できませんでした');return data;}
function selection(){const lat=+latInput.value,lon=+lonInput.value,radius=+radiusInput.value;
 if(!Number.isFinite(lat)||!Number.isFinite(lon)||!Number.isFinite(radius))throw Error('緯度・経度・範囲を入力してください');
 if(Math.abs(lat)>85.05112878||Math.abs(lon)>180||radius<(streamSupported?80:5)||radius>(streamSupported?600:300))throw Error(streamSupported?'緯度±85.05、経度±180、描画距離80〜600mで指定してください':'緯度±85.05、経度±180、範囲5〜300mで指定してください');
 return {lat,lon,radiusMeters:radius,zoom:20};}
el('preview-area').addEventListener('click',async()=>{const button=el('preview-area');button.disabled=true;lastPlan=null;el('fetch-location').disabled=true;
 try{const selected=selection();
   if(streamSupported){const leaves=planTiles(frameAt(selected.lat,selected.lon),{position:[0,100,160],yaw:0,pitch:-.45,fov:camera.fov*Math.PI/180,aspect:camera.aspect},selected.radiusMeters);
     lastPlan=selected;el('tile-preview').textContent=`近くから順に ${leaves.length} の表示範囲を読み込みます。移動先も自動で追加します。`;
     el('fetch-location').textContent='この場所から探索';el('fetch-location').disabled=false;el('picker-message').textContent='全高さ層を読み込みながら移動できます。';return;}
   const plan=await postJSON('/api/plan',selected);if(selection().lat!==selected.lat||selection().lon!==selected.lon||selection().radiusMeters!==selected.radiusMeters)throw Error('位置が変わったため、タイル数を再計算してください');lastPlan=plan;el('tile-preview').textContent=`z${plan.zoom} · 平面${plan.tileCount}タイル + 全高さ層 · 取得範囲 ±${plan.radiusMeters}m`;
   el('fetch-location').textContent=`全高さ層を取得して3D表示`;el('fetch-location').disabled=false;el('picker-message').textContent='この範囲のR3D取得と復号を開始できます。';}
 catch(error){el('tile-preview').textContent=String(error.message||error);el('picker-message').textContent='範囲を調整して再計算してください。';}
 finally{button.disabled=false;}});
el('fetch-location').addEventListener('click',async()=>{if(!lastPlan)return;const button=el('fetch-location');button.disabled=true;el('preview-area').disabled=true;
 try{if(streamSupported){const selected=selection();relocate(selected.lat,selected.lon,selected.radiusMeters);picker.hidden=true;el('preview-area').disabled=false;button.disabled=false;return;}
   const job=await postJSON('/api/jobs',selection());activeJob=job.id;el('picker-message').textContent=`平面${job.tileCount}タイルの全高さ層を取得中…`;
   while(true){await new Promise(resolve=>setTimeout(resolve,1200));const response=await fetch(`/api/jobs/${encodeURIComponent(activeJob)}`);const state=await response.json();
     if(state.status==='failed')throw Error(state.message||'取得または復号に失敗しました');
     el('picker-message').textContent=state.status==='ready'?'3Dシーンを開いています…':`${state.stage||'取得中'} · ${state.tileCount}タイル`;
     if(state.status==='ready'){window.location.assign(state.viewer);return;}}
 }catch(error){el('picker-message').textContent=String(error.message||error);button.disabled=false;el('preview-area').disabled=false;}
});
el('fly').addEventListener('click',()=>setFlying(!flying));el('reset').addEventListener('click',reset);
el('speed').addEventListener('input',e=>el('speedValue').textContent=`${e.target.value} m/s`);
el('opacity').addEventListener('input',e=>{splatMaterial.uniforms.alphaFactor.value=+e.target.value;el('opacityValue').textContent=e.target.value;});
renderer.domElement.addEventListener('click',()=>{if(flying&&matchMedia('(pointer:fine)').matches)renderer.domElement.requestPointerLock();});
document.addEventListener('mousemove',e=>{if(!flying||document.pointerLockElement!==renderer.domElement)return;
  yawPitch.y-=e.movementX*.002;yawPitch.x=THREE.MathUtils.clamp(yawPitch.x-e.movementY*.002,-Math.PI*.495,Math.PI*.495);
  camera.quaternion.setFromEuler(yawPitch);});
document.addEventListener('keydown',e=>{if(e.target instanceof HTMLInputElement)return;
  if(e.code==='Escape'&&document.pointerLockElement){document.exitPointerLock();keys.clear();}
  if(e.code==='KeyF'&&!e.repeat)setFlying(!flying);
  if(flying&&['KeyW','KeyA','KeyS','KeyD','KeyE','KeyQ','Space','ControlLeft','ShiftLeft','ShiftRight'].includes(e.code)){e.preventDefault();keys.add(e.code);}});
document.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>keys.clear());
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
document.addEventListener('visibilitychange',()=>{keys.clear();stream?.setActive(!document.hidden);});
el('stream-enabled').addEventListener('change',e=>{if(!stream)return;stream.enabled=e.target.checked;stream.setActive(e.target.checked&&!document.hidden);el('status').textContent=e.target.checked?'移動先を読み込み中…':'自動読み込みを停止しました';});
el('retry-stream').addEventListener('click',()=>stream?.retry());
el('distance').addEventListener('input',e=>{viewDistance=+e.target.value;el('distanceValue').textContent=`${viewDistance} m`;if(stream)stream.lastPlan=0;});
let touchLook=null;
renderer.domElement.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'&&flying){touchLook={id:e.pointerId,x:e.clientX,y:e.clientY};renderer.domElement.setPointerCapture(e.pointerId);}});
renderer.domElement.addEventListener('pointermove',e=>{if(touchLook?.id!==e.pointerId)return;yawPitch.y-=(e.clientX-touchLook.x)*.005;yawPitch.x=THREE.MathUtils.clamp(yawPitch.x-(e.clientY-touchLook.y)*.005,-Math.PI*.495,Math.PI*.495);camera.quaternion.setFromEuler(yawPitch);touchLook.x=e.clientX;touchLook.y=e.clientY;});
for(const event of ['pointerup','pointercancel'])renderer.domElement.addEventListener(event,()=>touchLook=null);
for(const button of document.querySelectorAll('[data-move]')){
  button.addEventListener('pointerdown',e=>{e.preventDefault();if(!flying)setFlying(true);keys.add(button.dataset.move);button.setPointerCapture(e.pointerId);});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(event,()=>keys.delete(button.dataset.move));
}
function cameraState(){camera.getWorldDirection(forward);return {position:camera.position.toArray(),yaw:Math.atan2(forward.x,-forward.z),pitch:Math.asin(THREE.MathUtils.clamp(forward.y,-1,1)),fov:camera.fov*Math.PI/180,aspect:camera.aspect};}
function streamStatus(state){
  el('counts').textContent=`${state.loaded} タイル · ${Math.round(state.residentBytes/1024/1024)} MiB · 読み込み ${state.pending} 件`;
  el('error').textContent=state.error;el('retry-stream').hidden=!state.error;
  if(!state.enabled)return;
  if(state.authFailed){el('status').textContent='取得設定の更新が必要です';return;}
  el('status').textContent=state.pending||state.queued?'移動先を読み込み中…':state.loaded?'視界内のモデルを表示中':'この範囲には対応する3Dデータがありません';
}
function startStreaming(){
  document.title='Apple Maps · 3D explorer';el('title').textContent=document.title;
  streamFrame=frameAt(metadata.origin[0],metadata.origin[1]);
  stream=new TileStream({frame:()=>streamFrame,camera:cameraState,distance:()=>viewDistance,
    load:(tile,signal)=>loadStreamModel(tile,signal,{frame:()=>streamFrame,renderer,polygons,splats,splatMaterial,meshGeometry,splatGeometry}),
    render:(model,visible,fine)=>renderStreamModel(model,visible,fine,streamFrame,splatMaterial.uniforms.alphaFactor.value),
    dispose:disposeStreamModel,status:streamStatus,reduceDistance:()=>{viewDistance=Math.max(80,viewDistance*.8);el('distance').value=viewDistance;el('distanceValue').textContent=`${Math.round(viewDistance)} m`;}});
  if(innerWidth<700)stream.budget=96*1024*1024;
  el('stream-controls').hidden=false;el('stream-enabled').checked=true;el('stream-enabled').disabled=false;
  el('distance').value=viewDistance;el('distanceValue').textContent=`${viewDistance} m`;
  radiusInput.min=80;radiusInput.max=600;radiusInput.value=viewDistance;
  el('radius-label').textContent='描画距離（m）';el('tile-preview').textContent='移動先を自動で読み込みます。';
  el('fetch-location').textContent='この場所から探索';el('picker-help').textContent='場所を選ぶと、その位置から移動しながら探索できます。';
  reset();ready=true;stream.update();
}
function relocate(lat,lon,distance=viewDistance){
  if(!validCoordinate(lat,lon))throw Error('緯度・経度が範囲外です');
  stream.clear();streamFrame=frameAt(lat,lon);metadata.origin=[lat,lon,0];viewDistance=distance;
  el('stream-enabled').checked=true;stream.enabled=true;stream.setActive(!document.hidden);
  el('distance').value=viewDistance;el('distanceValue').textContent=`${viewDistance} m`;
  el('location').textContent=`${lat.toFixed(6)}, ${lon.toFixed(6)}`;reset();stream.update();
  const url=new URL(location.href);url.searchParams.set('lat',lat.toFixed(7));url.searchParams.set('lon',lon.toFixed(7));history.replaceState(null,'',url);
}
renderer.setAnimationLoop(()=>{
  const dt=Math.min(clock.getDelta(),.1);
  if(flying){camera.getWorldDirection(forward);forward.y=0;forward.normalize();right.crossVectors(forward,camera.up).normalize();direction.set(0,0,0);
    if(keys.has('KeyW'))direction.add(forward);if(keys.has('KeyS'))direction.sub(forward);if(keys.has('KeyD'))direction.add(right);if(keys.has('KeyA'))direction.sub(right);
    if(keys.has('KeyE')||keys.has('Space'))direction.y+=1;if(keys.has('KeyQ')||keys.has('ControlLeft'))direction.y-=1;
    const speed=+el('speed').value*((keys.has('ShiftLeft')||keys.has('ShiftRight'))?4:1);if(direction.lengthSq())camera.position.addScaledVector(direction.normalize(),dt*speed);
  }else orbit.update();
  if(stream){
    if(Math.hypot(camera.position.x,camera.position.z)>3000){const current=coordinateAt(streamFrame,camera.position.toArray()),old=camera.position.clone();
      stream.clear();streamFrame=frameAt(current.lat,current.lon);metadata.origin=[current.lat,current.lon,0];camera.position.set(0,old.y,0);orbit.target.sub(new THREE.Vector3(old.x,0,old.z));rebases++;}
    stream.tick(performance.now());
    const current=coordinateAt(streamFrame,camera.position.toArray());el('location').textContent=`${current.lat.toFixed(6)}, ${current.lon.toFixed(6)}`;
  }
  renderer.render(scene,camera);
});
window.r3dViewer={snapshot:()=>({ready,loaded:stream?stream.models.size:loaded,flying,pointerLocked:document.pointerLockElement===renderer.domElement,
  position:camera.position.toArray(),quaternion:camera.quaternion.toArray(),polygonsVisible:polygons.visible,splatsVisible:splats.visible,
  origin:metadata?.origin,coordinate:stream?coordinateAt(streamFrame,camera.position.toArray()):null,rebases,stream:stream?.snapshot(),
  expectedPolygonTiles:stream?[...stream.models.values()].filter(e=>e.model.polygon).length:metadata?.tiles.filter(t=>t.triangles>0).length,polygonTiles:polygons.children.length,splatTiles:splats.children.length,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles})};
try{
  const r=await fetch('./scene.json');if(!r.ok)throw Error('scene.jsonを読み込めません');metadata=await r.json();
  if(metadata.webStreaming){const status=await (await fetch('/api/status')).json();streamSupported=!!status.streaming;if(!status.ready)el('error').textContent='サーバーに取得設定がありません';}
  const params=new URLSearchParams(location.search);if(streamSupported&&params.has('lat')&&params.has('lon')){const lat=Number(params.get('lat')),lon=Number(params.get('lon'));if(!validCoordinate(lat,lon))throw Error('URLの緯度・経度が範囲外です');metadata.origin=[lat,lon,0];}
  document.title=metadata.title;el('title').textContent=metadata.title;el('location').textContent=`${metadata.origin[0].toFixed(6)}, ${metadata.origin[1].toFixed(6)}`;
  const total=metadata.totals;el('counts').textContent=`${total.tiles} タイル · ポリゴン ${total.meshTriangles.toLocaleString()} 面 · Splat ${total.splatRecords.toLocaleString()}`;
  if(streamSupported){startStreaming();el('pick-location').disabled=false;}
  else{
  reset();const queue=metadata.tiles.slice();await Promise.all(Array.from({length:4},async()=>{while(queue.length)await loadTile(queue.shift());}));
  renderer.compile(scene,camera);ready=true;el('pick-location').disabled=false;el('status').textContent='元のテクスチャ付きポリゴン + Splat · 読み込み完了';
  }
}catch(error){el('error').textContent=String(error.message||error);el('status').textContent='読み込みに失敗しました';console.error(error);}
