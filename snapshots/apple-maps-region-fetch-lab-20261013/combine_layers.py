#!/usr/bin/env python3
"""Combine separate native triangular splat approximation and polygonized DEM."""
from pathlib import Path
import json,sys,trimesh
d=Path(sys.argv[1]).resolve()
files=['native_r3d_triangles_approx.glb','polygonized_height_approx.glb']
hybrid=trimesh.Scene()
stats={}
for name in files:
 scene=trimesh.load_scene(d/name)
 stats[name]={'bounds':scene.bounds.tolist(),'geometry':len(scene.geometry)}
 for label,mesh in scene.geometry.items():
  hybrid.add_geometry(mesh,geom_name=name+'-'+str(label))
target=d/'hybrid_preview_approx.glb'
hybrid.export(target)
stats['hybrid']={'file':target.name,'bytes':target.stat().st_size,
 'total_triangles':sum(len(g.faces) for g in hybrid.geometry.values()),
 'geometry_count':len(hybrid.geometry)}
(d/'hybrid_summary.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
