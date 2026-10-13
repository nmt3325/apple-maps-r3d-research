#!/usr/bin/env python3
"""Add genuine iOS27 Flyover splat normals (octahedral encoding) to every R3D point.
The two compressed normal components are read from R3D channels 5 and 6.
Decoding exactly follows Flyover::splat_vertex Metal LLVM: oct xy, restore z,
fold negative hemisphere, normalize, transform through tile ECEF to east/up/south.
"""
from pathlib import Path
import struct,json,math
import numpy as np
b=Path('/opt/flyover-viewer')
files=b/'www/data'
batch=json.loads((b/'decoded-native/all-223/batch.json').read_text())['files']
source=b/'www/Apple-R3D-native-all-223-colored-points.ply'
payload=source.read_bytes()
start=payload.index(b'end_header\n')+len(b'end_header\n')
structtype=np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('red','u1'),('green','u1'),('blue','u1'),('alpha','u1'),
 ('r3d_kind7','<f4'),('r3d_kind6_0','<f4'),('r3d_kind6_1','<f4'),('r3d_kind4','<f4')])
records=np.frombuffer(payload,dtype=structtype,offset=start).copy()
assert len(records)==736915
normals=[]
offset=0
for item in batch:
 n=item['vertices'];name=item['file']
 seg=records[offset:offset+n];offset+=n
 uv=np.column_stack([seg['r3d_kind6_0'],seg['r3d_kind6_1']]).astype('float64')*2.0-1.0
 z=1-np.abs(uv).sum(axis=1)
 t=np.maximum(-z,0)
 uv+=np.where(uv>=0,-t[:,None],t[:,None])
 loc=np.column_stack([uv,z])
 loc/=np.linalg.norm(loc,axis=1,keepdims=True)
 raw=(b/'native-r3d'/name).read_bytes()
 at=raw.find(bytes.fromhex('01010100016a'))+6
 R=np.array(struct.unpack_from('<9d',raw,at)).reshape(3,3)
 E=np.array(struct.unpack_from('<3d',raw,at+72))
 x,y,ecefZ=E
 lon=math.atan2(y,x);p=math.hypot(x,y)
 e2=.00669437999014;A=6378137.
 lat=math.atan2(ecefZ,p*(1-e2))
 for _ in range(6):
  rn=A/math.sqrt(1-e2*math.sin(lat)**2)
  alt=p/math.cos(lat)-rn
  lat=math.atan2(ecefZ,p*(1-e2*rn/(rn+alt)))
 east=np.array([-math.sin(lon),math.cos(lon),0])
 up=np.array([math.cos(lat)*math.cos(lon),math.cos(lat)*math.sin(lon),math.sin(lat)])
 south=np.array([math.sin(lat)*math.cos(lon),math.sin(lat)*math.sin(lon),-math.cos(lat)])
 enu=np.stack([east,up,south],axis=0)
 world=loc@R.T@enu.T
 world/=np.linalg.norm(world,axis=1,keepdims=True)
 normals.append(world.astype('<f4'))
assert offset==len(records)
norm=np.concatenate(normals)
assert np.all(np.isfinite(norm))
visible=records['alpha']>0
(files/'native-223-visible-normals.bin').write_bytes(norm[visible].tobytes())
dt=np.dtype(structtype.descr[:3]+[('nx','<f4'),('ny','<f4'),('nz','<f4')]+structtype.descr[3:])
out=np.zeros(len(records),dtype=dt)
for k in structtype.names:out[k]=records[k]
for i,k in enumerate(('nx','ny','nz')):out[k]=norm[:,i]
header='ply\nformat binary_little_endian 1.0\ncomment Actual iOS27 R3D XYZ/RGBA and octahedral normals decoded from splat_vertex Metal AIR.\n'
header+=f'element vertex {len(out)}\n'
header+=''.join(f'property {"uchar" if out.dtype.fields[k][0].kind=="u" else "float"} {k}\n' for k in out.dtype.names)
header+='end_header\n'
dest=b/'www/Apple-R3D-native-all-223-with-normals.ply'
with dest.open('wb') as f:f.write(header.encode());f.write(out.tobytes())
print('files',len(batch),'points',len(out),'normalsShape',norm.shape,'medianY',np.median(norm[:,1]),'unitLengthMean',np.linalg.norm(norm,axis=1).mean(),'plyBytes',dest.stat().st_size)
