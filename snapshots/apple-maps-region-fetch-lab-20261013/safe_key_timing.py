#!/usr/bin/env python3
"""Compare observed token expiration timestamp with capture time (never print token)."""
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
from collections import Counter,defaultdict
import statistics
d=defaultdict(list); lengths=defaultdict(Counter); p3len=defaultdict(Counter)
with open('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm','rb') as fh:
 for f in io.FlowReader(fh).stream():
  if not f.response: continue
  q=parse_qs(urlsplit(f.request.pretty_url).query)
  style=q.get('style',['?'])[0]
  key=q.get('accessKey',[''])[0].split('_',2)
  if len(key)!=3 or not key[0].isdecimal():continue
  delta=int(key[0])-f.request.timestamp_start
  d[style].append(delta); lengths[style][len(key[2])]+=1;p3len[style][len(key[1])]+=1
for style in ('98','99','100','68'):
 vals=d.get(style,[])
 if not vals:continue
 print('style',style,'samples',len(vals),'expiry_minus_request_sec',
       round(min(vals),1),round(statistics.median(vals),1),round(max(vals),1),
       'random_lengths',dict(p3len[style]),'cipher_lengths',dict(lengths[style]))
