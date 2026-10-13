from pathlib import Path
import sys,struct,json
from collections import Counter
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huffman_header import detect_huff_headers
from huff816_table_probe import table,HuffError
counts=Counter();samples=[];errors=[]
for f in Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'):
 b=f.read_bytes();s=dissect(b)['splatStream']
 for fr in s['blocks']:
  by=fr['byet'];st=s['offset']+by['compressedPayloadRelativeOffset']
  q=b[st:st+by['compressedPayloadBytes']]
  for d in split_j(q,12 if fr['index']==0 else 32)['descriptors']:
   if not d['compressedBytes']:continue
   src=q[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
   marks=detect_huff_headers(src)
   if not marks:continue
   off=marks[0]['relativeOffset']
   h=src[off:]
   if marks[0]['family']=='0x24' and len(h)>16:h=h[16:]
   if len(h)<4 or struct.unpack_from('<I',h)[0]!=0x61000002:continue
   try:
    v=table(h)
    counts['parsed']+=1
    for name in ('symbolValid','uniqueSymbols','uniqueCodes'):
     counts[(name,v[name])]+=1
    counts[('kraft_le_1',v['kraft']<=1.00001)]+=1
    counts[('codeWidth',v['codeWidth'])]+=1
    if len(samples)<8:samples.append((f.name,fr['index'],d['lane'],v))
   except Exception as e:
    counts['error']+=1
    if len(errors)<8:errors.append((f.name,fr['index'],d['lane'],str(e)))
print('COUNTS',counts)
print('SAMPLES',samples[:2])
print('ERRORS',errors)
Path('/opt/flyover-viewer/nativefree-research-20261013-2215/huff816_table_audit.json').write_text(json.dumps({'counts':{str(k):v for k,v in counts.items()},'samples':samples,'errors':errors},indent=2))
