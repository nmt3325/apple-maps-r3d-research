import sys
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from pathlib import Path
from collections import Counter
c=Counter()
for f in Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'):
 b=f.read_bytes();s=dissect(b)['splatStream']
 for fr in s['blocks']:
  by=fr['byet'];st=s['offset']+by['compressedPayloadRelativeOffset'];q=b[st:st+by['compressedPayloadBytes']]
  for d in split_j(q,12 if fr['index']==0 else 32)['descriptors']:
   if d['kind']==0:c[(fr['index'],d['compressedBytes']-s['pointCount'])]+=1
print(c.most_common(20))
