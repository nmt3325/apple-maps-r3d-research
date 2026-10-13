#!/usr/bin/env python3
"""Guard legacy Flyover C3M OBJ V convention against accidental reverse mapping.
We keep the native iOS27 R3D float2 UV data unchanged through geometry import.
- Three.js TextureLoader JPEG: flipY=true.
- trimesh glTF exporter internally flips V during export: visual UV MUST stay original.
"""
from pathlib import Path
import numpy as np, json, struct, trimesh,inspect
root=Path('/opt/flyover-viewer')
original_uv=json.loads((root/'www/data/native-c3m.json').read_text())
js=(root/'www/index.html').read_text()
source=(root/'export_original_textured_c3m.py').read_text()
old=(Path('/root/.desktop-mcp/linux-4ebec5ed/work/flyover-reverse-engineering/pkg/fly/exp/obj.go')).read_text()
assert 'e.objWriter.write(fmt.Fprintln' not in old or 'vtx.V' in old
assert '"vt", vtx.U, vtx.V' in old
assert 'texture.flipY=true' in js and 'texture.flipY=false' not in js.split('texture.flipY=true')[1]
assert "uv[:,1]=1.0-uv[:,1]" not in source, 'GLB UV flipped twice by application'
assert 'uv[:, 1] = 1.0 - uv[:, 1]' in inspect.getsource(trimesh.exchange.gltf), 'trimesh glTF V behavior changed'
count=0
for t in original_uv['tiles']:
 data=(root/'www/c3m-geometry'/t['geometry']).read_bytes()
 _,n,f,_=struct.unpack_from('<4I',data)
 uv=np.frombuffer(data,dtype='<f4',count=n*2,offset=16+n*12).reshape(-1,2)
 assert np.all(np.isfinite(uv)) and uv.min()>=0 and uv.max()<=1.001,(t['id'],uv.min(),uv.max())
 count+=1
glb=trimesh.load(root/'www/Apple-Flyover-iOS27-original-HEIC-textured-C3M-sample.glb',force='scene')
m=next(iter(glb.geometry.values()))
t=next(t for t in original_uv['tiles'] if t['z']==20 and t['x']==931324 and t['y']==412804 and t['h']==0)
data=(root/'www/c3m-geometry'/t['geometry']).read_bytes()
original=np.frombuffer(data,dtype='<f4',count=t['vertices']*2,offset=16+t['vertices']*12).reshape(-1,2)
assert len(m.visual.uv)==len(original)
assert np.allclose(m.visual.uv,original,atol=1e-6)
print(f'UV regression PASS: {count} original tiles + legacy OBJ convention + ThreeJS orientation + trimesh GLB roundtrip')
