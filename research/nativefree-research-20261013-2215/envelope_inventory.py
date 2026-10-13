#!/usr/bin/env python3
import sys,struct,json
from pathlib import Path
from collections import Counter,defaultdict
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huffman_header import detect_huff_headers
roots=[Path('/opt/flyover-viewer/native-r3d'),Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20')]
samples=defaultdict(list)
stats=Counter()
unmatched=[]
for region,root in zip(('tokyo','oahu'),roots):
    files=sorted(root.rglob('*.r3d'))
    print('REGION',region,'files',len(files))
    for f in files:
        data=f.read_bytes()
        splat=dissect(data)['splatStream']
        for frame in splat['blocks']:
            spec=frame['byet']
            start=splat['offset']+spec['compressedPayloadRelativeOffset']
            raw=data[start:start+spec['compressedPayloadBytes']]
            for d in split_j(raw,12 if frame['index']==0 else 32)['descriptors']:
                if not d['compressedBytes']:continue
                lane=raw[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
                marks=detect_huff_headers(lane)
                if not marks:
                    stats[(region,d['kind'],'no_mark')]+=1
                    if len(unmatched)<20:unmatched.append((region,f.name,frame['index'],d['lane'],d['kind'],lane[:40].hex()))
                    continue
                m=marks[0]
                off=m['relativeOffset']
                family=m['family']
                stats[(region,d['kind'],family,off)]+=1
                item={'tile':f.name,'block':frame['index'],'lane':d['lane'],'kind':d['kind'],'laneBytes':len(lane),'prefix':lane[:off].hex(),'header24':lane[off:off+24].hex()}
                if family=='0x24' and len(lane)>=off+16:
                    word=struct.unpack_from('<I',lane,off)[0]
                    item['wrapperMode']=(word>>8)&255
                    item['word1']=struct.unpack_from('<I',lane,off+4)[0]
                    item['word2']=struct.unpack_from('<Q',lane,off+8)[0]
                    item['after16']=lane[off+16:off+28].hex()
                key=(region,d['kind'],family,off)
                if len(samples[key])<2:samples[key].append(item)
out={'stats':{str(k):v for k,v in stats.items()},'samples':{str(k):v for k,v in samples.items()},'unmatched':unmatched}
p=Path('/opt/flyover-viewer/nativefree-research-20261013-2215/envelopes.json')
p.write_text(json.dumps(out,indent=2))
print('STATS',len(stats),'samples',sum(map(len,samples.values())),'unmatched',len(unmatched),'wrote',p)
for k,v in stats.most_common(35):print(k,v)
for k,items in list(samples.items())[:18]:print('SAMPLE',k,items[0])
