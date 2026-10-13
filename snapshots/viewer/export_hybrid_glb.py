from pathlib import Path
import numpy as np,trimesh,json
root=Path('/opt/flyover-viewer/www')
native=trimesh.load(root/'Apple-Flyover-iOS27-native-417650-triangles.glb',force='scene')
nmesh=next(iter(native.geometry.values()))
proxy=trimesh.load(root/'Flyover-captured-heightfield.glb',force='scene')
out=trimesh.Scene()
out.add_geometry(nmesh,geom_name='ORIGINAL_R3D_createSplats_triangles_RGBA',node_name='APPLE_R3D_417650_SPLATS')
xmin,xmax=-181.7,492.1;zmin,zmax=-56.8,678.1
face_total=0
for name,g in proxy.geometry.items():
 verts=g.vertices.copy()
 verts[:,0]-=1986.56;verts[:,2]-=1986.56
 verts[:,1]=51.68+verts[:,1]*0.394
 centers=verts[g.faces].mean(axis=1)
 ok=(centers[:,0]>=xmin)&(centers[:,0]<=xmax)&(centers[:,2]>=zmin)&(centers[:,2]<=zmax)
 sub=trimesh.Trimesh(vertices=verts,faces=g.faces[ok],process=False)
 if len(sub.faces)==0:continue
 out.add_geometry(sub,geom_name='ESTIMATED_PNG_STYLE99_HEIGHT_PROXY_'+name,node_name='NOT_NATIVE_C3M_'+name)
 face_total+=len(sub.faces)
p=root/'Apple-Flyover-hybrid-native-splats-calibrated-proxy.glb'
out.export(p)
check=trimesh.load(p,force='scene')
print('Native triangles',len(nmesh.faces),'PNG proxy triangles',face_total,'model bytes',p.stat().st_size)
print('readback meshes',[(n,len(g.faces)) for n,g in check.geometry.items()])
(root/'data/hybrid-export.json').write_text(json.dumps({'nativeTriangles':len(nmesh.faces),'proxyTriangles':face_total,'file':p.name,'important':'Polygon layer is only a calibrated style99 PNG approximation, not Apple original C3mModel. GLB cannot reproduce the native fragment shader attenuation.'},indent=2))
