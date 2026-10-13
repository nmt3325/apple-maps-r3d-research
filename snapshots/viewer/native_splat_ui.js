
// VERIFIED native Apple R3D XYZ from iOS27 VectorKit (no invented geometry).
// Cyan shading and sprite size are diagnostic, not decoded PBR or SH attributes.
const nativeMeta=await (await loader('./data/native-r3d.json')).json();
const nativeRaw=await (await loader('./data/'+nativeMeta.filename)).arrayBuffer();
const nativeXYZ=new Float32Array(nativeRaw);
if(nativeXYZ.length!==nativeMeta.count*3)throw new Error('Native XYZ length mismatch');
const nativeGeom=new THREE.BufferGeometry();
nativeGeom.setAttribute('position',new THREE.BufferAttribute(nativeXYZ,3));
nativeGeom.computeBoundingSphere();
const nativeMaterial=new THREE.ShaderMaterial({
 vertexShader:'void main(){vec4 eye=modelViewMatrix*vec4(position,1.0);gl_Position=projectionMatrix*eye;gl_PointSize=clamp(1400.0/max(12.0,-eye.z),2.2,25.0);}',
 fragmentShader:'precision mediump float;void main(){vec2 q=2.0*gl_PointCoord-1.0;float r=dot(q,q);if(r>1.0)discard;gl_FragColor=vec4(0.20,0.87,1.00,0.78*exp(-3.5*r));}',
 transparent:true,depthTest:false,depthWrite:false,blending:THREE.NormalBlending
});
const nativePoints=new THREE.Points(nativeGeom,nativeMaterial);
nativePoints.frustumCulled=false;nativePoints.renderOrder=999;
nativePoints.userData={type:'native-R3D',count:nativeMeta.count,z:nativeMeta.z,x:nativeMeta.x,y:nativeMeta.y,h:nativeMeta.h};
scene.add(nativePoints);
document.getElementById('nativePoints').addEventListener('change',e=>{nativePoints.visible=e.target.checked});
document.getElementById('focusNative').onclick=()=>{
 const c=nativeMeta.center;
 ctrl.target.set(c[0],c[1],c[2]);
 camera.position.set(c[0]+100,c[1]+75,c[2]+100);ctrl.update();
 document.getElementById('nativePoints').checked=true;nativePoints.visible=true;
 info.textContent='Apple純正 R3D から展開した '+nativeMeta.count.toLocaleString()+' 点の位置。色と粒径は仮設定。';
};
