// Gaussian-style point splats synthesized ONLY from observed 16-bit elevation rasters.
// This is an interactive rendering approximation, not decoded native Apple Gaussian data.
const gaussVertex=`
  attribute vec3 tint; varying vec3 vTint;
  uniform float uRadius;
  void main(){
    vTint=tint;
    vec4 p=modelViewMatrix*vec4(position,1.0);
    gl_Position=projectionMatrix*p;
    gl_PointSize=clamp(uRadius*1750.0/max(15.0,-p.z),1.5,48.0);
  }`;
const gaussFragment=`
  precision highp float;
  varying vec3 vTint;
  void main(){
    vec2 uv=(gl_PointCoord*2.0-1.0);
    float d=dot(uv,uv);
    if(d>1.0)discard;
    float alpha=exp(-5.0*d)*0.70;
    gl_FragColor=vec4(vTint,alpha);
  }`;
for(let index=0;index<objects.length;index++){
 const base=objects[index].geometry;
 const vertices=new Float32Array(base.getAttribute('position').array);
 const tints=new Float32Array(base.getAttribute('color').array);
 const geom=new THREE.BufferGeometry();
 geom.setAttribute('position',new THREE.BufferAttribute(vertices,3));
 geom.setAttribute('tint',new THREE.BufferAttribute(tints,3));
 const shader=new THREE.ShaderMaterial({
  uniforms:{uRadius:{value:5.0}},
  vertexShader:gaussVertex,fragmentShader:gaussFragment,
  transparent:true,depthTest:true,depthWrite:false,
  blending:THREE.NormalBlending
 });
 const g=new THREE.Points(geom,shader);
 g.frustumCulled=false;g.visible=false;
 g.userData={heights:base.userData.original};
 splatClouds.push(g);scene.add(g);
}
document.getElementById('splats').addEventListener('change',e=>{
 const show=e.target.checked;
 splatClouds.forEach(c=>c.visible=show);
 // Use cloud-only mode by default when splats are enabled, to avoid occlusion by the original meshes.
 objects.forEach(m=>m.visible=!show);
 document.getElementById('terrain').checked=!show;
 document.getElementById('error').textContent=show?'Gaussian描画: 実キャプチャの高さ値から再サンプリングした近似スプラット。style=98の3DGSの復号ではありません。':'※未解析の3DGSではなく、復号済みの高さラスタを表示中';
});
