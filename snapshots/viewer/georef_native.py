#!/usr/bin/env python3
"""Georeference REAL 4099 decoded native Apple R3D 'Splats' XYZ using R3D's 3x3 ECEF transform.
No heightfield or invented geometry is used for points. Colors/properties are NOT decoded.
"""
from pathlib import Path
import json,math,struct,numpy as np
root=Path('/opt/flyover-viewer')
p=root/'decoded-native/r3d_native_4099_positions.bin'
raw=root/'native-r3d/r3d_z20_x931324_y412804_h0.r3d'
viewer=root/'www/data'
meta=json.loads((viewer/'dataset.json').read_text())
x0=min(t['x'] for t in meta['style99Tiles'])
x1=max(t['x'] for t in meta['style99Tiles'])
y0=min(t['y'] for t in meta['style99Tiles'])
y1=max(t['y'] for t in meta['style99Tiles'])
mpp=3.88
cx=(x1-x0+1)*512*mpp/2
cz=(y1-y0+1)*512*mpp/2
points=np.fromfile(p,dtype='<f4').reshape(-1,3).astype('float64')
b=raw.read_bytes()
ofs=b.find(bytes.fromhex('01010100016a'))+6
assert ofs>6
rot=np.array(struct.unpack_from('<9d',b,ofs)).reshape(3,3)
ecef=np.array(struct.unpack_from('<3d',b,ofs+72))
assert np.isclose(np.linalg.det(rot),1,atol=1e-6)
# world: XYZ (m) -> ECEF XYZ (m)
xyz=points@rot.T+ecef
x,y,z=xyz.T
a=6378137.;e2=6.69437999014e-3
lon=np.arctan2(y,x)
q=np.hypot(x,y)
lat=np.arctan2(z,q*(1-e2))
for _ in range(7):
 N=a/np.sqrt(1-e2*np.sin(lat)**2)
 altitude=q/np.cos(lat)-N
 lat=np.arctan2(z,q*(1-e2*N/(N+altitude)))
N=a/np.sqrt(1-e2*np.sin(lat)**2)
altitude=q/np.cos(lat)-N
n=2**14
mx=(np.degrees(lon)+180)/360*n
my=(1-np.arcsinh(np.tan(lat))/np.pi)/2*n
assert np.all((mx>=931324/64-0.001)&(mx<=931325/64+0.002))
assert np.all((my>=412804/64-0.001)&(my<=412805/64+0.002))
out=np.column_stack([(mx-x0)*512*mpp-cx,altitude,(my-y0)*512*mpp-cz]).astype('<f4')
assert np.all(np.isfinite(out))
fn='native_R3D_z20_x931324_y412804_h0_4099xyz.bin'
(viewer/fn).write_bytes(out.tobytes())
report={'filename':fn,'z':20,'x':931324,'y':412804,'h':0,
 'source':'iOS27 VectorKit native r3d_world_read_mem output. Not heightfield derived.',
 'count':len(out),'dtype':'float32x3','coordinate':'viewer X east, Y true ECEF-derived ellipsoid height in meters, Z south',
 'rotation':rot.tolist(),'ecefAnchor':ecef.tolist(),
 'minimum':out.min(axis=0).round(4).tolist(),'maximum':out.max(axis=0).round(4).tolist(),
 'center':out.mean(axis=0).round(4).tolist(),
 'appearance':'no original Gaussian color, covariance, opacity or radii decoded yet'}
(viewer/'native-r3d.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
