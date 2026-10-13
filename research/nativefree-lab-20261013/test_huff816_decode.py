#!/usr/bin/env python3
"""Smoke-test independently decoded Huff816 symbols against exact point counts."""
from pathlib import Path
from collections import Counter
import sys,json,struct
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huff816 import decode_symbols,unwrap_24,Huff816Error
f=sorted(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'))[0]
b=f.read_bytes();s=dissect(b)['splatStream'];count=s['pointCount']
results=[]
for frame in s['blocks']:
    spec=frame['byet'];p=s['offset']+spec['compressedPayloadRelativeOffset']
    payload=b[p:p+spec['compressedPayloadBytes']]
    for d in split_j(payload,12 if frame['index']==0 else 32)['descriptors']:
        n=d['compressedBytes']
        if n<24:continue
        lane=payload[d['compressedOffset']:d['compressedOffset']+n]
        if lane[4:8]!=b'\x00\x00\x00\x24':continue
        h,wrap=unwrap_24(lane)
        try:
            raw,meta=decode_symbols(h,8,count)
            results.append(dict(frame=frame['index'],kind=d['kind'],lane=d['lane'],length=n,
                decoded=len(raw),unique=len(set(raw)),first=raw[:16].hex(),meta=meta))
        except Exception as exc:
            results.append(dict(frame=frame['index'],kind=d['kind'],lane=d['lane'],
                length=n,error=str(exc)))
        if len(results)>=12:break
    if len(results)>=12:break
print(json.dumps(dict(tile=f.name,pointCount=count,lanes=results),indent=2))
