// Optional first-person Flyover navigation. This mode never mutates native C3M or R3D geometry.
// WASD horizontal travel relative to camera heading; E/Space up; Q/Ctrl down; Shift sprint.
// Click viewport to lock mouse, Escape unlocks, F toggles mode. Mobile touch controls supported.
const flyButton=document.getElementById('flyMode');
const flyHud=document.getElementById('flyHud');
const flyHint=document.getElementById('flyHint');
const flySpeed=document.getElementById('flySpeed');
const flySpeedValue=document.getElementById('flySpeedValue');
const flyTouchControls=document.getElementById('flyTouchControls');
const flyKeys=new Set(),flyTouchKeys=new Set();
let flyMode=false,flyYaw=0,flyPitch=0,flyLastTime=0,flyLastSort=0,flyWasMoving=false,flyTouchLooking=false,flyLastPointerX=0,flyLastPointerY=0;
const flyDirection=new THREE.Vector3(),flyMove=new THREE.Vector3();
const flyRight=new THREE.Vector3(),flyForward=new THREE.Vector3();
const flyHandled=new Set(['KeyW','KeyA','KeyS','KeyD','KeyE','KeyQ','Space','ShiftLeft','ShiftRight','ControlLeft','ControlRight','KeyF']);
const isEditing=(target)=>!!target?.closest?.('input,select,textarea,[contenteditable="true"]');
flySpeed.addEventListener('input',()=>{flySpeedValue.textContent=flySpeed.value+' m/s'});
function applyFlyOrientation(){
 flyPitch=THREE.MathUtils.clamp(flyPitch,-Math.PI/2+0.012,Math.PI/2-0.012);
 camera.rotation.order='YXZ';
 camera.rotation.set(flyPitch,flyYaw,0,'YXZ');
}
function lookFly(dx,dy){
 if(!flyMode)return;
 flyYaw-=dx*0.0024;
 flyPitch-=dy*0.0024;
 applyFlyOrientation();
 requestNativeSort();
}
function updateFlyHud(){
 flyHud.hidden=!flyMode;
 flyTouchControls.hidden=!flyMode || !window.matchMedia('(pointer:coarse)').matches;
 flyButton.setAttribute('aria-pressed',String(flyMode));
 flyButton.textContent=flyMode?'自由移動 ON':'自由移動 OFF';
 flyHint.textContent=flyMode ?
  (document.pointerLockElement===renderer.domElement ? 'マウス操作中（Escで解除）' : '画面をクリックしてマウス視点操作') : '';
}
function setFlyMode(on){
 if(flyMode===!!on)return;
 flyMode=!!on;
 flyKeys.clear();flyTouchKeys.clear();
 flyLastTime=0;flyWasMoving=false;
 if(flyMode){
  camera.getWorldDirection(flyDirection);
  flyYaw=Math.atan2(-flyDirection.x,-flyDirection.z);
  flyPitch=Math.asin(THREE.MathUtils.clamp(flyDirection.y,-1,1));
  ctrl.enabled=false;
  applyFlyOrientation();
 }else{
  if(document.pointerLockElement===renderer.domElement)document.exitPointerLock();
  camera.getWorldDirection(flyDirection);
  ctrl.target.copy(camera.position).addScaledVector(flyDirection,Math.max(45,Math.min(125,90)));
  ctrl.enabled=true;
  ctrl.update();
  requestNativeSort();
 }
 updateFlyHud();
}
flyButton.addEventListener('click',()=>setFlyMode(!flyMode));
window.addEventListener('keydown',event=>{
 if(event.code==='KeyF' && !isEditing(event.target) && !event.repeat){
  event.preventDefault();setFlyMode(!flyMode);return;
 }
 if(!flyMode || isEditing(event.target))return;
 if(flyHandled.has(event.code)){
  event.preventDefault();
  // R3D scene renders can be slow on software GPUs; track real key hold duration,
  // rather than relying only on requestAnimationFrame frequency.
  if(!flyKeys.has(event.code)){
   if(flyKeys.size>0)updateFlyFrame(performance.now());
   else flyLastTime=performance.now();
   flyKeys.add(event.code);
  }
 }
},{passive:false});
window.addEventListener('keyup',event=>{
 if(!flyMode)return;
 if(flyHandled.has(event.code)){
  event.preventDefault();
  if(flyKeys.has(event.code))updateFlyFrame(performance.now());
  flyKeys.delete(event.code);
  requestNativeSort();
 }
},{passive:false});
window.addEventListener('blur',()=>{
 flyKeys.clear();flyTouchKeys.clear();
 if(flyMode)requestNativeSort();
});
renderer.domElement.addEventListener('click',()=>{
 if(!flyMode || window.matchMedia('(pointer:coarse)').matches)return;
 if(document.pointerLockElement!==renderer.domElement){
  const request=renderer.domElement.requestPointerLock?.();
  if(request?.catch)request.catch(()=>{flyHint.textContent='マウスロックが使えません。WASDは利用可能です。'});
 }
});
document.addEventListener('pointerlockchange',updateFlyHud);
document.addEventListener('mousemove',event=>{
 if(!flyMode || document.pointerLockElement!==renderer.domElement)return;
 lookFly(event.movementX,event.movementY);
});
renderer.domElement.addEventListener('pointerdown',event=>{
 if(!flyMode || event.pointerType!=='touch')return;
 flyTouchLooking=true;flyLastPointerX=event.clientX;flyLastPointerY=event.clientY;
 try{renderer.domElement.setPointerCapture(event.pointerId)}catch{}
});
renderer.domElement.addEventListener('pointermove',event=>{
 if(!flyMode || !flyTouchLooking || event.pointerType!=='touch')return;
 lookFly(event.clientX-flyLastPointerX,event.clientY-flyLastPointerY);
 flyLastPointerX=event.clientX;flyLastPointerY=event.clientY;
});
for(const name of ['pointerup','pointercancel','lostpointercapture']){
 renderer.domElement.addEventListener(name,()=>{flyTouchLooking=false;if(flyMode)requestNativeSort()});
}
for(const btn of flyTouchControls.querySelectorAll('[data-fly-key]')){
 const code=btn.dataset.flyKey;
 btn.addEventListener('pointerdown',e=>{
  if(!flyMode)return;
  e.preventDefault();btn.setPointerCapture(e.pointerId);
  if(flyTouchKeys.size===0 && flyKeys.size===0)flyLastTime=performance.now();
  flyTouchKeys.add(code);btn.classList.add('pressed');
 });
 const stop=e=>{if(flyMode && flyTouchKeys.has(code))updateFlyFrame(performance.now());flyTouchKeys.delete(code);btn.classList.remove('pressed');if(flyMode)requestNativeSort()};
 btn.addEventListener('pointerup',stop);
 btn.addEventListener('pointercancel',stop);
 btn.addEventListener('lostpointercapture',stop);
}
function updateFlyFrame(time){
 if(!flyMode)return;
 if(!flyLastTime){flyLastTime=time;return}
 // Integrate elapsed movement even when a high-cost 3D frame takes hundreds of ms.
 // Cap to avoid big unintended jumps when a background tab resumes.
 const dt=Math.max(0,Math.min((time-flyLastTime)/1000,0.70));
 flyLastTime=time;
 const pressed=(key)=>flyKeys.has(key)||flyTouchKeys.has(key);
 const f=(pressed('KeyW')?1:0)-(pressed('KeyS')?1:0);
 const side=(pressed('KeyD')?1:0)-(pressed('KeyA')?1:0);
 const up=(pressed('KeyE')||pressed('Space')?1:0)-(pressed('KeyQ')||pressed('ControlLeft')||pressed('ControlRight')?1:0);
 flyForward.set(-Math.sin(flyYaw),0,-Math.cos(flyYaw));
 flyRight.set(-flyForward.z,0,flyForward.x);
 flyMove.set(0,up,0);
 flyMove.addScaledVector(flyForward,f);
 flyMove.addScaledVector(flyRight,side);
 if(flyMove.lengthSq()===0){
  if(flyWasMoving){flyWasMoving=false;requestNativeSort()}
  return;
 }
 flyMove.normalize();
 const sprint=pressed('ShiftLeft')||pressed('ShiftRight')?3.5:1;
 camera.position.addScaledVector(flyMove,Number(flySpeed.value)*dt*sprint);
 flyWasMoving=true;
 // Moving the camera changes transparent blend depth order. Avoid expensive per-frame sorts:
 // refresh every ~1.2s, and once more after the final key release.
 if(time-flyLastSort>1200){requestNativeSort();flyLastSort=time}
}
updateFlyHud();
