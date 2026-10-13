// FULL Apple native R3D point cloud: 223 captured style98 tiles.
// Position / RGB / opacity come exclusively from iOS27 VectorKit.
// The billboard Gaussian radius is a diagnostic display approximation; native covariance not decoded.
const nativeAllMeta=await (await loader('./data/native-all.json')).json();
const [allPositionRaw,allColorRaw,allShapeRaw]=await Promise.all([
 loader('./data/'+nativeAllMeta.renderFiles.positions).then(r=>r.arrayBuffer()),
 loader('./data/'+nativeAllMeta.renderFiles.rgba).then(r=>r.arrayBuffer()),
 loader('./data/'+nativeAllMeta.renderFiles.shape).then(r=>r.arrayBuffer())
]);
const allPositions=new Float32Array(allPositionRaw);
const allColors=new Uint8Array(allColorRaw);
const allShapes=new Float32Array(allShapeRaw);
if(allPositions.length/3!==nativeAllMeta.visibleAlphaNonzero ||
 allColors.length/4!==nativeAllMeta.visibleAlphaNonzero ||
 allShapes.length/4!==nativeAllMeta.visibleAlphaNonzero)
 throw new Error('223 R3D tiles attribute counts differ');
const allGeo=new THREE.BufferGeometry();
allGeo.setAttribute('position',new THREE.BufferAttribute(allPositions,3));
allGeo.setAttribute('nativeRGBA',new THREE.BufferAttribute(allColors,4,true));
allGeo.setAttribute('rawShape',new THREE.BufferAttribute(allShapes,4));
allGeo.computeBoundingSphere();
const allMaterial=new THREE.ShaderMaterial({
 uniforms:{pixelSize:{value:1400.0}},
 vertexShader:'attribute vec4 nativeRGBA;attribute vec4 rawShape;uniform float pixelSize;varying vec4 vRGBA;void main(){vRGBA=nativeRGBA;vec4 eye=modelViewMatrix*vec4(position,1.0);gl_Position=projectionMatrix*eye;gl_PointSize=clamp(pixelSize/max(12.0,-eye.z),1.5,26.0);}',
 fragmentShader:'precision mediump float;varying vec4 vRGBA;void main(){vec2 q=gl_PointCoord*2.0-1.0;float t=dot(q,q);if(t>1.0||vRGBA.a<=0.0)discard;gl_FragColor=vec4(vRGBA.rgb,vRGBA.a*exp(-4.0*t));}',
 transparent:true,depthTest:false,depthWrite:false,blending:THREE.NormalBlending
});
const nativeAll=new THREE.Points(allGeo,allMaterial);
nativeAll.frustumCulled=false;
nativeAll.renderOrder=1000;
nativeAll.userData={type:'native-R3D-all',count:nativeAllMeta.visibleAlphaNonzero};
scene.add(nativeAll);
nativePoints.visible=false;
points.forEach(p=>p.visible=false);
document.getElementById('points').checked=false;
document.getElementById('allNative').addEventListener('change',e=>nativeAll.visible=e.target.checked);
document.getElementById('focusAllNative').onclick=()=>{
 const lo=nativeAllMeta.boundsMin,hi=nativeAllMeta.boundsMax;
 const mx=(lo[0]+hi[0])/2,my=(lo[1]+hi[1])/2,mz=(lo[2]+hi[2])/2;
 ctrl.target.set(mx,my,mz);
 camera.position.set(mx+560,my+480,mz+560);ctrl.update();
 nativeAll.visible=true;document.getElementById('allNative').checked=true;
 info.textContent='Apple純正R3D 223タイル／全736,915点、透明度0を除く417,650点を表示中。RGB/Alphaは実際のデータ、Gaussian半径は仮設定。';
};
