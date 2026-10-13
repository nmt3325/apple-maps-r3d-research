from pathlib import Path
from collections import Counter,defaultdict
import sys
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
samples=defaultdict(list)
counts=Counter()
for f in sorted(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'))[:6]:
    data=f.read_bytes()
    soup=dissect(data)['splatStream']
    for frame in soup['blocks']:
        spec=frame['byet']
        p=soup['offset']+spec['compressedPayloadRelativeOffset']
        payload=data[p:p+spec['compressedPayloadBytes']]
        for d in split_j(payload,12 if frame['index']==0 else 32)['descriptors']:
            src=payload[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
            key=(frame['index'],d['kind'])
            counts[key]+=1
            if len(samples[key])<4 and src:
                samples[key].append((d['lane'],len(src),src[:96].hex()))
print('COUNTS',counts)
for key,items in sorted(samples.items()):
    print(key,items)
