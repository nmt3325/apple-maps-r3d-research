#!/usr/bin/env python3
"""Analyze Huff816 tables in 295 captured R3D tiles without touching production."""
from pathlib import Path
from collections import Counter
import sys,json,struct,argparse
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huff816 import parse_table,build_tree,Huff816Error,unwrap_24,decode_symbols
ap=argparse.ArgumentParser()
ap.add_argument('--limit',type=int,default=295)
ap.add_argument('--output',type=Path)
args=ap.parse_args()
paths=list(sorted(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d')))
paths+=list(sorted(Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20').rglob('*.r3d')))
cnt=Counter();sample=[];bad=[]
for f in paths[:args.limit]:
    b=f.read_bytes();s=dissect(b)['splatStream']
    for frame in s['blocks']:
        spec=frame['byet'];p=s['offset']+spec['compressedPayloadRelativeOffset']
        j=b[p:p+spec['compressedPayloadBytes']]
        for d in split_j(j,12 if frame['index']==0 else 32)['descriptors']:
            n=d['compressedBytes']
            if n<24:continue
            lane=j[d['compressedOffset']:d['compressedOffset']+n]
            if lane[4:8]!=b'\x00\x00\x00\x24':continue
            try:
                h,wrap=unwrap_24(lane)
                marker=struct.unpack_from('<I',h)[0]
                if marker&0x80000000:
                    literal,info=decode_symbols(h,8,len(h)-4)
                    if literal != h[4:]:raise Huff816Error('literal payload mismatch')
                    cnt['literal']+=1
                    continue
                if (marker&0x7f0000ff)!=0x61000002:
                    cnt['other_marker']+=1
                    continue
                entries,at,stats=parse_table(h[4:],8)
                build_tree(entries)
                if wrap['wrapperU32'] != at+4:
                    raise Huff816Error(f'header table length {wrap["wrapperU32"]} != parsed {at+4}')
                cnt['parsed_tree']+=1
                if len(sample)<8:sample.append(dict(tile=f.name,block=frame['index'],kind=d['kind'],lane=d['lane'],compressed=n,marker=hex(marker),wrap=wrap,stats=stats,firstEntries=[vars(x) for x in entries[:8]]))
            except Exception as e:
                cnt['error_'+type(e).__name__]+=1
                if len(bad)<10:bad.append(dict(tile=f.name,block=frame['index'],lane=d['lane'],error=str(e)))
print(json.dumps(dict(tiles=args.limit,counts=dict(cnt),samples=sample,errors=bad),indent=2))
if args.output:args.output.write_text(json.dumps(dict(counts=dict(cnt),samples=sample,errors=bad),indent=2))
