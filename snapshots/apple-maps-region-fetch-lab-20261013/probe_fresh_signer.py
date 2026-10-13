#!/usr/bin/env python3
"""Minimal proof: sign a fresh iOS27 Flyover request using legacy public SDK keys.
No URL, token, key or binary payload is printed. Limits to two single-tile requests.
"""
from pathlib import Path
from urllib.parse import urlsplit,parse_qs,parse_qsl,urlencode,urlunsplit,quote
from urllib.request import urlopen,Request
from urllib.error import HTTPError,URLError
from mitmproxy import io
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
import base64,hashlib,re,time,secrets,gzip,os
base=Path(__file__).resolve().parent
old=Path('/root/.desktop-mcp/linux-4ebec5ed/work/Apple-3D-RE-Lightweight/main.go').read_text()
parts=[re.search(r'var\s+'+name+r'\s*=\s*"([^"]+)"',old).group(1) for name in ('tokenP1','tokenP2')]
sample=None
with (base/'captures/session-20261013-1913.mitm').open('rb') as fh:
 for f in io.FlowReader(fh).stream():
  if not f.response or f.response.status_code!=200 or f.request.timestamp_start<1791882000:continue
  q=parse_qs(urlsplit(f.request.pretty_url).query)
  if q.get('style')==['98'] and q.get('z')==['14'] and q.get('h')==['0'] and f.response.content:
   sample=f;break
if not sample:raise SystemExit('Missing sample')
u=urlsplit(sample.request.pretty_url)
query=[(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True) if k!='accessKey']
headers={k:sample.request.headers[k] for k in ('user-agent','accept','accept-language','accept-encoding') if k in sample.request.headers}
alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
def sign(qpairs):
    original=urlencode(qpairs)
    uri=u.path+'?'+original
    nonce=''.join(secrets.choice(alphabet) for _ in range(16))
    expiry=int(time.time())+4200
    key=hashlib.sha256((''.join(parts)+nonce).encode()).digest()
    plain=(uri+str(expiry)+nonce).encode()
    pad=16-len(plain)%16
    plain+=bytes([pad])*pad
    enc=Cipher(algorithms.AES(key),modes.CBC(bytes(16))).encryptor()
    crypt=enc.update(plain)+enc.finalize()
    auth=str(expiry)+'_'+nonce+'_'+base64.b64encode(crypt).decode()
    return urlunsplit((u.scheme,u.netloc,u.path,original+'&accessKey='+quote(auth,safe=''),''))
x=int(dict(query)['x'])
out=base/'fresh_signed'
out.mkdir(exist_ok=True,mode=0o700)
for purpose,delta in [('original_coordinate',0),('new_neighbor_coordinate',1)]:
    q=[(k,str(x+delta) if k=='x' else v) for k,v in query]
    target=sign(q)
    try:
        with urlopen(Request(target,headers=headers),timeout=12) as res:
            data=res.read(3_000_000)
            if res.headers.get('Content-Encoding')=='gzip' or data[:2]==b'\x1f\x8b':
                data=gzip.decompress(data)
            is_r3d=data.startswith(bytes.fromhex('3d96592e02000000'))
            print(purpose,'HTTP',res.status,'decoded_bytes',len(data),'valid_r3d',is_r3d)
            if res.status==200 and is_r3d:
                dst=out/(purpose+'.r3d')
                dst.write_bytes(data);os.chmod(dst,0o600)
                print('saved',dst.name,'sha256',hashlib.sha256(data).hexdigest()[:16])
    except HTTPError as err:
        print(purpose,'HTTP',err.code)
    except URLError as err:
        print(purpose,'network_error',type(err.reason).__name__)
