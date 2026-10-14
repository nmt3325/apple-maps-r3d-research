from pathlib import Path
import math,struct,json
p=Path.home()/'ios27-maps-binary-lab/gpu-analysis'
b=(p/'real_triangle_corrected_gpu_alpha.raw').read_bytes();xs=struct.unpack('<'+str(len(b)//2)+'e',b)
xyq=[(2500,62500),(62500,27143),(29959,2500)]
v=[((qx/65535*1.8-.9+1)*32,(1-(qy/65535*1.8-.9))*32) for qx,qy in xyq]
(x0,y0),(x1,y1),(x2,y2)=v;det=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
ampfactor=20*(61/255)
diff=[];mask=0;inside_pred=0;leak=0
for py in range(64):
 for px in range(64):
  x=px+.5;y=py+.5
  b0=((y1-y2)*(x-x2)+(x2-x1)*(y-y2))/det
  b1=((y2-y0)*(x-x2)+(x0-x2)*(y-y2))/det;b2=1-b0-b1
  # Top-left raster-edge definition approximate; exclude boundary near 1e-3 due sample-rule differences
  inside=min(b0,b1,b2)>=0
  pred=min(.99,ampfactor*b0*b1*b2) if inside else 0
  actual=xs[(py*64+px)*4]
  diff.append(pred-actual)
  if actual>0:mask+=1
  if pred>0:inside_pred+=1
  if actual==0 and pred>0:leak+=1
out={'predicted_pixels':inside_pred,'actual_pixels':mask,'pixel_set_symmetric_difference':leak+sum(pred==0 and xs[i*4]>0 for i,pred in enumerate([0]*0)),'rmse':math.sqrt(sum(x*x for x in diff)/len(diff)),'mae':sum(abs(x) for x in diff)/len(diff),'max_abs':max(map(abs,diff)),'source':'Metal native Splat vertex vs software triangle kernel c=1,p=20, prequantized geometry, 64x64' }
print(json.dumps(out,indent=2));(p/'ANALYTIC_BARYCENTRIC_PIXEL_PARITY.json').write_text(json.dumps(out,indent=2)+'\n')
