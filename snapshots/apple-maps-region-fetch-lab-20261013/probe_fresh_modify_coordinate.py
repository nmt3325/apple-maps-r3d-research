#!/usr/bin/env python3
"""Compare a signed saved request with one coordinate changed, one request only."""
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs,parse_qsl,urlencode,urlunsplit
from urllib.request import urlopen,Request
from urllib.error import HTTPError,URLError
from pathlib import Path
import time
src=Path(__file__).resolve().parent/'captures/session-20261013-1913.mitm'
chosen=None
with src.open('rb') as inp:
 for f in io.FlowReader(inp).stream():
  if not f.response or f.response.status_code!=200:continue
  q=parse_qs(urlsplit(f.request.pretty_url).query)
  if q.get('style')!=['98'] or q.get('z')!=['14']:continue
  key=q.get('accessKey',[''])[0].split('_',2)
  if len(key)==3 and key[0].isnumeric() and int(key[0])>time.time()+120:
   chosen=f;break
if not chosen:raise SystemExit('No fresh signed request')
u=urlsplit(chosen.request.pretty_url)
params=parse_qsl(u.query,keep_blank_values=True)
p=dict(params)
origin=int(p['x']);p['x']=str(origin+1)
updated=[(k,p[k] if k=='x' else v) for k,v in params]
url=urlunsplit((u.scheme,u.netloc,u.path,urlencode(updated),u.fragment))
headers={k:chosen.request.headers[k] for k in ('user-agent','accept','accept-language','accept-encoding') if k in chosen.request.headers}
try:
 with urlopen(Request(url,headers=headers),timeout=10) as f:
  print('With x changed +1 and same accessKey: HTTP',f.status, 'first 8 bytes',f.read(8).hex())
except HTTPError as e:
 print('With x changed +1 and same accessKey: HTTP',e.code)
except URLError as e:
 print('Network issue:',type(e.reason).__name__)
