#!/usr/bin/env python3
"""Export real Apple R3D decoded positions and per-point RGBA/material fields.
Coordinates decoded by iOS27 VectorKit. RGB/alpha mapping verified in createSplats ARM64.
Other fields are retained raw without claiming covariance semantics.
"""
import numpy as np,json, pathlib
d=pathlib.Path('/opt/flyover-viewer/decoded-native')
out=pathlib.Path('/opt/flyover-viewer/www/data')
a=np.fromfile(d/'r3d_native_4099_attributes.bin',dtype='<f4').reshape(-1,8)
coords=np.fromfile(out/'native_R3D_z20_x931324_y412804_h0_4099xyz.bin',dtype='<f4').reshape(-1,3)
assert len(a)==len(coords)==4099
safe=np.nan_to_num(a,nan=0.0,posinf=0.0,neginf=0.0)
# channel 0 alpha, channels 1-3 RGB; these match iOS createSplats conversion
rgba=np.clip(safe[:,[1,2,3,0]],0,1).astype('<f4')
raw= np.asarray(safe[:,4:8],dtype='<f4')
file='native_R3D_z20_x931324_y412804_h0_4099_rgba_shape.bin'
data=np.concatenate([rgba,raw],axis=1)
(out/file).write_bytes(data.tobytes())
# portable PLY storing the actual position, native RGBA and original remaining four floats
names=['x','y','z','red','green','blue','alpha','r3d_kind7','r3d_kind6_0','r3d_kind6_1','r3d_kind4']
ty=np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('red','u1'),('green','u1'),('blue','u1'),('alpha','u1'),
             ('r3d_kind7','<f4'),('r3d_kind6_0','<f4'),('r3d_kind6_1','<f4'),('r3d_kind4','<f4')])
points=np.zeros(len(coords),dtype=ty)
for j,k in enumerate(['x','y','z']):points[k]=coords[:,j]
rgbbytes=np.rint(rgba*255).astype(np.uint8)
for j,k in enumerate(['red','green','blue','alpha']):points[k]=rgbbytes[:,j]
for j,k in enumerate(['r3d_kind7','r3d_kind6_0','r3d_kind6_1','r3d_kind4']):points[k]=raw[:,j]
header='ply\nformat binary_little_endian 1.0\ncomment Actual iOS27 VectorKit decoded R3D splat XYZ and RGB/alpha. Other fields semantics unverified.\n'
header+=f'element vertex {len(coords)}\n'
header+=''.join(f'property {"uchar" if ty.fields[k][0].kind=="u" else "float"} {k}\n' for k in ty.names)
header+='end_header\n'
ply=out/'Apple-R3D-native-4099-colored-points.ply'
with ply.open('wb') as f:f.write(header.encode());f.write(points.tobytes())
rep={'actualDecodedPositions':len(coords),'nativeRgbAlphaChannels':'8 floats/point: first alpha, next 3 RGB; mapping from Apple createSplats',
 'remaining':'type 7 = float at index4, type6 = vec2 indices5 and6, type4 = float index7; semantics not confirmed',
 'nanRgbCount':int(np.isnan(a[:,1:4]).any(axis=1).sum()),'fullyTransparentCount':int(np.count_nonzero(rgba[:,3]==0)),
 'visiblePoints':int(np.count_nonzero(rgba[:,3]>0)), 'customAttributeFilename':file,
 'portablePointCloudPLY':ply.name,'plyBytes':ply.stat().st_size}
(out/'native-rgba.json').write_text(json.dumps(rep,indent=2))
print(json.dumps(rep,indent=2))
