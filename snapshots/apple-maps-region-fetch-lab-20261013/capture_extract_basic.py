#!/usr/bin/env python3
"""Extract known Apple Maps tiles for a planned area without making new requests."""
import sys,json,pathlib
from urllib.parse import urlsplit,parse_qs
from mitmproxy import io
root=pathlib.Path(__file__).parent
plan=json.loads(pathlib.Path(sys.argv[1]).read_text())
dst=root/'exports'/sys.argv[2]
dst.mkdir(parents=True,exist_ok=False)
want=set()
for style,key in [(98,'style98_3d_h0'),(99,'style99_height_z14'),(100,'style100_metadata_z13')]:
 for item in plan['layers'][key]:
  want.add((style,item['z'],item['x'],item['y']))
found=set()
with open('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm','rb') as handle:
 for flow in io.FlowReader(handle).stream():
  if not flow.response or flow.response.status_code!=200:continue
  q=parse_qs(urlsplit(flow.request.pretty_url).query)
  try:key=tuple(int(q[t][0]) for t in ('style','z','x','y'))
  except (KeyError,ValueError,IndexError):continue
  if key not in want:continue
  s,z,x,y=key
  suffix={98:'r3d',99:'png',100:'c3mm'}[s]
  b=flow.response.content or b''
  (dst/f's{s}_z{z}_x{x}_y{y}.{suffix}').write_bytes(b)
  found.add(key)
print('Captured matched:',len(found),'Requested:',len(want),'Output:',dst)
