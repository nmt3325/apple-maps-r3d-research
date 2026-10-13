#!/usr/bin/env python3
from pathlib import Path
import concurrent.futures,subprocess,time
src=Path('/opt/flyover-viewer/decoded-native/c3m-all-223')
out=Path('/opt/flyover-viewer/www/c3m-textures')
out.mkdir(parents=True,exist_ok=True)
files=sorted(src.glob('*.texture-0-0.heic'))
def convert(f):
 target=out/(f.name.removesuffix('.r3d.texture-0-0.heic')+'.jpg')
 if target.exists() and target.stat().st_size>100:return (f.name,target.stat().st_size,None)
 r=subprocess.run(['/usr/local/bin/ffmpeg','-hide_banner','-loglevel','error','-threads','1','-y','-i',str(f),'-frames:v','1','-q:v','3',str(target)],capture_output=True,text=True,timeout=40)
 if r.returncode!=0 or not target.exists():return (f.name,0,r.stderr[-250:])
 return (f.name,target.stat().st_size,None)
start=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 res=list(pool.map(convert,files))
errors=[x for x in res if x[2]]
print('textures',len(files),'converted',len(res)-len(errors),'errors',errors[:7])
print('bytes',sum(x[1] for x in res),'seconds',round(time.time()-start,1))
