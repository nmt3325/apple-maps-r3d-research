#!/usr/bin/env python3
"""Combine genuine Apple iOS27 R3D C3M textured polygons with genuine soft triangular
splats in independent glTF scene nodes. Note: glTF generic renderers cannot encode Apple's
custom per-fragment triangular opacity kernel; use WebGL viewer for the soft splats.
"""
from pathlib import Path
import sys,time,trimesh
root=Path('/opt/flyover-viewer/www')
z=sys.argv[1] if len(sys.argv)>1 else '19'
mesh=trimesh.load(root/('Apple-Flyover-iOS27-original-HEIC-textured-C3M-'+z+'.glb'),force='scene')
splats=trimesh.load(root/'Apple-Flyover-iOS27-native-417650-triangles.glb',force='scene')
out=trimesh.Scene()
for name,g in mesh.geometry.items():
 out.add_geometry(g,geom_name='ORIGINAL_C3M_HEIC_ATLAS_'+name,node_name='APPLE_NATIVE_TEXTURED_POLYGON_'+name)
for name,g in splats.geometry.items():
 out.add_geometry(g,geom_name='ORIGINAL_NATIVE_SPLATS_'+name,node_name='APPLE_NATIVE_SOFT_TRIANGLE_SPLATS_Requires_Custom_Shader')
dest=root/('Apple-Flyover-iOS27-original-textured-C3M-plus-R3D-splats-'+z+'.glb')
out.export(dest)
reimport=trimesh.load(dest,force='scene')
meshes=list(reimport.geometry.values())
print('output',dest.name,'bytes',dest.stat().st_size,'nodes',len(meshes),'polygons',sum(len(g.faces) for g in meshes),
 'textures',sum(getattr(g.visual.material,'baseColorTexture',None) is not None for g in meshes if g.visual.kind=='texture'),
 'splatTriangles',sum(len(g.faces) for n,g in reimport.geometry.items() if 'SPLATS' in n),
 flush=True)
