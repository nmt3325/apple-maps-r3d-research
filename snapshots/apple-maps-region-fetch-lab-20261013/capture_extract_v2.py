#!/usr/bin/env python3
"""Offline geographic export of captured style 98 / 99 / 100 assets."""
import sys,json,os,hashlib
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from mitmproxy import io
home=Path(__file__).resolve().parent
plan=json.loads(Path(sys.argv[1]).read_text())['layers']
name=sys.argv[2]
if not name.replace('_','').replace('-','').isalnum():raise SystemExit('Invalid output name')
out=home/'exports'/name
out.mkdir(parents=True,mode=0o700,exist_ok=False)
want=set()
mapping=[(98,'style98_3d_h0',0),(98,'style98_3d_h1_optional',1),
 (98,'style98_context_z19',0),(98,'style98_context_z18',0),
 (99,'style99_height_z14',0),(100,'style100_metadata_z13',0),(100,'style100_root_z9',0)]
for s,key,h in mapping:
 want.update((s,v['z'],v['x'],v['y'],h) for v in plan[key])
sig={98:b'\x3d\x96\x59\x2e',99:b'\x89PNG',100:b'C3MM'}
ext={98:'r3d',99:'png',100:'c3mm'}
saved={}
with open('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm','rb') as fh:
 for flow in io.FlowReader(fh).stream():
  if not flow.response or flow.response.status_code!=200:continue
  q=parse_qs(urlsplit(flow.request.pretty_url).query)
  try:key=tuple(int(q[n][0]) for n in ('style','z','x','y','h'))
  except (KeyError,ValueError,IndexError):continue
  if key not in want:continue
  s,z,x,y,h=key
  body=flow.response.content or b''
  if not body.startswith(sig[s]):continue
  rel=f's{s}_z{z}_x{x}_y{y}_h{h}.{ext[s]}'
  path=out/rel;path.write_bytes(body);os.chmod(path,0o600)
  saved[key]={'file':rel,'style':s,'z':z,'x':x,'y':y,'h':h,'bytes':len(body),
   'sha256':hashlib.sha256(body).hexdigest()}
manifest={'area':name,'files':list(saved.values()),'matched':len(saved),
 'planned':len(want),'missing':len(want)-len(saved),
 'styles':{str(s):sum(k[0]==s for k in saved) for s in (98,99,100)}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
os.chmod(out/'manifest.json',0o600)
print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
