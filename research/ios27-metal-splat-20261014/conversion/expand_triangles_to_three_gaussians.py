#!/usr/bin/env python3
"""3-Gaussian Apple triangle approximation, center-transmittance matched.
Input from existing isolated, native-decoded Tokyo corrected triangle buffers.
Gaussian approximation and c,p experimental, not an independently decoded R3D file.
"""
from pathlib import Path
import argparse,re,json,math
import numpy as np
p=argparse.ArgumentParser();p.add_argument('ply',type=Path);p.add_argument('triangle_positions',type=Path);p.add_argument('output',type=Path);p.add_argument('--offset',type=float,default=.25);p.add_argument('--sigma-factor',type=float,default=.75);p.add_argument('--concentration',type=float,default=1.0);a=p.parse_args()
if not 0<a.sigma_factor<=3 or not 0<=a.offset<=1 or a.concentration<=0:raise ValueError('invalid Gaussian mixture parameters')
with a.ply.open('rb') as f:
 header=b''
 while not header.endswith(b'end_header\n'):
  chunk=f.readline()
  if not chunk:raise ValueError('bad PLY')
  header+=chunk
count=int(re.search(rb'element vertex (\d+)',header).group(1));fields=re.findall(rb'property float ([^\n]+)',header)
if len(fields)!=17:raise ValueError('expected SH0 17 fields')
if a.ply.stat().st_size!=len(header)+count*17*4:raise ValueError('bad source length')
g=np.memmap(a.ply,mode='r',dtype='<f4',offset=len(header)).reshape(count,17)
v=np.memmap(a.triangle_positions,mode='r',dtype='<f4').reshape(count,3,3)
# The normalized triangle barycentric-power kernel has vertex Mahalanobis squared 2*(3c+4),
# giving Gaussian drop at original triangle centroid g=exp(-(3c+4)*(offset/sigma)^2).
attenuation=math.exp(-(3*a.concentration+4)*(a.offset/a.sigma_factor)**2)
if attenuation<.1:raise ValueError('mixture components too far from center')
out_header=b'ply\nformat binary_little_endian 1.0\ncomment THREE Gaussians per REAL native-decoded Apple triangle; lossy approximate; opacity constants assumed\nelement vertex '+str(count*3).encode()+b'\n'+b''.join(b'property float '+field+b'\n' for field in fields)+b'end_header\n'
a.output.parent.mkdir(parents=True,exist_ok=True);clipped=0
with a.output.open('wb') as f:
 f.write(out_header)
 for start in range(0,count,16384):
  end=min(count,start+16384);m=end-start
  ga=np.asarray(g[start:end],dtype=np.float64);tri=np.asarray(v[start:end],dtype=np.float64)
  part=np.repeat(ga,3,axis=0).reshape(m,3,17)
  centers=ga[:,None,0:3]+a.offset*(tri-ga[:,None,0:3]);part[:,:,0:3]=centers
  part[:,:,10:13]=part[:,:,10:13]+math.log(a.sigma_factor)
  opacity=1/(1+np.exp(-ga[:,9]))
  sub=(1-np.cbrt(1-opacity))/attenuation
  clipped+=int((sub>=.99).sum());sub=np.clip(sub,1e-7,.99)
  part[:,:,9]=np.log(sub/(1-sub))[:,None]
  if not np.isfinite(part).all():raise ValueError('nonfinite PLY record')
  f.write(part.astype('<f4').tobytes())
stat={'gaussians':count*3,'input_native_splats':count,'source':str(a.ply),'out':str(a.output),'size':a.output.stat().st_size,'mean_abs_center_match_error_theory':0,'mix_center_offset':a.offset,'sigma_scale':a.sigma_factor,'center_attenuation':attenuation,'clipped_sub_opacity_count':clipped,'method':'approximate three isotropic-weight Gaussians with original native triangular local geometry and SH0 color; transformed Gaussian center+covariance and alpha center matched with front-to-back transmittance; theoretical view/overlap not verified','provenance':'Native-decoded goldens, not native-free'}
a.output.with_suffix('.json').write_text(json.dumps(stat,indent=2)+'\n')
print(json.dumps(stat,indent=2))
