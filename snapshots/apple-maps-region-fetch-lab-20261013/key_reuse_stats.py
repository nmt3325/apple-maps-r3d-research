#!/usr/bin/env python3
"""Count per-request credential reuse without disclosing any credential."""
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
from collections import defaultdict,Counter
d=defaultdict(list)
with open('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm','rb') as fh:
 for f in io.FlowReader(fh).stream():
  if not f.response:continue
  q=parse_qs(urlsplit(f.request.pretty_url).query)
  s=q.get('style',['other'])[0]
  if s in ('98','99','100'):
   d[s].append((q.get('accessKey',[''])[0],q.get('preflight',[''])[0],q.get('v',[''])[0]))
for s,ls in sorted(d.items()):
 print('style',s,'requests',len(ls),'distinct accessKey',len(set(k for k,p,v in ls)),
  'accessKey lengths',dict(Counter(len(k) for k,p,v in ls)),
  'preflight values',dict(Counter(p for k,p,v in ls)),
  'versions',dict(Counter(v for k,p,v in ls)))
