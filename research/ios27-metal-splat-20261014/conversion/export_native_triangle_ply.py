#!/usr/bin/env python3
"""LOSSY approximation: real *native-decoded* Apple triangles -> Gaussian Splat PLY.
The R3D independent source decoder is NOT implemented by this utility.
The alpha constants are only assumed and MUST be replaced after runtime verification.
"""
import argparse, math, json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
C0=0.28209479177387814
PROPS='x y z nx ny nz f_dc_0 f_dc_1 f_dc_2 opacity scale_0 scale_1 scale_2 rot_0 rot_1 rot_2 rot_3'.split()
def main():
 p=argparse.ArgumentParser();p.add_argument('--positions',required=True);p.add_argument('--rgba',required=True);p.add_argument('--output',required=True);p.add_argument('--alpha-concentration',type=float,required=True);p.add_argument('--alpha-pre-factor',type=float,required=True);p.add_argument('--thickness-ratio',type=float,default=.08);a=p.parse_args()
 if a.alpha_concentration<=0 or a.alpha_pre_factor<=0 or a.thickness_ratio<=0:raise ValueError('all parameters must be positive')
 xyz=np.memmap(a.positions,dtype='<f4',mode='r'); rgba=np.memmap(a.rgba,dtype=np.uint8,mode='r')
 if xyz.size%9 or rgba.size%4 or xyz.size//9!=rgba.size//4:raise ValueError('buffer lengths mismatch')
 n=rgba.size//4; xyz=xyz.reshape(n,3,3);rgba=rgba.reshape(n,4)
 valid=0;written=0;stats=[];out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
 # output PLY header count patched after counting valid triangles
 with open(out,'wb') as f:
  countpos=f.tell();f.write(('ply\nformat binary_little_endian 1.0\ncomment Native-decoded Apple geometry; lossy triangular kernel Gaussian approximation; unverified alpha parameters\nelement vertex %012d\n'%0).encode()); f.write(''.join('property float '+x+'\n' for x in PROPS).encode());f.write(b'end_header\n')
  for start in range(0,n,40000):
   v=np.asarray(xyz[start:start+40000],dtype=np.float64)
   rgb=np.asarray(rgba[start:start+40000],dtype=np.float64)/255
   e1=v[:,1]-v[:,0];e2=v[:,2]-v[:,0];l1=np.linalg.norm(e1,axis=1);normal=np.cross(e1,e2);ln=np.linalg.norm(normal,axis=1)
   mask=(l1>1e-10)&(ln>1e-10)&np.isfinite(v).all(axis=(1,2))&(rgb[:,3]>0)
   v=v[mask];e1=e1[mask];e2=e2[mask];l1=l1[mask];normal=normal[mask]/ln[mask,None];color=rgb[mask];x=e1/l1[mask,None];y=np.cross(normal,x)
   aa=l1[mask];bb=np.einsum('ij,ij->i',e2,x);dd=np.einsum('ij,ij->i',e2,y)
   den=9*(3*a.alpha_concentration+4)
   xx=(2*aa*aa-2*aa*bb+2*bb*bb)/den;xy=(2*bb-aa)*dd/den;yy=2*dd*dd/den
   delta=np.hypot(xx-yy,2*xy);lam0=np.maximum((xx+yy+delta)*.5,1e-10);lam1=np.maximum((xx+yy-delta)*.5,1e-10)
   angle=.5*np.arctan2(2*xy,xx-yy);ct=np.cos(angle)[:,None];st=np.sin(angle)[:,None];major=x*ct+y*st;minor=-x*st+y*ct
   # Projection to SO(3) by construction; scipy quaternion xyzw -> Graphdeco wxyz
   mat=np.stack([major,minor,normal],axis=-1);q=Rotation.from_matrix(mat).as_quat()
   val=np.zeros((len(v),17),dtype='<f4');val[:,0:3]=v.mean(axis=1);val[:,3:6]=normal;val[:,6:9]=(color[:,:3]-.5)/C0
   alpha=np.minimum(.99,a.alpha_pre_factor*color[:,3]*((1/27)**a.alpha_concentration));alpha=np.clip(alpha,1e-6,.99);val[:,9]=np.log(alpha/(1-alpha))
   scales=np.stack([np.sqrt(lam0),np.sqrt(lam1),np.sqrt(lam1)*a.thickness_ratio],axis=1);val[:,10:13]=np.log(scales);val[:,13:17]=q[:,[3,0,1,2]]
   if not np.isfinite(val).all():raise ValueError('nonfinite Gaussian parameters')
   f.write(val.tobytes());written+=len(v);stats.append(float(np.mean(scales[:,0])))
  f.seek(countpos);f.write(('ply\nformat binary_little_endian 1.0\ncomment Native-decoded Apple geometry; lossy triangular kernel Gaussian approximation; unverified alpha parameters\nelement vertex %012d\n'%written).encode())
 outstat={'source':'Apple native-decoded saved golden buffers (not independently decoded)', 'input_count':n,'output_count':written,'input_positions':a.positions,'input_rgba':a.rgba,'output_ply':str(out),'output_size_bytes':out.stat().st_size,'alpha_concentration_hypothetical':a.alpha_concentration,'alpha_pre_factor_hypothetical':a.alpha_pre_factor,'thickness_ratio_hypothetical':a.thickness_ratio,'mean_chunk_major_sigma':stats,'limitations':'Triangle-supported kernel approximated by unbounded Gaussian, color PBR/transfer and SH, clipping and georeference not reproduced; alpha globals assumed, no iOS runtime comparison.'}
 out.with_suffix('.json').write_text(json.dumps(outstat,indent=2))
 print(json.dumps({k:v for k,v in outstat.items() if k!='mean_chunk_major_sigma'},indent=2))
if __name__=='__main__':main()
