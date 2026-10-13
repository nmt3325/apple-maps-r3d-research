from pathlib import Path
from collections import Counter
import sys
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huffman_header import detect_huff_headers
from nativefree_trico_size import read_size
c=Counter();samples={}
for f in Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'):
 b=f.read_bytes();s=dissect(b)['splatStream'];points=s['pointCount']
 for fr in s['blocks']:
  by=fr['byet'];st=s['offset']+by['compressedPayloadRelativeOffset'];q=b[st:st+by['compressedPayloadBytes']]
  for d in split_j(q,12 if fr['index']==0 else 32)['descriptors']:
   if not d['compressedBytes']:continue
   src=q[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
   marks=detect_huff_headers(src)
   if not marks:continue
   off=marks[0]['relativeOffset'];p=0;values=[]
   try:
    while p<off:
     v,p=read_size(src,p,off)
     values.append(v)
    if p!=off:raise ValueError('bad prefix')
    c[('parsed',d['kind'],len(values))]+=1
    if values:
     for multiple in (1,2,3,4):
      if values[0]==points*multiple:c[('first_exact',d['kind'],multiple)]+=1
     key=(d['kind'],fr['index'])
     if key not in samples:samples[key]=(f.name,points,off,src[:off].hex(),values,src[off:off+4].hex())
   except Exception:
    c[('prefix_error',d['kind'])]+=1
print('COUNTS',c)
print('SAMPLES',samples)
