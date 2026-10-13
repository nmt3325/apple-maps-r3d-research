// ORIGINAL APPLE R3D C3M textured polygon layer.
// XYZ, UV, normals and 3 independent triangle-corner indices from iOS27 native decoder.
// Each tile's JPEG is a browser conversion of its one-to-one Apple HEIC texture atlas.
const c3mManifest=await (await loader('./data/native-c3m.json')).json();
const c3mGroup=new THREE.Group();
c3mGroup.name='Apple-original-C3M-UV-textured-polygon-meshes';
scene.add(c3mGroup);
const c3mTextureLoader=new THREE.TextureLoader();
const c3mCache=new Map();
let c3mLoadGeneration=0;
let c3mModeIsHybrid=false;
const c3mStatus=document.getElementById('c3mStatus');
function selectC3mTiles(){
 const selected=document.getElementById('c3mLOD').value;
 if(selected==='19')return c3mManifest.tiles.filter(t=>t.z===19);
 if(selected==='18')return c3mManifest.tiles.filter(t=>t.z===18);
 if(selected==='20-all')return c3mManifest.tiles.filter(t=>t.z===20);
 const center=ctrl.target;
 return c3mManifest.tiles.filter(t=>t.z===20).sort((a,b)=>{
  const da=(a.center[0]-center.x)**2+(a.center[2]-center.z)**2;
  const db=(b.center[0]-center.x)**2+(b.center[2]-center.z)**2;
  return da-db;
 }).slice(0,50);
}
async function loadOneNativeC3m(tile){
 if(c3mCache.has(tile.id))return c3mCache.get(tile.id);
 const raw=await(await loader('./c3m-geometry/'+tile.geometry)).arrayBuffer();
 const header=new DataView(raw);
 const magic=header.getUint32(0,true),n=header.getUint32(4,true),faces=header.getUint32(8,true);
 if(magic!==0x4d33434d || n!==tile.vertices || faces!==tile.triangles || raw.byteLength!==16+n*32+faces*12)
  throw new Error('C3M geometry bytes mismatch: '+tile.id);
 let off=16;
 const pos=new Float32Array(raw,off,n*3);off+=n*12;
 const uv=new Float32Array(raw,off,n*2);off+=n*8;
 const normals=new Float32Array(raw,off,n*3);off+=n*12;
 const indices=new Uint32Array(raw,off,faces*3);
 const geo=new THREE.BufferGeometry();
 geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
 geo.setAttribute('uv',new THREE.BufferAttribute(uv,2));
 geo.setAttribute('normal',new THREE.BufferAttribute(normals,3));
 geo.setIndex(new THREE.BufferAttribute(indices,1));
 geo.computeBoundingSphere();
 const texture=await c3mTextureLoader.loadAsync('./'+tile.texture);
 // The original C3M UVs use the same bottom-left V convention as the legacy
 // Flyover OBJ exporter. Three.js TextureLoader must flip decoded HEIC JPEGs.
 // flipY=false incorrectly mapped roofs and windows onto unrelated faces.
 texture.flipY=true;
 texture.colorSpace=THREE.SRGBColorSpace;
 texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
 const mat=new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide,depthWrite:true});
 const mesh=new THREE.Mesh(geo,mat);
 mesh.name='ORIGINAL_C3M_'+tile.id;
 mesh.userData={source:'iOS27 VectorKit R3D C3M',tile};
 mesh.visible=false;
 c3mGroup.add(mesh);
 c3mCache.set(tile.id,mesh);
 return mesh;
}
function updateC3mLayerVisibility(){
 const requested=document.getElementById('originalC3M').checked;
 const active=c3mModeIsHybrid && requested;
 c3mGroup.visible=active;
 for(const m of c3mCache.values())m.visible=active && m.userData.selected===true;
 // Once true textured C3M is enabled, suppress the artificial PNG height mesh;
 // it remains available through the independent toggle when C3M is unchecked.
 objects.forEach(m=>m.visible=c3mModeIsHybrid && !requested && document.getElementById('terrain').checked);
}
async function reloadNativeC3m(){
 const seq=++c3mLoadGeneration;
 const selected=selectC3mTiles();
 const wanted=new Set(selected.map(t=>t.id));
 for(const [id,mesh] of c3mCache)mesh.userData.selected=wanted.has(id);
 let loaded=0,faces=0,errors=[];
 c3mStatus.textContent='純正C3M '+selected.length+'タイル読み込み中…';
 const queue=selected.slice();
 async function worker(){
  while(queue.length){
   if(seq!==c3mLoadGeneration)return;
   const t=queue.shift();
   try{
    const mesh=await loadOneNativeC3m(t);
    if(seq!==c3mLoadGeneration)return;
    mesh.userData.selected=true;loaded++;faces+=t.triangles;
    if(loaded%4===0||loaded===selected.length)c3mStatus.textContent=
      'C3M '+loaded+'/'+selected.length+'タイル · '+faces.toLocaleString()+'面';
   }catch(e){errors.push(t.id+' '+e.message)}
  }
 }
 await Promise.all(Array.from({length:Math.min(4,selected.length)},worker));
 if(seq!==c3mLoadGeneration)return;
 updateC3mLayerVisibility();
 c3mStatus.textContent=errors.length? 'C3M '+loaded+'/'+selected.length+'タイル、失敗'+errors.length+
  '（'+errors[0]+'）':'純正テクスチャ付きC3M '+loaded+'タイル / '+faces.toLocaleString()+'三角形を表示';
 if(loaded>0)setStatus('✓ 純正C3M＋純正R3D Splat：'+faces.toLocaleString()+'ポリゴン / 417,650 Splat');
}
document.getElementById('originalC3M').addEventListener('change',updateC3mLayerVisibility);
document.getElementById('c3mLOD').addEventListener('change',reloadNativeC3m);
document.getElementById('refreshC3m').onclick=reloadNativeC3m;
