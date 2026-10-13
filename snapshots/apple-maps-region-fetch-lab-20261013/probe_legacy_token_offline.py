#!/usr/bin/env python3
"""Offline only: test whether old public demo token pair decrypts a current captured request."""
from pathlib import Path
import re,hashlib,base64
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
old=Path('/root/.desktop-mcp/linux-4ebec5ed/work/Apple-3D-RE-Lightweight/main.go').read_text()
def extract(name):
 m=re.search(r'var\s+'+name+r'\s*=\s*"([^"]+)"',old)
 if not m:raise RuntimeError('Token declaration unavailable')
 return m.group(1)
a,b=extract('tokenP1'),extract('tokenP2')
cap=Path(__file__).resolve().parent/'captures/session-20261013-1913.mitm'
freshtokens=[]
with cap.open('rb') as fd:
 for flow in io.FlowReader(fd).stream():
  if not flow.response or flow.response.status_code!=200 or flow.request.timestamp_start<1791882000:continue
  q=parse_qs(urlsplit(flow.request.pretty_url).query)
  if q.get('style')!=['98']:continue
  parts=q.get('accessKey',[''])[0].split('_',2)
  if len(parts)==3:freshtokens.append((parts,q))
  if len(freshtokens)>=3:break
for i,(parts,q) in enumerate(freshtokens):
 try:
  ts,nonce,cipher64=parts
  key=hashlib.sha256((a+b+nonce).encode()).digest()
  plaintext=Cipher(algorithms.AES(key),modes.CBC(bytes(16))).decryptor().update(base64.b64decode(cipher64))
  pad=plaintext[-1]
  valid_padding=1<=pad<=16 and plaintext.endswith(bytes([pad])*pad)
  clean=plaintext[:-pad] if valid_padding else b''
  print('sample',i+1,'legacy AES-CBC decrypt valid PKCS7',valid_padding,'contains expected tile path',b'/tile?' in clean)
 except Exception as e:
  print('sample',i+1,'decrypt failed with',type(e).__name__)
