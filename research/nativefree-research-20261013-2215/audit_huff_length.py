from pathlib import Path
from collections import Counter
import sys,struct
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huffman_header import detect_huff_headers
from nativefree_trico_size import read_size
from huff816_decode_experimental import decode
c=Counter();examples=[]
for f in sorted(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d')):
 b=f.read_bytes();s=dissect(b)['splatStream']
 for fr in s['blocks']:
  by=fr['byet'];st=s['offset']+by['compressedPayloadRelativeOffset'];q=b[st:st+by['compressedPayloadBytes']]
  for d in split_j(q,12 if fr['index']==0 else 32)['descriptors']:
   if not d['compressedBytes']:continue
   src=q[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
   marks=detect_huff_headers(src)
   if not marks:continue
   off=marks[0]['relativeOffset']
   h=src[off:]
   if marks[0]['family']=='0x24' and len(h)>16:h=h[16:]
   if len(h)<4 or struct.unpack_from('<I',h)[0]!=0x61000002:continue
   first,p=read_size(src,0,off)
   second,p=read_size(src,p,off)
   if p!=off:continue
   for typ,n in [('first',first),('second',second)]:
    try:
     out,at,total,info=decode(h,n)
     c[(typ,'ok')]+=1
     c[(typ,'trailing_under32',0<=total-at<=31)]+=1
     if len(examples)<12:examples.append((f.name,fr['index'],d['lane'],typ,n,total-at,len(out),out[:10].hex()))
    except Exception as e:
     c[(typ,'error')]+=1
     if len(examples)<12:examples.append((f.name,fr['index'],d['lane'],typ,n,str(e)))
   if c[('first','ok')]+c[('first','error')]>=100:break
  if c[('first','ok')]+c[('first','error')]>=100:break
 if c[('first','ok')]+c[('first','error')]>=100:break
print(c)
print('SAMPLES',examples)
