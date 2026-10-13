#!/usr/bin/env python3
"""Extract ORIGINAL Apple R3D C3M polygon topology, vertex positions, per-corner UV,
normals, and matching one-to-one HEIC texture atlases (browser JPEG transcodes).

Memory layout validated directly from iOS27 VectorKit native world buffers:
+0x2b0 float3 positions, +0x2c8 float2 UVs, +0x2e0 float3 normals
+0x2f8/+0x310/+0x328 independent triangle-corner indices.
+0x338 HEIC material count, +0x340 material pointer.
All original arrays remain intact in /opt/flyover-viewer/decoded-native/c3m-all-223.
"""
from pathlib import Path
import json,struct,time
import numpy as np
BASE=Path('/opt/flyover-viewer')
RAW=BASE/'decoded-native/c3m-all-223'
ORIG=BASE/'native-r3d'
TEXTURES=BASE/'www/c3m-textures'
OUT=BASE/'www/c3m-geometry'
OUT.mkdir(exist_ok=True,parents=True)
SITE=BASE/'www/data'
dataset=json.loads((SITE/'dataset.json').read_text())
x0=min(t['x'] for t in dataset['style99Tiles']);x1=max(t['x'] for t in dataset['style99Tiles'])
y0=min(t['y'] for t in dataset['style99Tiles']);y1=max(t['y'] for t in dataset['style99Tiles'])
mpp=3.88;cx=(x1-x0+1)*512*mpp/2;cz=(y1-y0+1)*512*mpp/2
rows=json.loads((RAW/'batch.json').read_text())['files']
manifest=[];fail=[];start=time.time()
for rec in rows:
 name=rec['file'];prefix=RAW/name
 try:
  pos=np.fromfile(str(prefix)+'.c3m-2b0.bin',dtype='<f4').reshape(-1,3)
  uv=np.fromfile(str(prefix)+'.c3m-2c8.bin',dtype='<f4').reshape(-1,2)
  normal=np.fromfile(str(prefix)+'.c3m-2e0.bin',dtype='<f4').reshape(-1,3)
  ip=np.fromfile(str(prefix)+'.c3m-2f8.bin',dtype='<u4')
  iu=np.fromfile(str(prefix)+'.c3m-310.bin',dtype='<u4')
  inn=np.fromfile(str(prefix)+'.c3m-328.bin',dtype='<u4')
  assert len(ip)==len(iu)==len(inn) and len(ip)%3==0 and len(ip)>0
  assert ip.max()<len(pos) and iu.max()<len(uv) and inn.max()<len(normal)
  originals=(ORIG/name).read_bytes()
  off=originals.find(bytes.fromhex('01010100016a'))+6
  assert off>=6
  R=np.array(struct.unpack_from('<9d',originals,off)).reshape(3,3)
  E=np.array(struct.unpack_from('<3d',originals,off+72))
  assert abs(np.linalg.det(R)-1)<1e-4
  # Geodetic coordinates MUST exactly match earlier native-Splat viewer convention.
  xyz=pos.astype('float64')@R.T+E
  x,y,z=xyz.T
  lon=np.arctan2(y,x);p=np.hypot(x,y);esq=6.69437999014e-3;a=6378137.
  lat=np.arctan2(z,p*(1-esq))
  for _ in range(6):
   n=a/np.sqrt(1-esq*np.sin(lat)**2)
   h=p/np.cos(lat)-n
   lat=np.arctan2(z,p*(1-esq*n/(n+h)))
  n=a/np.sqrt(1-esq*np.sin(lat)**2)
  height=p/np.cos(lat)-n
  zoom14=16384
  mx=(np.degrees(lon)+180)/360*zoom14
  my=(1-np.arcsinh(np.tan(lat))/np.pi)/2*zoom14
  world=np.stack([(mx-x0)*512*mpp-cx,height,(my-y0)*512*mpp-cz],axis=1).astype('<f4')
  # native normal is a local xyz; rotate into ECEF and ENU / south viewer axes
  ecefNorm=normal.astype('float64')@R.T
  # Normals are indexed independently from positions; their array size is different.
  # Use local tile ECEF tangent basis (tile spans only tens of meters).
  la=float(np.median(lat));lo=float(np.median(lon))
  east=np.array([-np.sin(lo),np.cos(lo),0.0])
  up=np.array([np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)])
  south=np.array([np.sin(la)*np.cos(lo),np.sin(la)*np.sin(lo),-np.cos(la)])
  viewnorm=np.stack([ecefNorm@east,ecefNorm@up,ecefNorm@south],axis=1).astype('<f4')
  viewnorm/=np.maximum(np.linalg.norm(viewnorm,axis=1,keepdims=True),1e-8)
  corners=np.column_stack((ip,iu,inn))
  unique,rev=np.unique(corners,axis=0,return_inverse=True)
  v3=world[unique[:,0]]
  v2=uv[unique[:,1]].astype('<f4')
  vn=viewnorm[unique[:,2]]
  faces=rev.astype('<u4').reshape(-1,3)
  texture=TEXTURES/(name.replace('.r3d','')+'.jpg')
  assert texture.is_file() and texture.stat().st_size>500
  binaryName=name+'.polybuf'
  with (OUT/binaryName).open('wb') as f:
   f.write(struct.pack('<4I',0x4d33434d,len(unique),len(faces),0))
   f.write(v3.astype('<f4').tobytes())
   f.write(v2.tobytes());f.write(vn.astype('<f4').tobytes());f.write(faces.tobytes())
  tilestring=name.replace('.r3d','')
  xyz_center=v3.mean(axis=0)
  bmin=v3.min(axis=0);bmax=v3.max(axis=0)
  meta={'id':tilestring,'z':int(tilestring.split('_')[1][1:]),'x':int(tilestring.split('_')[2][1:]),'y':int(tilestring.split('_')[3][1:]),'h':int(tilestring.split('_')[4][1:]),
        'name':name,'geometry':binaryName,'texture':f'c3m-textures/{texture.name}',
        'vertices':len(unique),'originalPositions':len(pos),'originalUV':len(uv),'originalNormals':len(normal),
        'triangles':len(faces),'center':xyz_center.round(4).tolist(),
        'boundsMin':bmin.round(4).tolist(),'boundsMax':bmax.round(4).tolist(),
        'bytes':(OUT/binaryName).stat().st_size}
  manifest.append(meta)
 except Exception as ex:fail.append({'tile':name,'exception':str(ex)})
report={'source':'Apple iOS27 VectorKit decoded R3D original C3M polygon positions, topology, normals and UV and extracted original HEIC texture atlases re-encoded as browser JPEG.',
 'textureNote':'Each image comes directly from the corresponding style98 tile; JPEG is browser-compatible conversion of original HEIC (not synthetic artwork).',
 'originalPolygonTileCount':len(manifest),'totalTriangles':sum(t['triangles'] for t in manifest),
 'combinedUniqueVertices':sum(t['vertices'] for t in manifest),
 'missingOrFailed':fail,'order':'vertex XYZ float32, UV float32x2, normal float32x3, triangle indices uint32x3, preceded by four uint32 header',
 'tiles':manifest}
(SITE/'native-c3m.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print('valid',len(manifest),'failed',len(fail),'triangles',report['totalTriangles'],
      'vertices',report['combinedUniqueVertices'],
      'bytes',sum(t['bytes'] for t in manifest),'elapsed',round(time.time()-start,1))
print('sample',(manifest[0] if manifest else 'none'),'failures',fail[:5])
