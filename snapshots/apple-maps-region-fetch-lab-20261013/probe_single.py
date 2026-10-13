#!/usr/bin/env python3
"""One-request compatibility probe against the same Apple host as an observed map tile."""
from pathlib import Path
from mitmproxy import io
from urllib.parse import urlsplit,parse_qsl,urlunsplit,urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import hashlib,sys
if len(sys.argv)!=4:raise SystemExit('Usage: probe_single.py X Y Z')
tx,ty,tz=map(int,sys.argv[1:])
cap=Path('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm')
out=Path(__file__).resolve().parent/'probes'
out.mkdir(mode=0o700,exist_ok=True)
request_url=None
with cap.open('rb') as f:
 for row in io.FlowReader(f).stream():
  if not row.response or row.response.status_code!=200:continue
  u=urlsplit(row.request.pretty_url)
  qp=dict(parse_qsl(u.query))
  if qp.get('style')=='98' and qp.get('z')==str(tz) and qp.get('h')=='0':
   for k,val in [('x',str(tx)),('y',str(ty)),('z',str(tz))]:qp[k]=val
   request_url=urlunsplit((u.scheme,u.netloc,u.path,urlencode(qp),u.fragment))
   break
if request_url is None:raise SystemExit('No suitable captured template for that zoom')
try:
 req=Request(request_url,headers={'User-Agent':'GeoServices/1.0','Accept':'*/*'})
 with urlopen(req,timeout=12) as response:
  payload=response.read(3_000_000)
  status=response.status
except HTTPError as e:
 print('HTTP status',e.code,'body_bytes',len(e.read(128)))
 sys.exit(2)
except URLError as e:
 print('Transport failure',type(e.reason).__name__)
 sys.exit(3)
print('HTTP status',status,'bytes',len(payload),'signature',payload[:8].hex())
if status==200 and payload.startswith(bytes.fromhex('3d96592e02000000')):
 dest=out/f'fresh_z{tz}_x{tx}_y{ty}_h0.r3d'
 dest.write_bytes(payload);dest.chmod(0o600)
 print('Saved validated R3D',dest,'sha256',hashlib.sha256(payload).hexdigest())
