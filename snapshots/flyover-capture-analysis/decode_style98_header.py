#!/usr/bin/env python3
"""Locate version-2 style-98 binary segment boundaries, without touching URLs or auth tokens."""
import json, pathlib, struct, statistics, collections
from mitmproxy import io
from urllib.parse import urlsplit, parse_qs
fpath=pathlib.Path('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm')
out=pathlib.Path('/root/.desktop-mcp/linux-4ebec5ed/work/flyover-capture-analysis')
out.mkdir(exist_ok=True)
def leb(b,p):
 v=0;s=0
 for _ in range(5):
  c=b[p];p+=1;v+=(c&127)<<s;s+=7
  if c<128:return v,p
 raise ValueError('long varint')
sig1=bytes.fromhex('01010100016a')
sig2=bytes.fromhex('01010100019801')
features={}
checks=collections.Counter();err=[]
with fpath.open('rb') as f:
 for flow in io.FlowReader(f).stream():
  if not getattr(flow,'response',None):continue
  req=flow.request;u=urlsplit(req.pretty_url)
  q=parse_qs(u.query)
  b=flow.response.content or b''
  if q.get('style')!=['98'] or len(b)<300:continue
  try:
   assert b[:8]==bytes.fromhex('3d96592e02000000'), 'magic mismatch'
   n,end=leb(b,12)
   a=b.find(sig1);pos=b.find(sig2)
   assert a==end, f'first header pos={a}, after count={end}'
   assert pos in (n+16+(end-12),n+15+(end-12)), f'second marker={pos}, predicted={n+16+(end-12)}'
   assert b[a+6:a+102]==b[pos+7:pos+103], 'transform difference'
   m,mend=leb(b,169+end-12)
   assert n-m==(157+(end-12)), f'count delta {n-m}, expected {157+end-12}'
   xyz=struct.unpack_from('<3d',b,a+6+72)
   count_marker=b.find(bytes.fromhex('d122c90701000000'))
   assert count_marker>0
   count=int.from_bytes(b[count_marker+8:count_marker+12],'little')
   key=(int(q['z'][0]),int(q['x'][0]),int(q['y'][0]),int(q['h'][0]))
   checks['validated']+=1
   features[key]={
     'z':key[0],'x':key[1],'y':key[2],'h':key[3],
     'bytes':len(b),'firstSectionBoundaryField':n,
     'secondSectionMarkerOffset':pos,
     'secondVarintField':m,'candidateElementCount':count,
     'firstSectionHeaderOffset':a,'transformBytesEqual':True
   }
  except Exception as e:
   checks['failed']+=1
   if len(err)<5:err.append({'error':str(e),'size':len(b)})
rows=list(features.values())
report={'capture':fpath.name,'style98CapturedValidated':checks['validated'],'style98UniqueTiles':len(rows),
  'failed':checks['failed'],'sampleFailures':err,
  'firstSectionBoundaryRange':[min(r['firstSectionBoundaryField'] for r in rows),max(r['firstSectionBoundaryField'] for r in rows)],
  'tileSizesBytesMedian':statistics.median(r['bytes'] for r in rows),
  'notes':[
    'All successfully parsed style98 bodies start with 3D96592E02000000',
    'A first shared ECEF + rotation transform is repeated exactly in a second section.',
    'The second-section marker is at the first varint value plus 15-16 + varint-length bytes (11 h=1 cases differ by one).',
    'The first varint equals second varint plus a constant header-adjustment (157 + first-varint-byte-length).',
    'No per-Gaussian XYZ/SH/opacity decompression has been implemented.']}
(out/'style98_structure.json').write_text(json.dumps({'summary':report,'tiles':rows},indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
