import * as THREE from 'three';
import {tileMatrix,tileBounds} from './stream-planner.mjs';

const maskDeclarations='uniform int lodMaskCount;uniform vec4 lodMasks[16];varying vec2 vWorldXZ;';
const maskBody='for(int i=0;i<16;i++){if(i>=lodMaskCount)break;vec4 r=lodMasks[i];if(vWorldXZ.x>=r.x&&vWorldXZ.x<r.y&&vWorldXZ.y>=r.z&&vWorldXZ.y<r.w)discard;}';

function polygonMaterial(texture,mask){
  const material=new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide});
  material.onBeforeCompile=shader=>{
    shader.uniforms.lodMaskCount=mask.count;shader.uniforms.lodMasks=mask.rectangles;
    shader.vertexShader='varying vec2 vWorldXZ;\n'+shader.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\nvWorldXZ=(modelMatrix*vec4(transformed,1.0)).xz;');
    shader.fragmentShader=maskDeclarations+'\n'+shader.fragmentShader.replace('#include <clipping_planes_fragment>','#include <clipping_planes_fragment>\n'+maskBody);
  };
  material.customProgramCacheKey=()=> 'r3d-stream-lod-v1';
  return material;
}
async function binary(path,signal){const r=await fetch(path,{signal});if(!r.ok)throw Error('タイルのキャッシュを読み込めません。再試行してください。');return r.arrayBuffer();}
async function textureFrom(path,signal){
  const response=await fetch(path,{signal});if(!response.ok)throw Error('元テクスチャを読み込めません');
  const url=URL.createObjectURL(await response.blob());
  try{const image=new Image();image.src=url;await image.decode();if(signal.aborted)throw new DOMException('Aborted','AbortError');return new THREE.Texture(image);}
  finally{URL.revokeObjectURL(url);}
}
export async function loadStreamModel(tile,signal,options){
  let texture=null,polygon=null,splat=null;
  try{
    // Finish texture creation before Promise rejection cleanup, including aborts.
    const results=await Promise.allSettled([binary(tile.mesh,signal),binary(tile.splats,signal),tile.texture?textureFrom(tile.texture,signal):Promise.resolve(null)]);
    texture=results[2].status==='fulfilled'?results[2].value:null;
    const failure=results.find(r=>r.status==='rejected');if(failure)throw failure.reason;
    if(signal.aborted)throw new DOMException('Aborted','AbortError');
    const matrix=new THREE.Matrix4().fromArray(tileMatrix(options.frame(),tile.transform));
    const mask={count:{value:0},rectangles:{value:Array.from({length:16},()=>new THREE.Vector4())}};
    let cost=0;
    const account=geometry=>{for(const attribute of Object.values(geometry.attributes))cost+=attribute.array.byteLength;if(geometry.index)cost+=geometry.index.array.byteLength;};
    if(tile.triangles){
      if(!texture)throw Error('ポリゴンの元テクスチャがありません');
      texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=true;texture.needsUpdate=true;
      texture.anisotropy=Math.min(4,options.renderer.capabilities.getMaxAnisotropy());
      polygon=new THREE.Mesh(options.meshGeometry(results[0].value),polygonMaterial(texture,mask));account(polygon.geometry);
      cost+=Math.ceil(texture.image.width*texture.image.height*4*4/3);
    }
    const material=options.splatMaterial.clone();
    material.uniforms.lodMaskCount=mask.count;material.uniforms.lodMasks=mask.rectangles;
    material.vertexShader='varying vec2 vWorldXZ;\n'+material.vertexShader.replace('void main(){','void main(){vWorldXZ=(modelMatrix*vec4(position,1.0)).xz;');
    material.fragmentShader=maskDeclarations+'\n'+material.fragmentShader.replace('void main(){','void main(){'+maskBody);
    splat=new THREE.Mesh(options.splatGeometry(results[1].value),material);account(splat.geometry);splat.renderOrder=1;
    for(const mesh of [polygon,splat].filter(Boolean)){mesh.name=tile.source;mesh.matrixAutoUpdate=false;mesh.matrix.copy(matrix);mesh.visible=false;}
    if(polygon)options.polygons.add(polygon);options.splats.add(splat);
    return {polygon,splat,texture,mask,cost,tile};
  }catch(error){for(const mesh of [polygon,splat].filter(Boolean)){mesh.geometry.dispose();mesh.material.dispose();}texture?.dispose();throw error;}
}
export function renderStreamModel(model,visible,fine,frame,opacity){
  if(model.polygon)model.polygon.visible=visible;model.splat.visible=visible;
  model.splat.material.uniforms.alphaFactor.value=opacity;
  model.mask.count.value=Math.min(16,fine.length);
  for(let i=0;i<model.mask.count.value;i++)model.mask.rectangles.value[i].fromArray(tileBounds(frame,fine[i]));
}
export function disposeStreamModel(model){
  for(const mesh of [model.polygon,model.splat].filter(Boolean)){mesh.removeFromParent();mesh.geometry.dispose();mesh.material.dispose();}
  model.texture?.dispose();
}
