#!/usr/bin/env python3
"""Test whether an exact previously observed tile request remains usable. No URLs printed."""
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
cap='/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm'
with open(cap,'rb') as f:
 for flow in io.FlowReader(f).stream():
  if not flow.response or flow.response.status_code!=200:continue
  p=urlsplit(flow.request.pretty_url)
  q=parse_qs(p.query)
  if q.get('style')==['98'] and q.get('z')==['20'] and q.get('h')==['0']:
   url=flow.request.pretty_url
   print('test coordinates:',q.get('x'),q.get('y'),'signature in original',flow.response.content[:8].hex())
   break
 else:raise SystemExit('No original sample')
try:
 with urlopen(Request(url,headers={'User-Agent':'GeoServices/1.0','Accept':'*/*'}),timeout=12) as response:
  payload=response.read(128)
  print('Live response',response.status,'first bytes',payload[:8].hex())
except HTTPError as e:print('Live response',e.code,'body length prefix',len(e.read(128)))
except URLError as e:print('Transport failure',type(e.reason).__name__)
