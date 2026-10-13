#!/usr/bin/env python3
"""Reconstruct combined georeferenced iOS27 R3D point positions and native RGBA over all 223 tiles.
Heightfield polygons and native R3D splat points remain SEPARATE render layers.
Splat projected size/covariance are intentionally not invented.
"""
from pathlib import Path
import json,struct,math,os
import numpy as np
B=Path('/opt/flyover-viewer')
root=B/'decoded-native/all-223'
raw=B/'native-r3d'
web=B/'www/data'
idx=json.loads((root/'batch.json').read_text())
dataset=json.loads((web/'dataset.json').read_text())
x0=min(x['x'] for x in dataset['style99Tiles']);x1=max(x['x'] for x in dataset['style99Tiles'])
y0=min(y['y'] for y in dataset['style99Tiles']);y1=max(y['y'] for y in dataset['style99Tiles'])
cx=(x1-x0+1)*512*3.88/2;cz=(y1-y0+1)*512*3.88/2
poslist=[];rgbaList=[];rawShape=[];normalList=[];diagnostics=[];bad=[]
for item in idx['files']:
 name=item['file'];inpath=root/(name+'.decoded')
 if not inpath.exists():bad.append((name,'missing'));continue
 b=inpath.read_bytes()
 magic,n,channels,_=struct.unpack_from('<4I',b,0)
 if magic!=0x31443352 or channels!=8 or len(b)!=16+n*(12+8*4):bad.append((name,'invalid decoded header'));continue
 xyz=np.frombuffer(b,dtype='<f4',count=n*3,offset=16).reshape(-1,3).astype('float64')
 a=np.frombuffer(b,dtype='<f4',count=n*8,offset=16+n*12).reshape(-1,8)
 orig=raw/name
 if not orig.exists():bad.append((name,'missing R3D original'));continue
 payload=orig.read_bytes()
 at=payload.find(bytes.fromhex('01010100016a'))+6
 if at<6:bad.append((name,'no transform'));continue
 R=np.array(struct.unpack_from('<9d',payload,at)).reshape(3,3)
 E=np.array(struct.unpack_from('<3d',payload,at+72))
 if not np.isclose(np.linalg.det(R),1,atol=1e-4):bad.append((name,'invalid rotation matrix'));continue
 pts=xyz@R.T+E
 x,y,z=pts.T
 lon=np.arctan2(y,x);p=np.hypot(x,y);esq=6.69437999014e-3;earth=6378137.
 lat=np.arctan2(z,p*(1-esq))
 for _ in range(5):
  rn=earth/np.sqrt(1-esq*np.sin(lat)**2)
  alt=p/np.cos(lat)-rn
  lat=np.arctan2(z,p*(1-esq*rn/(rn+alt)))
 rn=earth/np.sqrt(1-esq*np.sin(lat)**2)
 alt=p/np.cos(lat)-rn
 n14=16384
 mx=(np.degrees(lon)+180)/360*n14
 my=(1-np.arcsinh(np.tan(lat))/np.pi)/2*n14
 world=np.stack([(mx-x0)*512*3.88-cx,alt,(my-y0)*512*3.88-cz],axis=1).astype('<f4')
 if not np.all(np.isfinite(world)):bad.append((name,'invalid geodetics'));continue
 # Untrusted NaN RGB exists in 65 points of one tile. The native splat renderer's
 # float-to-byte conversion writes 0 for nonfinite values.
 clean=np.nan_to_num(a,nan=0,posinf=0,neginf=0)
 rgba=np.rint(np.clip(clean[:,[1,2,3,0]],0,1)*255).astype(np.uint8)
 more=clean[:,4:8].astype('<f4')
 # Native type-6 vec2 is octahedrally encoded normal, as iOS27 Flyover::splat_vertex.
 nxy=clean[:,5:7].astype('float64')*2.0-1.0
 nz=1-np.abs(nxy[:,0])-np.abs(nxy[:,1])
 adjust=np.maximum(-nz,0.0)
 nx=nxy[:,0]+np.where(nxy[:,0]>=0,-adjust,adjust)
 ny=nxy[:,1]+np.where(nxy[:,1]>=0,-adjust,adjust)
 localNormal=np.column_stack([nx,ny,nz])
 localNormal/=np.maximum(np.linalg.norm(localNormal,axis=1,keepdims=True),1e-10)
 ecefNormal=localNormal@R.T
 east=np.stack([-np.sin(lon),np.cos(lon),np.zeros_like(lon)],axis=1)
 up=np.stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)],axis=1)
 south=np.stack([np.sin(lat)*np.cos(lon),np.sin(lat)*np.sin(lon),-np.cos(lat)],axis=1)
 normals=np.stack([(ecefNormal*east).sum(axis=1),
                   (ecefNormal*up).sum(axis=1),
                   (ecefNormal*south).sum(axis=1)],axis=1).astype('<f4')
 poslist.append(world);rgbaList.append(rgba);rawShape.append(more);normalList.append(normals)
 diagnostics.append({'name':name,'count':int(n),'visible':int(np.count_nonzero(rgba[:,3]>0)),
                     'rangeLat':[float(np.min(np.degrees(lat))),float(np.max(np.degrees(lat)))],
                     'rangeLon':[float(np.min(np.degrees(lon))),float(np.max(np.degrees(lon)))],
                     'rangeHeight':[float(alt.min()),float(alt.max())]})
