#!/usr/bin/env python3
"""Inspect only the structure of plaintext after successful legacy decryption; no sensitive strings printed."""
from pathlib import Path
from urllib.parse import urlsplit,parse_qsl
from mitmproxy import io
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
import hashlib,re,base64
old=Path('/root/.desktop-mcp/linux-4ebec5ed/work/Apple-3D-RE-Lightweight/main.go').read_text()
keys=[re.search(r'var\s+'+k+r'\s*=\s*"([^"]+)"',old).group(1) for k in ('tokenP1','tokenP2')]
with (Path(__file__).resolve().parent/'captures/session-20261013-1913.mitm').open('rb') as fh:
 for flow in io.FlowReader(fh).stream():
  if not flow.response or flow.response.status_code!=200 or flow.request.timestamp_start<1791882000:continue
  u=urlsplit(flow.request.pretty_url)
  qp=parse_qsl(u.query,keep_blank_values=True)
  if dict(qp).get('style')!='98':continue
  ts,nonce,crypt=dict(qp)['accessKey'].split('_',2)
  key=hashlib.sha256((''.join(keys)+nonce).encode()).digest()
  dec=Cipher(algorithms.AES(key),modes.CBC(bytes(16))).decryptor()
  clear=dec.update(base64.b64decode(crypt))+dec.finalize()
  clear=clear[:-clear[-1]]
  query=[(k,v) for k,v in qp if k!='accessKey']
  from urllib.parse import urlencode
  path=u.path+'?'+urlencode(query)
  suffix=(ts+nonce).encode()
  extra=clear[len(path):]
  print('prefix_match',clear.startswith(path.encode()),
   'includes_sid',b'sid=' in clear,'suffix_time_nonce',clear.endswith(suffix),
   'extra_length',len(extra),'extra_contains_sid',b'sid=' in extra,
   'extra_starts_ampersand',extra.startswith(b'&'),
   'request_parameters',[k for k,v in query])
  break
