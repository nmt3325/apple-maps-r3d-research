#!/usr/bin/env python3
"""Experimental single-tile Apple Maps iOS27 fetcher based on observed style, region and version.
Reuses PUBLIC legacy signing token pair from lightweight source, not a saved accessKey.
Never prints authentication material. Default dry-run. Intended only for permitted tests.
"""
import argparse,base64,gzip,hashlib,math,os,re,secrets,time
from pathlib import Path
from urllib.parse import urlsplit,parse_qsl,urlencode,urlunsplit,quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from mitmproxy import io
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
base=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--lat',type=float,required=True);parser.add_argument('--lon',type=float,required=True)
parser.add_argument('--zoom',type=int,default=20);parser.add_argument('--style',type=int,choices=[98,99,100],default=98)
parser.add_argument('--label',default='probe');parser.add_argument('--execute',action='store_true')
a=parser.parse_args()
if not -85<a.lat<85 or not -180<a.lon<180 or not 0<=a.zoom<=22:parser.error('Invalid geospatial coordinates')
if not re.fullmatch('[a-zA-Z0-9_-]{1,60}',a.label):parser.error('Invalid label')
N=2**a.zoom
x=math.floor((a.lon+180)/360*N)
y=math.floor((1-math.asinh(math.tan(math.radians(a.lat)))/math.pi)/2*N)
print('target tile',dict(style=a.style,z=a.zoom,x=x,y=y,h=0))
if not a.execute:raise SystemExit('Dry run only; use --execute to issue exactly one request')
old=Path('/root/.desktop-mcp/linux-4ebec5ed/work/Apple-3D-RE-Lightweight/main.go').read_text()
tokens=[re.search(r'var\s+'+n+r'\s*=\s*"([^"]+)"',old).group(1) for n in ('tokenP1','tokenP2')]
cap=base/'captures/session-20261013-1913.mitm'
sample=None
with cap.open('rb') as inp:
 for f in io.FlowReader(inp).stream():
  if not f.response or f.response.status_code!=200:continue
  q=dict(parse_qsl(urlsplit(f.request.pretty_url).query))
  if q.get('style')==str(a.style) and q.get('z')==str(a.zoom):
   sample=f;break
if sample is None:raise SystemExit('No captured request template for this style+zoom')
u=urlsplit(sample.request.pretty_url)
params=[(k, str({'z':a.zoom,'x':x,'y':y,'h':0}[k]) if k in ('z','x','y','h') else v)
       for k,v in parse_qsl(u.query,keep_blank_values=True) if k!='accessKey']
uri=u.path+'?'+urlencode(params)
chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
nonce=''.join(secrets.choice(chars) for _ in range(16))
ts=int(time.time())+4200
key=hashlib.sha256((''.join(tokens)+nonce).encode()).digest()
plaintext=(uri+str(ts)+nonce).encode()
pad=16-len(plaintext)%16;plaintext+=bytes([pad])*pad
ctx=Cipher(algorithms.AES(key),modes.CBC(bytes(16))).encryptor()
cypher=ctx.update(plaintext)+ctx.finalize()
access=str(ts)+'_'+nonce+'_'+base64.b64encode(cypher).decode()
target=urlunsplit((u.scheme,u.netloc,u.path,urlencode(params)+'&accessKey='+quote(access,safe=''),''))
headers={k:sample.request.headers[k] for k in ('user-agent','accept','accept-language','accept-encoding') if k in sample.request.headers}
try:
 with urlopen(Request(target,headers=headers),timeout=12) as r:
  blob=r.read(3000000)
  if blob[:2]==b'\x1f\x8b':blob=gzip.decompress(blob)
  sig={98:bytes.fromhex('3d96592e'),99:b'\x89PNG',100:b'C3MM'}[a.style]
  valid=blob.startswith(sig)
  print('HTTP',r.status,'bytes',len(blob),'format_valid',valid,'first4',blob[:4].hex())
  if valid:
   d=base/'fresh_signed'/a.label;d.mkdir(parents=True,exist_ok=True,mode=0o700)
   ext={98:'r3d',99:'png',100:'c3mm'}[a.style]
   p=d/f's{a.style}_z{a.zoom}_x{x}_y{y}.{ext}'
   p.write_bytes(blob);os.chmod(p,0o600)
   print('saved',p,'sha256',hashlib.sha256(blob).hexdigest())
except HTTPError as e:print('HTTP',e.code)
except URLError as e:print('network failure',type(e.reason).__name__)
