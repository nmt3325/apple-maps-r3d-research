#!/usr/bin/env python3
"""Experimental LOSSY Apple triangle-Splat -> Graphdeco 3DGS PLY adapter.

Input: decoded GPU vertex triangles, per-splat RGBA and *per-tile* uniforms.
Does NOT parse R3D/BYET itself, execute proprietary code, or reproduce PBR.
Python standard library only; synthetic fixture intended for geometric proof.
"""
import argparse, json, math, struct
from pathlib import Path
SH_C0=0.28209479177387814

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):
 d=math.sqrt(dot(a,a));
 if d<1.e-12: raise ValueError('degenerate triangle')
 return tuple(x/d for x in a)
def addscale(a,b,s):return tuple(x+s*y for x,y in zip(a,b))
def quat_cols(x,y,z):
 # columns of a right-handed rotation matrix; Graphdeco uses (w,x,y,z)
 m=[[x[0],y[0],z[0]],[x[1],y[1],z[1]],[x[2],y[2],z[2]]]
 tr=m[0][0]+m[1][1]+m[2][2]
 if tr>0:
  t=math.sqrt(tr+1)*2; q=((t/4),(m[2][1]-m[1][2])/t,(m[0][2]-m[2][0])/t,(m[1][0]-m[0][1])/t)
 else:
  j=max(range(3),key=lambda k:m[k][k]); k=(j+1)%3;l=(j+2)%3
  t=math.sqrt(max(1e-12,1+m[j][j]-m[k][k]-m[l][l]))*2
  q=[0.,0.,0.,0.];q[j+1]=t/4;q[0]=(m[l][k]-m[k][l])/t;q[k+1]=(m[k][j]+m[j][k])/t;q[l+1]=(m[l][j]+m[j][l])/t
 return tuple(round(x,12) for x in norm(q))

def gaussian_from_triangle(triangle,c,thickness_ratio=.08):
 """Dirichlet kernel alpha~(b0*b1*b2)^c -> moment-matched 2D Gaussian."""
 v0,v1,v2=[tuple(map(float,v)) for v in triangle]
 e1,e2=sub(v1,v0),sub(v2,v0)
 x=norm(e1);z=norm(cross(e1,e2)); y=norm(cross(z,x))
 a=dot(e1,x);b=dot(e2,x);d=dot(e2,y)
 # exact normalized kernel moment covariance for Dirichlet(c+1,c+1,c+1)
 den=9*(3*c+4)
 xx=(2*a*a-2*a*b+2*b*b)/den
 xy=(2*b-a)*d/den;yy=2*d*d/den
 delta=math.hypot(xx-yy,2*xy); lam0=(xx+yy+delta)/2;lam1=(xx+yy-delta)/2
 if lam1<=0: raise ValueError('invalid eigenvalue')
 if abs(xy)>1e-15: u=norm((lam0-yy,xy))
 elif xx>=yy:u=(1.,0.)
 else:u=(0.,1.)
 major=norm(addscale(tuple(a0*u[0] for a0 in x),y,u[1]));minor=norm(addscale(tuple(-a0*u[1] for a0 in x),y,u[0]))
 q=quat_cols(major,minor,z)
 xyz=tuple(sum(v[i] for v in (v0,v1,v2))/3 for i in range(3))
 scales=(math.sqrt(lam0),math.sqrt(lam1),math.sqrt(lam1)*thickness_ratio)
 return xyz,scales,q,z

def convert(inp,out):
 specs=json.loads(Path(inp).read_text());c=float(specs['alpha_concentration']);pref=float(specs['alpha_pre_factor']);th=float(specs.get('thickness_ratio',.08))
 if c<=0 or pref<=0 or th<=0:raise ValueError('c, prefactor and thickness_ratio must be positive')
 splats=specs['splats']; props=['x','y','z','nx','ny','nz','f_dc_0','f_dc_1','f_dc_2','opacity','scale_0','scale_1','scale_2','rot_0','rot_1','rot_2','rot_3']
 header='ply\nformat binary_little_endian 1.0\ncomment EXPERIMENTAL LOSSY Apple triangle Splat approximate moment Gaussian; not original 3DGS\nelement vertex %s\n'%len(splats)+''.join('property float '+p+'\n' for p in props)+'end_header\n'
 with open(out,'wb') as f:
  f.write(header.encode())
  for item in splats:
   xyz,ss,q,n=gaussian_from_triangle(item['triangle'],c,th)
   col=int(str(item['albedo_srgb_hex']),0)
   rgba=[(col>>shift)&255 for shift in (24,16,8,0)]
   rgb=[v/255 for v in rgba[:3]] # viewer-dependent sRGB/linear color correction NOT applied
   opacity=min(.99,pref*(rgba[3]/255)*(1/27)**c)
   opacity=max(1e-6,opacity)
   record=[*xyz,*n,*[(v-.5)/SH_C0 for v in rgb],math.log(opacity/(1-opacity)),*[math.log(v) for v in ss],*q]
   f.write(struct.pack('<17f',*record))
 return len(splats)

def compare_kernel(c,n=120):
 sq=ab=0;num=0
 for i in range(n+1):
  for j in range(n+1-i):
   b1=i/n;b2=j/n;b0=1-b1-b2
   apple=max(0,27*b0*b1*b2)**c
   d1=b1-1/3; d2=b2-1/3
   # inverse of exact moment covariance in barycentric b1,b2
   gaussian=math.exp(-.5*3*(3*c+4)*(2*d1*d1+2*d2*d2+2*d1*d2))
   sq+=(apple-gaussian)**2;ab+=abs(apple-gaussian);num+=1
 return {'c':c,'rms_error_relative_peak':math.sqrt(sq/num),'mean_abs_error_relative_peak':ab/num,'gaussian_at_edge_midpoint':math.exp(-.5*3*(3*c+4)*(2*(1/6)**2+2*(1/6)**2+2*(1/6)**2))}

def main():
 p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output');p.add_argument('--validate',action='store_true');a=p.parse_args()
 if a.validate:
  for c in (.5,1.,2.,4.):print(json.dumps(compare_kernel(c)))
 if a.input:
  if not a.output:p.error('--output is required with --input')
  print('converted',convert(a.input,a.output),'triangle splats to an approximate standard 3DGS PLY')
if __name__=='__main__':main()
