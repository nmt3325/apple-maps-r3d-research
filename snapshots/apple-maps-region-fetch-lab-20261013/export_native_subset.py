#!/usr/bin/env python3
"""Build a color-triangle GLB from read-only native VectorKit decoder outputs."""
import sys,re,json
from pathlib import Path
import numpy as np,trimesh
from geo_ops import project
dest=Path(sys.argv[1]).resolve()
source=Path('/opt/flyover-viewer/decoded-native/all-223')
png=list(dest.glob('s99_z14_*.png'))
if not png:raise SystemExit('Need a style99 raster for coordinate origin')
origin=[tuple(map(int,re.search(r'_x(\d+)_y(\d+)_',p.name).groups())) for p in png]
x0=min(i[0] for i in origin);y0=min(i[1] for i in origin)
scene=trimesh.Scene();done=[];miss=[]
for raw in sorted(dest.glob('s98_*.r3d')):
 m=re.match(r's98_z(\d+)_x(\d+)_y(\d+)_h(\d+).r3d',raw.name)
 if not m:continue
 z,x,y,h=map(int,m.groups())
 base=f'r3d_z{z}_x{x}_y{y}_h{h}.r3d'
 geom=source/(base+'.native-triangle-f32')
 props=source/(base+'.native-material20')
 if not geom.exists() or not props.exists():miss.append(raw.name);continue
 local=np.fromfile(geom,dtype='<f4').reshape(-1,3,3)
 rgba=np.fromfile(props,dtype='u1').reshape(-1,20)[:,:4]
 if len(local)!=len(rgba):miss.append(raw.name);continue
 visible=rgba[:,3]>0
 if not visible.any():continue
 xyz=project(local[visible],raw.read_bytes(),x0,y0).reshape(-1,3)
 faces=np.arange(len(xyz)).reshape(-1,3)
 colors=np.repeat(rgba[visible],3,axis=0)
 mesh=trimesh.Trimesh(vertices=xyz,faces=faces,vertex_colors=colors,process=False)
 scene.add_geometry(mesh,node_name=raw.stem)
 done.append({'tile':raw.name,'triangles':len(faces)})
output=dest/'native_r3d_triangles_approx.glb'
scene.export(output)
info={'output':output.name,'used':len(done),'missing_decoder':miss,
 'colored_triangles':sum(t['triangles'] for t in done),
 'note':'Actual native triangle vertices and RGBA; Gaussian compositing shader not reproduced.'}
(dest/'native_mesh_info.json').write_text(json.dumps(info,indent=2))
print(json.dumps({k:v for k,v in info.items() if k!='missing_decoder'},indent=2))
