#!/usr/bin/env python3
"""Extract exact Apple Maps iOS27 style=98 R3D response bodies, no query strings/accessKey."""
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
from pathlib import Path
import json,hashlib,struct,zipfile
CAP=Path('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm')
PRIV=Path('/opt/flyover-viewer/native-r3d');PRIV.mkdir(exist_ok=True,mode=0o700)
PUBLIC=Path('/opt/flyover-viewer/www/native');PUBLIC.mkdir(exist_ok=True)
tiles={}
with CAP.open('rb') as fh:
 for f in io.FlowReader(fh).stream():
  if not getattr(f,'response',None) or f.response.status_code!=200:continue
  q=parse_qs(urlsplit(f.request.pretty_url).query)
  b=f.response.content or b''
  if q.get('style')!=['98'] or len(b)<300 or b[:8]!=bytes.fromhex('3d96592e02000000'):continue
  try:key=tuple(int(q[k][0]) for k in ('z','x','y','h'))
  except (KeyError,ValueError):continue
  tiles[key]=b
manifest=[]
for (z,x,y,h),b in sorted(tiles.items()):
 name=f'r3d_z{z}_x{x}_y{y}_h{h}.r3d'
 path=PRIV/name;path.write_bytes(b);path.chmod(0o600)
 manifest.append(dict(file=name,z=z,x=x,y=y,h=h,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(PRIV/'manifest.json').write_text(json.dumps(manifest,indent=2))
if manifest:
 sample=next((m for m in manifest if m['z']==20 and m['h']==0 and 100000<=m['bytes']<=250000),manifest[0])
 (PUBLIC/'test-tile.r3d').write_bytes((PRIV/sample['file']).read_bytes())
 (PUBLIC/'test-tile-metadata.json').write_text(json.dumps(sample,indent=2))
 print('test tile',sample)
print('R3D files:',len(tiles),'total bytes',sum(m['bytes'] for m in manifest))