print('processed',len(diagnostics),'errors',bad[:15])
xyz=np.concatenate(poslist);rgb=np.concatenate(rgbaList);raw=np.concatenate(rawShape);normals=np.concatenate(normalList)
print('points',len(xyz),'nonzero-opacity',np.count_nonzero(rgb[:,3]),'positionBounds',xyz.min(0),xyz.max(0))
# Full resolution real R3D PLY -- every splat position, all color values and four unknown shape fields.
dtype=np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('red','u1'),('green','u1'),('blue','u1'),('alpha','u1'),
 ('r3d_kind7','<f4'),('r3d_kind6_0','<f4'),('r3d_kind6_1','<f4'),('r3d_kind4','<f4')])
points=np.zeros(len(xyz),dtype=dtype)
for j,k in enumerate(['x','y','z']):points[k]=xyz[:,j]
for j,k in enumerate(['red','green','blue','alpha']):points[k]=rgb[:,j]
for j,k in enumerate(['r3d_kind7','r3d_kind6_0','r3d_kind6_1','r3d_kind4']):points[k]=raw[:,j]
header='ply\nformat binary_little_endian 1.0\ncomment iOS27 VectorKit native R3D float XYZ + RGB and alpha; shape semantics not yet verified.\n'
header+=f'element vertex {len(points)}\n'
header+=''.join(f'property {"uchar" if dtype.fields[k][0].kind=="u" else "float"} {k}\n' for k in dtype.names)
header+='end_header\n'
ply=B/'www/Apple-R3D-native-all-223-colored-points.ply'
with ply.open('wb') as f:f.write(header.encode());f.write(points.tobytes())
# Browser-only: skip fully transparent splats to improve render speed but full PLY contains all.
mask=rgb[:,3]>0
vxyz=xyz[mask];vrgb=rgb[mask];vraw=raw[mask];vnorm=normals[mask]
pre='native-223-visible'
(web/(pre+'-positions.bin')).write_bytes(vxyz.astype('<f4').tobytes())
(web/(pre+'-rgba.bin')).write_bytes(vrgb.tobytes())
(web/(pre+'-shapes.bin')).write_bytes(vraw.astype('<f4').tobytes())
(web/(pre+'-normals.bin')).write_bytes(vnorm.astype('<f4').tobytes())
m={'source':'223 captured style98 R3D tiles, decoded by iOS27 VectorKit r3d_world_read_mem',
 'totalTiles':len(diagnostics),'totalPositionRecords':len(xyz),
 'visibleAlphaNonzero':len(vxyz),'hiddenZeroAlpha':len(xyz)-len(vxyz),
 'color': 'Apple native RGB/alpha mapped according to createSplats; no invented colors',
 'splatGeometry':'Native octahedral normals decoded from iOS27 Metal shader. Native triangle vertex geometry and radius not yet resolved.',
 'coordinate':'three.js X east, Y ECEF ellipsoid-derived altitude, Z south; meters',
 'renderFiles':{'positions':pre+'-positions.bin','rgba':pre+'-rgba.bin','shape':pre+'-shapes.bin','normals':pre+'-normals.bin'},
 'downloadPLY':ply.name,'byteSizePLY':ply.stat().st_size,
 'boundsMin':xyz.min(0).round(3).tolist(),'boundsMax':xyz.max(0).round(3).tolist(),
 'normalStats':{'meanEastUpSouth':normals.mean(axis=0).round(5).tolist(),'fractionUp':float(np.mean(normals[:,1]>0.5))},
 'tileRanges':diagnostics}
(web/'native-all.json').write_text(json.dumps(m,indent=2))
print('browserBytes',sum((web/q).stat().st_size for q in m['renderFiles'].values()))
print('PLYbytes',ply.stat().st_size,'all successful',not bad)
