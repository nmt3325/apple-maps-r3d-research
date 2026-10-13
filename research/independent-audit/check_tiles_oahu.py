from pathlib import Path
import re
from c3mm_v2_parser import parse
B=Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013')
meta=B/'fresh_signed/oahu_hilton_20261013/s100_z13_x504_y3600.c3mm'
data,cells=parse(meta.read_bytes(),True)
files=list((B/'fresh_signed/oahu_hilton_20261013/area_z20').glob('*.r3d'))
ok=bad=0
for f in files:
 m=re.search('z20_x([0-9]+)_y([0-9]+)_h([0-9]+)',f.name)
 if not m:continue
 x,y,h=map(int,m.groups())
 if x//128!=504 or y//128!=3600:continue
 point=((x//8)%16,15-(y//8)%16,h)
 if point in cells:ok+=1
 else:bad+=1;print('not-indexed',f.name,point)
print('verified',ok,'not-indexed',bad,'index-cells',len(cells))
