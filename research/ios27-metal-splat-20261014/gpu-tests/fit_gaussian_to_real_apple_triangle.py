#!/usr/bin/env python3
"""Compare reference moment-matched Gaussian with Apple's real Metal barycentric-power alpha pixels.
No numpy/scipy; evaluative proof on 64x64, single projected native Tokyo triangle.
"""
import struct,math,json
from pathlib import Path
P=Path.home()/'ios27-maps-binary-lab/gpu-analysis'
input_pixels=(P/'real_triangle_corrected_gpu_alpha.raw').read_bytes()
rgba=struct.unpack('<'+str(len(input_pixels)//2)+'e',input_pixels)
obs=[rgba[i*4] for i in range(4096)]
xyq=[(2500,62500),(62500,27143),(29959,2500)]
# Metal viewport 64x64, y downward
v=[((qx/65535*1.8-.9+1)*32,(1-(qy/65535*1.8-.9))*32) for qx,qy in xyq]
mu=tuple(sum(pt[i] for pt in v)/3 for i in range(2)); e1=[v[1][i]-v[0][i] for i in range(2)];e2=[v[2][i]-v[0][i] for i in range(2)]
c=1.;amp=min(.99,20*(61/255)*(1/27)**c)
k=1/(9*(3*c+4));cov=[[k*(2*e1[i]*e1[j]-e1[i]*e2[j]-e2[i]*e1[j]+2*e2[i]*e2[j]) for j in range(2)] for i in range(2)]
det=cov[0][0]*cov[1][1]-cov[0][1]**2;inv=[[cov[1][1]/det,-cov[0][1]/det],[-cov[1][0]/det,cov[0][0]/det]]
pxs=[(j+.5,i+.5) for i in range(64) for j in range(64)]

def gauss(pt,centroid,scale):
 d0=pt[0]-centroid[0];d1=pt[1]-centroid[1]
 exponent=-.5*(inv[0][0]*d0*d0+(inv[0][1]+inv[1][0])*d0*d1+inv[1][1]*d1*d1)/scale**2
 return math.exp(exponent) if exponent>-200 else 0.

def kernel_mixture(pt,offset,scale):
 ctrs=[(mu[0]+offset*(q[0]-mu[0]),mu[1]+offset*(q[1]-mu[1])) for q in v]
 return sum(gauss(pt,q,scale) for q in ctrs)/3

def score(vals,amp_mode):
 if amp_mode=='matched': A=amp
 else:A=sum(a*b for a,b in zip(vals,obs))/max(1e-12,sum(a*a for a in vals))
 errs=[A*q-x for q,x in zip(vals,obs)]
 return {'amp':A,'rmse':math.sqrt(sum(e*e for e in errs)/len(errs)),'mae':sum(abs(e) for e in errs)/len(errs),'rmse_inside':math.sqrt(sum(e*e for i,e in enumerate(errs) if obs[i]>0)/max(1,sum(y>0 for y in obs))),'max_error':max(map(abs,errs))}

def compute(offset,scale,amp_mode='least_squares'):
 vals=[kernel_mixture(pt,offset,scale) for pt in pxs]
 return score(vals,amp_mode)
fixed=compute(0,1,'matched');best_single=(None,{'rmse':float('inf')}); best_mix=(None,{'rmse':float('inf')})
for j in range(12,35):
 s=j/20
 for offi in range(0,11):
  off=offi/20
  r=compute(off,s)
  if offi==0 and r['rmse']<best_single[1]['rmse']:best_single=((off,s),r)
  if r['rmse']<best_mix[1]['rmse']:best_mix=((off,s),r)
results={'input':'actual iOS native-decoded Tokyo triangle 30, projected to 64x64, rendered with Apple macOS Metal vertex + custom analytic fragment','target_pixel_count':len(obs),'rendered_pixel_count':sum(a>0 for a in obs),'source_rgba':[239,239,239,61],'assumed_test_alpha_concentration':c,'assumed_test_alpha_pre_factor':20,'triangle_viewport_px':v,'moment_covariance_px':cov,'moment_matched_fixed_peak':fixed,'best_single_gaussian_optimized_sigma_amp':{'params':best_single[0],**best_single[1]},'best_three_gaussian_mixture_optimized':{'params':best_mix[0],**best_mix[1]},'limits':'Raster-space 64x64 single triangle approximation, 3-Gaussian mixture equal strength with 3 centers, no native Apple frame or multi-primitive overlap and no PBR.'}
print(json.dumps(results,indent=2));(P/'gaussian_fit_to_native_triangle_pixels.json').write_text(json.dumps(results,indent=2)+'\n')
