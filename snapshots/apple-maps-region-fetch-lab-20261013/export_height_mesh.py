#!/usr/bin/env python3
"""Polygonize captured style99 16-bit height rasters (vertical unit uncalibrated)."""
import sys,re,math,json
from pathlib import Path
import numpy as np
from PIL import Image
import trimesh
out=Path(sys.argv[1]).resolve()
step=int(sys.argv[2]) if len(sys.argv)>2 else 2
if step<1 or 512%step:raise SystemExit('step must divide 512')
sources=list(out.glob('s99_z14_*.png'))
if not sources:raise SystemExit('No style99 height files')
tiles=[]
for path in sources:
 m=re.search(r'_x(\d+)_y(\d+)(?:_|\.)',path.name)
 tiles.append((int(m[1]),int(m[2]),path))
minx=min(t[0] for t in tiles);miny=min(t[1] for t in tiles)
scene=trimesh.Scene()
for x,y,path in tiles:
 heights=np.asarray(Image.open(path),dtype='<u2')[::step,::step].astype('float32')
 n=heights.shape[0]
 lat=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y+.5)/16384))))
 tilemeters=40075016.686*math.cos(math.radians(lat))/16384
 ix,iy=np.meshgrid(np.arange(n),np.arange(n))
 east=(x-minx+(ix+.5)*step/512)*tilemeters
 south=(y-miny+(iy+.5)*step/512)*tilemeters
 vertices=np.stack([east,heights,south],axis=-1).reshape(-1,3)
 a=(np.arange(n-1)[:,None]*n+np.arange(n-1)[None,:]).ravel()
 faces=np.stack([a,a+n,a+1,a+1,a+n,a+n+1],axis=-1).reshape(-1,3)
 mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
 scene.add_geometry(mesh,node_name=path.stem)
dest=out/'polygonized_height_approx.glb'
scene.export(dest)
metadata={'file':dest.name,'source':'captured style99 PNG elevation raster','vertical_units':'unknown; uncalibrated sample value','source_tiles':len(tiles),
          'vertices':sum(len(g.vertices) for g in scene.geometry.values()),
          'triangles':sum(len(g.faces) for g in scene.geometry.values())}
(out/'polygon_mesh_info.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps(metadata,indent=2))
