# Derived for independent research; no existing viewer files modified.
#!/usr/bin/env python3
"""Exact Apple iOS27 native createSplats TRIANGLE vertices and packed RGBA -> viewer-space data.
Native triangle geometry is exact. Screen compositing/exponent still shader reconstruction.
"""
from pathlib import Path
import json,math,struct
import numpy as np
ROOT=Path('/opt/flyover-viewer')
IN=ROOT/'decoded-native/all-223'
R3D=ROOT/'native-r3d'
OUT=ROOT/'standard3dgs-research-20261014/corrected-triangles'
OUT.mkdir(parents=True,exist_ok=True)
VIEWER_DATA=ROOT/'www/data'
data=json.loads((VIEWER_DATA/'dataset.json').read_text())
x0=min(t['x'] for t in data['style99Tiles']);x1=max(t['x'] for t in data['style99Tiles'])
y0=min(t['y'] for t in data['style99Tiles']);y1=max(t['y'] for t in data['style99Tiles'])
cx=(x1-x0+1)*512*3.88/2;cz=(y1-y0+1)*512*3.88/2
manifest=json.loads((IN/'batch.json').read_text())['files']
all_tri=[];all_col=[];results=[];fail=[]
for item in manifest:
 name=item['file'];n=item['vertices']
 geom=IN/(name+'.native-triangle-f32');prop=IN/(name+'.native-material20')
 if not geom.exists() or not prop.exists() or geom.stat().st_size!=n*36 or prop.stat().st_size!=n*20:
  fail.append((name,'wrong geometry or property length'));continue
 local=np.fromfile(geom,dtype='<f4').reshape(3,n,3).transpose(1,0,2).astype('float64')
 mat=np.fromfile(prop,dtype='u1').reshape(n,20)
 # createSplats' exact low->high packed 8-bit channels are red, green, blue, alpha.
 rgba=mat[:,:4].copy()
 b=(R3D/name).read_bytes()
 off=b.find(bytes.fromhex('01010100016a'))+6
 if off<6:fail.append((name,'unknown geo transform'));continue
 R=np.array(struct.unpack_from('<9d',b,off)).reshape(3,3)
 E=np.array(struct.unpack_from('<3d',b,off+72))
 if not np.isclose(np.linalg.det(R),1.0,atol=1e-4):fail.append((name,'bad rotation'));continue
 ecef=local.reshape(-1,3)@R.T+E
 x,y,z=ecef.T;p=np.hypot(x,y)
 lon=np.arctan2(y,x);lat=np.arctan2(z,p*(1-6.69437999014e-3))
 for _ in range(6):
  N=6378137./np.sqrt(1-6.69437999014e-3*np.sin(lat)**2)
  h=p/np.cos(lat)-N
  lat=np.arctan2(z,p*(1-6.69437999014e-3*N/(N+h)))
 N=6378137./np.sqrt(1-6.69437999014e-3*np.sin(lat)**2)
 h=p/np.cos(lat)-N
 mx=(np.degrees(lon)+180.)/360.*16384
 my=(1.-np.arcsinh(np.tan(lat))/np.pi)/2.*16384
 world=np.stack([(mx-x0)*512*3.88-cx,h,(my-y0)*512*3.88-cz],axis=-1).reshape(n,3,3).astype('<f4')
 if not np.all(np.isfinite(world)):fail.append((name,'nonfinite coordinate'));continue
 visible=rgba[:,3]>0
 all_tri.append(world[visible]);all_col.append(rgba[visible])
 results.append(dict(tile=name,records=int(n),visible=int(np.count_nonzero(visible))))
tri=np.concatenate(all_tri,axis=0)
rgba=np.concatenate(all_col,axis=0)
assert len(tri)==len(rgba)==417650 and len(results)==223, (len(tri),len(results),fail)
print('total native triangles',sum(x['records'] for x in results),'visible',len(tri),'true vertices',len(tri)*3,'fail',fail)
bpos='corrected-native-223-triangles-positions.bin';bcol='corrected-native-223-triangles-rgba.bin'
(OUT/bpos).write_bytes(tri.astype('<f4').tobytes())
(OUT/bcol).write_bytes(rgba.tobytes())
from numpy.linalg import norm
area=norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5
med=np.percentile(area,[0,5,25,50,75,95,99,100])
summary={'provenance':'iOS27 VectorKit geo::r3d::createSplats actual triangle vertices and packed RGBA per style98 tile',
 'tileCount':len(results),'splatTrianglesFull':int(sum(x['records'] for x in results)),
 'splatTrianglesVisible':int(len(tri)),'triangleVerticesVisible':int(3*len(tri)),
 'vertexLayout':'each set of three positions is one native C3M/R3D splat triangle; float32 X east, Y ellipsoid altitude, Z south',
 'colorLayout':'native createSplats first uint32 little endian RGBA, four uint8 channels per triangle',
 'shapeAccuracy':'exact native 3D triangulation (not a synthesized point sprite or elliptical Gaussian)',
 'compositingAccuracy':'browser reconstruction of smooth triangle opacity, native exact exponent/compositing not yet matched',
 'areaSqMPercentiles':[round(float(v),4) for v in med],
 'sourceFiles':{'triangles':bpos,'color':bcol},'rawTriangleGeometries':results,
 'min':tri.reshape(-1,3).min(axis=0).round(4).tolist(),
 'max':tri.reshape(-1,3).max(axis=0).round(4).tolist()}
(OUT/'native-triangle-splats.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in summary.items() if k not in ('rawTriangleGeometries',)},ensure_ascii=False,indent=2))
