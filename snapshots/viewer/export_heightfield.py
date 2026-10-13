#!/usr/bin/env python3
"""Export CT104 *observed* 16-bit Apple map heightfield samples as textured-independent GLB geometry.
This is NOT an export of style=98 Gaussian splat primitives.
"""
import json,pathlib
import numpy as np
import trimesh
base=pathlib.Path('/opt/flyover-viewer/www')
d=json.loads((base/'data/dataset.json').read_text())
tiles=d['style99Tiles']
x0=min(t['x'] for t in tiles);y0=min(t['y'] for t in tiles)
unit=3.88
geo=trimesh.Scene()
for meta in tiles:
    b=(base/'data'/meta['file']).read_bytes()
    height=np.frombuffer(b,dtype='<u2').reshape(256,256).astype('float32')
    xx,zz=np.meshgrid(np.linspace(0,1,256,dtype=np.float32),np.linspace(0,1,256,dtype=np.float32))
    x=(meta['x']-x0+xx)*512*unit
    z=(meta['y']-y0+zz)*512*unit
    y=height*2.0
    vertices=np.stack([x,y,z],axis=-1).reshape(-1,3)
    a=np.arange(255*255,dtype=np.uint32).reshape(255,255)
    jj,ii=np.indices((255,255));a=(jj*256+ii).ravel()
    faces=np.stack([a,a+256,a+1,a+1,a+256,a+257],axis=-1).reshape(-1,3)
    h=np.clip(height.reshape(-1)/220,0,1)
    colors=np.stack([75+160*h,130+57*h,93-30*h,np.full_like(h,255)],axis=-1).astype(np.uint8)
    mesh=trimesh.Trimesh(vertices=vertices,faces=faces,vertex_colors=colors,process=False)
    geo.add_geometry(mesh,node_name=f"terrain_z{meta['z']}_{meta['x']}_{meta['y']}",geom_name=f"z{meta['z']}_{meta['x']}_{meta['y']}")
path=base/'Flyover-captured-heightfield.glb'
geo.export(path)
print('exported',path,'size',path.stat().st_size,'geometry_count',len(geo.geometry),'faces',sum(len(m.faces) for m in geo.geometry.values()),'vertices',sum(len(m.vertices) for m in geo.geometry.values()))
