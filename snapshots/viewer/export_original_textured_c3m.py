#!/usr/bin/env python3
"""Export real iOS 27 Apple R3D C3M textured polygon meshes as glTF GLB.
Face topology, normals, UVs and original HEIC texture atlas originate in captured R3D.
HEIC atlases were decoded to JPEG for browser interoperability (no color invented).
"""
from pathlib import Path
import numpy as np
from PIL import Image
import trimesh
import json,sys,struct,time
root=Path('/opt/flyover-viewer/www')
meta=json.loads((root/'data/native-c3m.json').read_text())
selection=sys.argv[1] if len(sys.argv)>1 else '19'
tiles=[t for t in meta['tiles'] if str(t['z'])==selection] if selection in ('18','19','20') else meta['tiles']
if selection=='sample':tiles=[next(t for t in meta['tiles'] if t['z']==20 and t['x']==931324 and t['y']==412804 and t['h']==0)]
outpath=root/('Apple-Flyover-iOS27-original-HEIC-textured-C3M-'+selection+'.glb')
start=time.time()
scene=trimesh.Scene()
for i,t in enumerate(tiles):
 raw=(root/'c3m-geometry'/t['geometry']).read_bytes()
 magic,n,f,_=struct.unpack_from('<IIII',raw,0)
 assert magic==0x4d33434d and n==t['vertices'] and f==t['triangles']
 off=16
 v=np.frombuffer(raw,dtype='<f4',count=n*3,offset=off).reshape(-1,3).copy();off+=12*n
 uv=np.frombuffer(raw,dtype='<f4',count=n*2,offset=off).reshape(-1,2).copy();off+=8*n
 norm=np.frombuffer(raw,dtype='<f4',count=n*3,offset=off).reshape(-1,3).copy();off+=12*n
 faces=np.frombuffer(raw,dtype='<u4',count=f*3,offset=off).reshape(-1,3).copy()
 atlas=Image.open(root/t['texture']).convert('RGB')
 visual=trimesh.visual.TextureVisuals(uv=uv,material=trimesh.visual.material.PBRMaterial(
  baseColorTexture=atlas, metallicFactor=0.0, roughnessFactor=1.0,
  doubleSided=True, name='Apple-HEIC-'+t['id']))
 mesh=trimesh.Trimesh(vertices=v,faces=faces,vertex_normals=norm,visual=visual,process=False,validate=False)
 scene.add_geometry(mesh,node_name='C3M_'+t['id'],geom_name='HEIC_C3M_'+t['id'])
 if i%25==24:print('processed',i+1,'/',len(tiles),flush=True)
print('exporting',len(tiles),'original native textured tiles',sum(t['triangles'] for t in tiles),'triangles',flush=True)
scene.export(outpath)
out=trimesh.load(outpath,force='scene')
loaded=list(out.geometry.values())
print('wrote',outpath.name,'bytes',outpath.stat().st_size,'readback meshes',len(loaded),
 'faces',sum(len(g.faces) for g in loaded),'vertices',sum(len(g.vertices) for g in loaded),
 'textureMaterials',sum(bool(getattr(g.visual.material,'baseColorTexture',None)) for g in loaded if g.visual.kind=='texture'),
 'time',round(time.time()-start,1))
