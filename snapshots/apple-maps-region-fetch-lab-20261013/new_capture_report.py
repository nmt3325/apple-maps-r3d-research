#!/usr/bin/env python3
"""Read-only safe statistics from a snapshot of the user's Apple Maps capture."""
from collections import Counter, defaultdict
from datetime import datetime,timezone
from urllib.parse import parse_qs,urlsplit
from mitmproxy import io
import json,math
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'captures/session-20261013-1913.mitm'
cut=1791867426 # 2026-10-13 04:57:06 UTC, previous file's mtime
groups={'before':Counter(),'after':Counter()}
ext={'before':defaultdict(set),'after':defaultdict(set)}
bounds=defaultdict(list); samples={};last=[]
new_tokens=[];total=0
with p.open('rb') as f:
 for flow in io.FlowReader(f).stream():
  if not getattr(flow,'request',None):continue
  when=flow.request.timestamp_start
  period='after' if when>cut else 'before'
  response=getattr(flow,'response',None)
  u=urlsplit(flow.request.pretty_url)
  q=parse_qs(u.query)
  style=q.get('style',['other'])[0]
  status=response.status_code if response else 0
  body=(response.content or b'') if response else b''
  groups[period][(style,str(status))]+=1
  try:
   tile=tuple(int(q[k][0]) for k in ('z','x','y','h'))
   ext[period][style].add(tile)
   if period=='after' and status==200 and style in ('98','99','100'):
    z,x,y,h=tile
    lon=(x+0.5)/2**z*360-180
    lat=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y+0.5)/2**z))))
    bounds[style].append((lat,lon,z,x,y,h,len(body)))
    if style not in samples: samples[style]={'z':z,'x':x,'y':y,'h':h,'size':len(body),'header':body[:8].hex()}
  except (KeyError,ValueError,IndexError):pass
  if period=='after' and style=='98' and status==200:
   key=q.get('accessKey',[''])[0].split('_',2)
   if len(key)==3 and key[0].isdigit():
    new_tokens.append(int(key[0])-when)
  if period=='after':
   last.append((when,style,status,len(body)))
   if len(last)>12:last.pop(0)
  total+=1
print('snapshot',p.stat().st_size,'flows',total)
for period in ('before','after'):
 print(period,'flow_counts',dict(groups[period]))
 print(period,'unique_tiles', {s:len(v) for s,v in ext[period].items()})
for s,rows in bounds.items():
 lat=[a[0] for a in rows];lon=[a[1] for a in rows]
 print('NEW_STYLE',s,'count',len(rows),'unique',len(set((v[2],v[3],v[4],v[5]) for v in rows)),
 'lat',round(min(lat),6),round(max(lat),6),'lon',round(min(lon),6),round(max(lon),6),
 'z',dict(Counter(v[2] for v in rows)),'h',dict(Counter(v[5] for v in rows)),
 'bodyMB',round(sum(v[6] for v in rows)/1000000,2))
print('R3D accessKey valid seconds relative to capture',round(min(new_tokens),1) if new_tokens else None,round(max(new_tokens),1) if new_tokens else None)
print('first samples',samples)
print('last events',[(datetime.fromtimestamp(t,timezone.utc).isoformat(),s,n,bytes_) for t,s,n,bytes_ in last])
