#!/usr/bin/env python3
"""Gaussian PLY approximation GENERATED FROM observed style=99 map heightfield samples.
NOT a decoder for Apple's native style=98 geometry/splat tiles.
"""
from pathlib import Path
import json,numpy as np,math
base=Path('/opt/flyover-viewer/www')
d=json.loads((base/'data/dataset.json').read_text())
ts=d['style99Tiles'];x0=min(t['x'] for t in ts);y0=min(t['y'] for t in ts)
dtype=np.dtype([
 ('x','<f4'),('y','<f4'),('z','<f4'),
 ('nx','<f4'),('ny','<f4'),('nz','<f4'),
 ('f_dc_0','<f4'),('f_dc_1','<f4'),('f_dc_2','<f4'),
 ('opacity','<f4'),
 ('scale_0','<f4'),('scale_1','<f4'),('scale_2','<f4'),
 ('rot_0','<f4'),('rot_1','<f4'),('rot_2','<f4'),('rot_3','<f4')
])
arr=np.zeros((len(ts)*256*256,),dtype=dtype)
for it,t in enumerate(ts):
 off=it*256*256
 mat=np.frombuffer((base/'data'/t['file']).read_bytes(),'<u2').reshape(256,256)
 gx,gz=np.meshgrid(np.linspace(0,1,256,dtype='float32'),np.linspace(0,1,256,dtype='float32'))
 height=mat.ravel().astype('float32')
 sub=arr[off:off+65536]
 sub['x']=((t['x']-x0+gx.ravel())*512*3.88)
 sub['z']=((t['y']-y0+gz.ravel())*512*3.88)
 sub['y']=height*2
 sub['ny']=1
 brightness=np.clip(height/220,0,1)
 rgb=np.stack([0.28+0.48*brightness,0.48+0.22*brightness,0.31-0.12*brightness],axis=-1)
 for k in range(3):sub['f_dc_'+str(k)]=(rgb[:,k]-0.5)/0.28209479177387814
 sub['opacity']=np.log(0.9/0.1)
 for k in range(3):sub['scale_'+str(k)]=np.log(5.5 if k!=1 else 3.3)
 sub['rot_0']=1
path=base/'Flyover-height-derived-gaussian-preview.ply'
header='ply\nformat binary_little_endian 1.0\ncomment Derived from 16bit PNG heightmaps - NOT decoded native Apple gaussian splats\n'
header+=f'element vertex {len(arr)}\n'
header+=''.join('property float '+n+'\n' for n in arr.dtype.names)
header+='end_header\n'
with path.open('wb') as f:
 f.write(header.encode());f.write(arr.tobytes())
print('saved',path,'bytes',path.stat().st_size,'splats',len(arr))
