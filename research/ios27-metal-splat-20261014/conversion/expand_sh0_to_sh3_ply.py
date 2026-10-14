#!/usr/bin/env python3
"""Expand Graphdeco binary PLY SH0 data to all 45 degree-3 coefficients set to zero.
Order: XYZ normals dc0..2 rest0..44 opacity scale0..2 rot0..3.
Standalone operation on our isolated approximate splat PLY, no data extraction.
"""
import argparse,struct,re,json
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
with a.input.open('rb') as f:
 header=b''
 while not header.endswith(b'end_header\n'):
  b=f.readline()
  if not b or len(header)>40000:raise ValueError('invalid PLY header')
  header+=b
 assert b'format binary_little_endian 1.0' in header
 n=int(re.search(rb'element vertex\s+(\d+)',header).group(1))
 props=re.findall(rb'property float ([^\n]+)',header)
 expected=['x','y','z','nx','ny','nz','f_dc_0','f_dc_1','f_dc_2','opacity','scale_0','scale_1','scale_2','rot_0','rot_1','rot_2','rot_3']
 if [x.decode() for x in props]!=expected:raise ValueError('unexpected source PLY schema')
 if a.input.stat().st_size!=len(header)+n*68:raise ValueError('input data size not complete')
 with a.output.open('wb') as out:
  header_out=(b'ply\nformat binary_little_endian 1.0\ncomment SH3 coefficients zero; LOSSY Apple triangle-to-Gaussian with unverified opacity constants\nelement vertex '+str(n).encode()+b'\n')
  for fld in expected[:9]+[f'f_rest_{i}' for i in range(45)]+expected[9:]:
   header_out+=f'property float {fld}\n'.encode()
  header_out+=b'end_header\n';out.write(header_out)
  for start in range(0,n,16384):
   c=min(16384,n-start)
   rows=np.frombuffer(f.read(c*68),dtype='<f4').reshape(c,17)
   expanded=np.zeros((c,62),dtype='<f4');expanded[:,:9]=rows[:,:9];expanded[:,54:]=rows[:,9:];out.write(expanded.tobytes())
 print(json.dumps(dict(input=str(a.input),output=str(a.output),vertices=n,degree=3,output_bytes=a.output.stat().st_size,per_vertex_floats=62,expected_bytes=len(header_out)+n*62*4),indent=2))
