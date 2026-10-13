from pathlib import Path
import json,struct,numpy as np
root=Path('/opt/flyover-viewer/www')
doc=json.loads((root/'data/native-c3m.json').read_text())
issues=[]; triangles=0; verts=0; ratios=[]
for row in doc['tiles']:
 try:
  b=(root/'c3m-geometry'/row['geometry']).read_bytes()
  mag,n,f,z=struct.unpack_from('<4I',b)
  assert mag==0x4d33434d and n==row['vertices'] and f==row['triangles'] and z==0
  assert len(b)==16+n*32+f*12
  pos=np.frombuffer(b,'<f4',count=n*3,offset=16).reshape(-1,3)
  uv=np.frombuffer(b,'<f4',count=n*2,offset=16+n*12).reshape(-1,2)
  normals=np.frombuffer(b,'<f4',count=n*3,offset=16+n*20).reshape(-1,3)
  face=np.frombuffer(b,'<u4',count=f*3,offset=16+n*32)
  assert np.isfinite(pos).all() and np.isfinite(uv).all() and np.isfinite(normals).all()
  assert face.max()<n and uv.min()>=0 and uv.max()<1.001
  assert (root/row['texture']).stat().st_size>500
  triangles+=f;verts+=n
  ratios.append(float(np.mean(np.linalg.norm(normals,axis=1))))
 except Exception as e:issues.append([row['id'],str(e)])
print('mesh tiles',len(doc['tiles']),'triangles',triangles,'vertices',verts,'failures',issues[:10])
print('mean normals length min/max',min(ratios),max(ratios))
assert not issues
