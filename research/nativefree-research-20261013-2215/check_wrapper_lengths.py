from pathlib import Path
from collections import Counter
import sys,struct
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huffman_header import detect_huff_headers
from nativefree_trico_size import read_size
c=Counter();ex=[]
for root in ['/opt/flyover-viewer/native-r3d','/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20']:
 for f in Path(root).rglob('*.r3d'):
  b=f.read_bytes();s=dissect(b)['splatStream']
  for fr in s['blocks']:
   by=fr['byet'];st=s['offset']+by['compressedPayloadRelativeOffset'];q=b[st:st+by['compressedPayloadBytes']]
   for d in split_j(q,12 if fr['index']==0 else 32)['descriptors']:
    if not d['compressedBytes']:continue
    src=q[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
    marks=detect_huff_headers(src)
    if not marks or marks[0]['family']!='0x24':continue
    off=marks[0]['relativeOffset'];h=src[off:]
    if len(h)<20:continue
    word,part1,part2=struct.unpack_from('<IIQ',h)
    v1,p=read_size(src,0,off);v2,p=read_size(src,p,off)
    if p!=off:continue
    inner=struct.unpack_from('<I',h,16)[0]
    c[(hex(inner), 'match',v2==part1+part2+16)]+=1
    if len(ex)<12:ex.append((f.name,fr['index'],d['lane'],v1,v2,part1,part2,hex(inner)))
print('counts',c)
print('examples',ex)
