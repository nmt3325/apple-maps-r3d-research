#!/usr/bin/env python3
"""Check whether the BYET lane compact prefix determines Huff816 output count."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_trico_size import read_size
from nativefree_huff816 import unwrap_24,decode_symbols
f=sorted(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'))[0]
b=f.read_bytes();s=dissect(b)['splatStream'];rows=[]
for frame in s['blocks']:
 spec=frame['byet'];p=s['offset']+spec['compressedPayloadRelativeOffset']
 payload=b[p:p+spec['compressedPayloadBytes']]
 for d in split_j(payload,12 if frame['index']==0 else 32)['descriptors']:
  n=d['compressedBytes']
  if n<24:continue
  lane=payload[d['compressedOffset']:d['compressedOffset']+n]
  if lane[4:8]!=b'\x00\x00\x00\x24':continue
  size,after=read_size(lane)
  h,wrap=unwrap_24(lane)
  try:
   raw,meta=decode_symbols(h,8,size)
   state=dict(decoded=len(raw),entropyBits=meta.get('entropyBitsConsumed'),unique=len(set(raw)),
     payloadBytes=len(h)-4-wrap['wrapperU32'],unusedBits=8*(len(h)-4-wrap['wrapperU32'])-meta.get('entropyBitsConsumed',0))
  except Exception as e:state=dict(error=str(e))
  rows.append(dict(block=frame['index'],kind=d['kind'],lane=d['lane'],sizePrefix=size,sizeBytes=after,
   compressed=n,**state))
print(json.dumps(dict(tile=f.name,pointCount=s['pointCount'],lanes=rows),indent=2))
