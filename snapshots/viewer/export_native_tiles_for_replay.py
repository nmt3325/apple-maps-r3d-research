#!/usr/bin/env python3
"""Export only the authorized recorded style98 payloads; strip all auth URLs and headers."""
from mitmproxy import io
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
import json,hashlib
base=Path("/var/lib/flyover-replay")
(base/"tiles").mkdir(parents=True,exist_ok=True)
out=[]
seen=set()
with Path("/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm").open("rb") as f:
 for flow in io.FlowReader(f).stream():
  resp=getattr(flow,"response",None)
  if resp is None or resp.status_code!=200:continue
  req=flow.request;u=urlsplit(req.pretty_url)
  q=parse_qs(u.query)
  if req.pretty_host.lower()!="gspe11-ssl.ls.apple.com" or u.path!="/tile" or q.get("style")!=["98"]:continue
  keys=("style","v","region","x","y","z","h")
  if any(k not in q for k in keys):continue
  item={k:q[k][0] for k in keys}
  tup=tuple(item[k] for k in keys)
  if tup in seen:continue
  content=resp.content or b""
  if not content.startswith(bytes.fromhex("3d96592e02000000")):continue
  seen.add(tup)
  digest=hashlib.sha256(content).hexdigest()
  name=digest[:20]+".r3d"
  (base/"tiles"/name).write_bytes(content)
  out.append({**item,"file":name,"length":len(content),"sha256":digest})
(base/"index.json").write_text(json.dumps(out,separators=(',',':')),'utf-8')
print('sanitized recorded native r3d tiles',len(out),'bytes',sum(it['length'] for it in out))
