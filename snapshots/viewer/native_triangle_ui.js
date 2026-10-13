// Actual iOS27 VectorKit createSplats output: 3 real XYZ vertices and one packed RGBA per triangle.
// Only smooth edge transparency is approximated (barycentric-product exponent + normalized factor).
const nativeTrianglesMeta=await (await loader('./data/native-triangle-splats.json')).json();
const [nativeTriPositionsRaw,nativeTriColorsRaw]=await Promise.all([
 loader('./data/'+nativeTrianglesMeta.sourceFiles.triangles).then(r=>r.arrayBuffer()),
 loader('./data/'+nativeTrianglesMeta.sourceFiles.color).then(r=>r.arrayBuffer())
]);
const triPositions=new Float32Array(nativeTriPositionsRaw);
const triColors=new Uint8Array(nativeTriColorsRaw);
const triCount=nativeTrianglesMeta.splatTrianglesVisible;
if(triCount!==417650 || triPositions.length!==triCount*9 || triColors.length!==triCount*4)
 throw new Error('Native createSplats buffer sizes invalid');
const triColorVerts=new Uint8Array(triCount*12);
const triBary=new Uint8Array(triCount*9);
const triNormalVerts=new Float32Array(triCount*9);
for(let i=0;i<triCount;i++){
 const k=i*12,s=i*4,base=i*9,nn=i*3;
 for(let v=0;v<3;v++){
  triColorVerts.set(triColors.subarray(s,s+4),k+4*v);
  triNormalVerts.set(allNormals.subarray(nn,nn+3),base+3*v);
 }
 triBary[base]=255;triBary[base+4]=255;triBary[base+8]=255;
}
const nativeTriangleGeo=new THREE.BufferGeometry();
nativeTriangleGeo.setAttribute('position',new THREE.BufferAttribute(triPositions,3));
nativeTriangleGeo.setAttribute('nativeRGBA',new THREE.BufferAttribute(triColorVerts,4,true));
nativeTriangleGeo.setAttribute('bary',new THREE.BufferAttribute(triBary,3,true));
nativeTriangleGeo.setAttribute('nativeNormal',new THREE.BufferAttribute(triNormalVerts,3));
nativeTriangleGeo.computeBoundingSphere();
const nativeTriangleMat=new THREE.ShaderMaterial({
 uniforms:{splatExponent:{value:1.0},useNormalLight:{value:0.0}},
 vertexShader:'attribute vec4 nativeRGBA;attribute vec3 bary;attribute vec3 nativeNormal;varying vec4 vRGBA;varying vec3 vBary;uniform float useNormalLight;void main(){float ndotl=max(0.0,dot(normalize(nativeNormal),normalize(vec3(-0.2,0.9,0.4))));float light=mix(1.0,0.35+0.65*ndotl,useNormalLight);vRGBA=vec4(nativeRGBA.rgb*light,nativeRGBA.a);vBary=bary;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
 fragmentShader:'precision highp float;varying vec4 vRGBA;varying vec3 vBary;uniform float splatExponent;void main(){float prod=vBary.x*vBary.y*vBary.z;if(prod<=0.0||vRGBA.a<=0.0)discard;float smooth=pow(clamp(27.0*prod,0.0,1.0),splatExponent);gl_FragColor=vec4(vRGBA.rgb,vRGBA.a*smooth);}',
 transparent:true,depthTest:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.NormalBlending
});
const nativeTriangleMesh=new THREE.Mesh(nativeTriangleGeo,nativeTriangleMat);
nativeTriangleMesh.frustumCulled=false;
nativeTriangleMesh.renderOrder=999;
nativeTriangleMesh.userData={type:'Apple-Native-Triangular-Splats',triangleCount:triCount};
scene.add(nativeTriangleMesh);
document.getElementById('realNativeTriangles').addEventListener('change',e=>nativeTriangleMesh.visible=e.target.checked);
document.getElementById('splatExponent').addEventListener('input',e=>{
 nativeTriangleMat.uniforms.splatExponent.value=+e.target.value;
 document.getElementById('splatExponentVal').textContent=(+e.target.value).toFixed(2);
});
document.getElementById('shadeNormals').addEventListener('change',e=>{
 nativeTriangleMat.uniforms.useNormalLight.value=e.target.checked?1.0:0.0;
});
