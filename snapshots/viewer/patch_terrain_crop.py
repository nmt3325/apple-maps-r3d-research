from pathlib import Path
p=Path('/opt/flyover-viewer/www/index.html')
s=p.read_text()
a='<input id="scale" type="range" min="0" max="8" step=".25" value="2">'
b='<input id="scale" type="range" min="0" max="3" step=".05" value="1">'
assert s.count(a)==1
s=s.replace(a,b)
s=s.replace('標高サンプルの単位・オフセットは未校正。倍率は可視化用です。','保存されたR3D座標の標高とPNG値を照合し、h ≈ 51.68 + 0.788 × PNG値に校正しました（推定値）。')
a='  <div class="row"><label for="terrain">保存PNGを高さサーフェス表示</label><input checked type="checkbox" id="terrain"></div>'
assert s.count(a)==1
s=s.replace(a,a+'\n  <div class="row"><label for="clipTerrain">補助メッシュをR3D取得範囲に限定</label><input checked type="checkbox" id="clipTerrain"></div>')
a="renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});"
assert s.count(a)==1
s=s.replace(a,a+"renderer.localClippingEnabled=true;",1)
anchor="const nativeTrianglesMeta=await (await loader('./data/native-triangle-splats.json')).json();"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"""
// Clip the calibrated but NON-original PNG heightfield to the region actually captured
// and decoded as native R3D splats. Avoid showing unsupported giant polygon spikes elsewhere.
const bbox=nativeTrianglesMeta;
const terrainMargin=55;
const xmin=bbox.min[0]-terrainMargin,xmax=bbox.max[0]+terrainMargin;
const zmin=bbox.min[2]-terrainMargin,zmax=bbox.max[2]+terrainMargin;
const pngCropPlanes=[
 new THREE.Plane(new THREE.Vector3(1,0,0),-xmin),
 new THREE.Plane(new THREE.Vector3(-1,0,0),xmax),
 new THREE.Plane(new THREE.Vector3(0,0,1),-zmin),
 new THREE.Plane(new THREE.Vector3(0,0,-1),zmax)
];
terrainMaterials.forEach(m=>{m.clippingPlanes=pngCropPlanes;m.needsUpdate=true});
document.getElementById('clipTerrain').addEventListener('change',e=>{
 terrainMaterials.forEach(m=>{m.clippingPlanes=e.target.checked?pngCropPlanes:null;m.needsUpdate=true});
});
""")
p.write_text(s)
print('Created R3D-aligned calibrated polygon height proxy with opt-out cropping.')
