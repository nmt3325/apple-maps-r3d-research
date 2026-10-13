import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"codec"))
from pathlib import Path
import re
from c3mm_v2_parser import parse
B=Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013')
meta=B/'exports/capture-validation-b/s100_z13_x7276_y3225_h0.c3mm'
data,cells=parse(meta.read_bytes(),True)
files=list(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'))
ok=bad=0
for f in files:
 m=re.search('z20_x([0-9]+)_y([0-9]+)_h([0-9]+)',f.name)
 if not m:continue
 x,y,h=map(int,m.groups())
 if x//128!=7276 or y//128!=3225:continue
 point=((x//8)%16,15-(y//8)%16,h)
 if point in cells:ok+=1
 else:bad+=1;print('not-indexed',f.name,point)
print('verified',ok,'not-indexed',bad,'index-cells',len(cells))
