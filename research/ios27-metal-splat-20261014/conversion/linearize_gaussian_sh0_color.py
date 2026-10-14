#!/usr/bin/env python3
"""Convert R3D native material sRGB colors to linear RGB Graphdeco SH0 PLY coefficients.
Preserves native-decoded Apple geometry/approximate Gaussian shape/opacity unchanged.
This is optional: renderer may apply sRGB transfer separately. Validate on target.
"""
import argparse,re,json
from pathlib import Path
import numpy as np
C0=0.28209479177387814
p=argparse.ArgumentParser();p.add_argument('src',type=Path);p.add_argument('dst',type=Path);a=p.parse_args()
with a.src.open('rb') as f:
 header=b''
 while not header.endswith(b'end_header\n'):
  b=f.readline()
  if not b:raise ValueError('invalid PLY')
  header+=b
 count=int(re.search(rb'element vertex (\d+)',header)[1]);fields=re.findall(rb'property float ([^\n]+)',header)
 if len(fields)!=17:raise ValueError('only 17-channel SH0 Gaussian source supported')
 if a.src.stat().st_size!=len(header)+count*68:raise ValueError('truncated PLY')
 out_header=header.replace(b'end_header\n',b'comment Color corrected with sRGB EOTF to linear Graphdeco SH0 for Metal parity; viewer color interpretation may vary\nend_header\n')
 with a.dst.open('wb') as out:
  out.write(out_header);last_min=1.;last_max=0.;chunk_count=0
  for i in range(0,count,16384):
   n=min(16384,count-i);rows=np.frombuffer(f.read(n*68),dtype='<f4').reshape(n,17).copy()
   srgb=np.clip(rows[:,6:9].astype('float64')*C0+.5,0,1)
   linear=np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4)
   last_min=min(last_min,float(linear.min()));last_max=max(last_max,float(linear.max()));rows[:,6:9]=(linear-.5)/C0
   if not np.isfinite(rows).all():raise ValueError('nonfinite converted PLY')
   out.write(rows.astype('<f4').tobytes());chunk_count+=1
result={'input':str(a.src),'output':str(a.dst),'point_count':count,'chunks':chunk_count,'output_size':a.dst.stat().st_size,'output_linear_range':[last_min,last_max],'notes':'SH0 color converted based on actual iOS/Mac Metal 4-pass GPU parity test; remaining geometry/opacity approximate and constants assumed, do not double-apply sRGB gamma in viewer.'}
a.dst.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
