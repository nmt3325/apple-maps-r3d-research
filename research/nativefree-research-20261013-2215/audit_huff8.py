#!/usr/bin/env python3
"""Audit Huff8 mode0 -> Huff816 literal stage across captured Tokyo and Oahu lanes."""
import sys,json,struct
from pathlib import Path
from collections import Counter
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huffman_header import detect_huff_headers
from huff8_mode0_literal import peel_huff8,UnsupportedHuff8
roots={'tokyo':Path('/opt/flyover-viewer/native-r3d'),'oahu':Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20')}
counts=Counter();examples=[];bad=[];lengths=[]
for region,root in roots.items():
    for f in sorted(root.rglob('*.r3d')):
        b=f.read_bytes()
        s=dissect(b)['splatStream']
        for frame in s['blocks']:
            by=frame['byet']
            st=s['offset']+by['compressedPayloadRelativeOffset']
            payload=b[st:st+by['compressedPayloadBytes']]
            lanes=split_j(payload,12 if frame['index']==0 else 32)['descriptors']
            for d in lanes:
                if not d['compressedBytes']:continue
                src=payload[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
                marks=detect_huff_headers(src)
                if not marks:
                    counts[(region,'no_header',d['kind'])]+=1
                    continue
                off=marks[0]['relativeOffset']
                enc=src[off:]
                family=marks[0]['family']
                if family=='0x24':
                    if len(enc)<20:
                        bad.append((f.name,d['lane'],'short_24'));continue
                    h,meta1,meta2=struct.unpack_from('<IIQ',enc)
                    counts[(region,'24_mode',h>>8&255)]+=1
                    inner=struct.unpack_from('<I',enc,16)[0]
                    counts[(region,'24_inner',hex(inner))]+=1
                else:
                    inner=struct.unpack_from('<I',enc)[0]
                    counts[(region,'61_direct',hex(inner))]+=1
                try:
                    decoded=peel_huff8(enc)
                    counts[(region,'literal_decoded',frame['index'],d['kind'])]+=1
                    counts[(region,'literal_bytes')]+=len(decoded)
                    lengths.append((len(decoded),s['pointCount'],frame['index'],d['kind']))
                    if len(examples)<10:
                        examples.append({'tile':f.name,'region':region,'block':frame['index'],'lane':d['lane'],'kind':d['kind'],'offset':off,'encodedBytes':len(enc),'decodedBytes':len(decoded),'first16':decoded[:16].hex(),'pointCount':s['pointCount']})
                    # Strict rejection: caller's incorrect expected length must not pass.
                    try:peel_huff8(enc,len(decoded)+1)
                    except ValueError:pass
                    else:bad.append((f.name,d['lane'],'bad_length_accepted'))
                except UnsupportedHuff8:
                    counts[(region,'compressed_pending',frame['index'],d['kind'])]+=1
                except ValueError as e:
                    bad.append((f.name,d['lane'],str(e)))
report={'counts':{str(k):v for k,v in counts.items()},'samples':examples,'failures':bad[:30],
        'genuineLiteralLanes':sum(v for k,v in counts.items() if k[1]=='literal_decoded'),
        'note':'Huff-stage literal bytes only, not BYET predictors or XYZ floats.'}
dest=Path('/opt/flyover-viewer/nativefree-research-20261013-2215/huff8_audit.json')
dest.write_text(json.dumps(report,indent=2))
for k,v in counts.most_common(40):print(k,v)
print('Genuine literal lanes',report['genuineLiteralLanes'],'failures',len(bad),'report',dest)
print('Examples',examples[:4])
if bad:sys.exit(1)
