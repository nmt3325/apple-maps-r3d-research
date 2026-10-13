#!/usr/bin/env python3
"""Single live replay probe of freshly captured Apple Maps tile; never prints URL/token."""
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from pathlib import Path
import time
p=Path(__file__).resolve().parent/'captures/session-20261013-1913.mitm'
record=None
with p.open('rb') as stream:
 for flow in io.FlowReader(stream).stream():
  if not flow.response or flow.response.status_code!=200:continue
  q=parse_qs(urlsplit(flow.request.pretty_url).query)
  if q.get('style')!=['98'] or not flow.response.content:continue
  key=q.get('accessKey',[''])[0].split('_',2)
  if len(key)!=3 or not key[0].isdigit() or int(key[0])<time.time()+120:continue
  if flow.request.timestamp_start<1791882000:continue
  record=flow
  break
if record is None:raise SystemExit('No fresh unexpired R3D success in snapshot')
q=parse_qs(urlsplit(record.request.pretty_url).query)
print('Source: captured successful R3D tile (coords only)',{k:q.get(k) for k in ('style','z','x','y','h')})
print('Captured HTTP',record.response.status_code,'body',len(record.response.content))
headers={}
for key in ('user-agent','accept','accept-language','accept-encoding'):
 v=record.request.headers.get(key)
 if v:headers[key]=v
req=Request(record.request.pretty_url,headers=headers)
try:
 with urlopen(req,timeout=10) as response:
  sample=response.read(256)
  print('Exact fresh URL replay: HTTP',response.status,'response prefix',sample[:8].hex(),'content type',response.headers.get('content-type'))
except HTTPError as e:
 print('Exact fresh URL replay: HTTP',e.code)
except URLError as e:
 print('Exact fresh URL replay: transport failure',type(e.reason).__name__)
