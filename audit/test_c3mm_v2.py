import sys, os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"codec"))
from pathlib import Path
from c3mm_v2_parser import parse
BASE=Path(os.environ.get('R3D_FETCH_LAB_DIR','/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013'))
files=sorted(BASE.rglob('*.c3mm'))
for p in files:
 records=parse(p.read_bytes())
 print(p.name,'tags',[r['tag'] for r in records],'rawBytes',sum(r['uncompressed'] for r in records))
 assert all(x.get('count16Matches',True) for x in records)
print('PASS',len(files),'files',sum(len(parse(p.read_bytes())) for p in files),'sections')
