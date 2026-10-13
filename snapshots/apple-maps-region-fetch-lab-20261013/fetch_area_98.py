#!/usr/bin/env python3
"""Bounded, serial signed style98 tile fetch for an explicitly planned small region.
Independent outputs, no request URL or credentials printed or saved.
"""
import argparse,base64,gzip,hashlib,json,os,re,secrets,time
from pathlib import Path
from urllib.parse import parse_qsl,urlencode,urlsplit,urlunsplit,quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from mitmproxy import io
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--plan',type=Path,required=True)
p.add_argument('--name',required=True)
p.add_argument('--max-requests',type=int,default=80)
p.add_argument('--delay',type=float,default=0.4)
p.add_argument('--execute',action='store_true')
a=p.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',a.name):p.error('Invalid name')
plan=json.loads(a.plan.read_text())
tiles=plan['layers']['style98_3d_h0']
if not 1<=len(tiles)<=a.max_requests<=100:p.error('Tile count/max request limit invalid')
print('center',plan['center'],'radius_m',plan['radius_m'],'tiles',len(tiles))
if not a.execute:raise SystemExit('Dry run. Use --execute')
old=Path('/root/.desktop-mcp/linux-4ebec5ed/work/Apple-3D-RE-Lightweight/main.go').read_text()
keys=[re.search(r'var\s+'+k+r'\s*=\s*"([^"]+)"',old).group(1) for k in ('tokenP1','tokenP2')]
snapshot=ROOT/'captures/session-20261013-1913.mitm'
sample=None
with snapshot.open('rb') as f:
 for flow in io.FlowReader(f).stream():
  if not flow.response or flow.response.status_code!=200:continue
  url=urlsplit(flow.request.pretty_url)
  pars=dict(parse_qsl(url.query))
  if pars.get('style')=='98' and pars.get('z')=='20' and pars.get('h')=='0' and flow.response.content:
   sample=flow;break
if sample is None:raise SystemExit('No signing template')
u=urlsplit(sample.request.pretty_url)
params=[(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True) if k!='accessKey']
headers={k:sample.request.headers[k] for k in ('user-agent','accept','accept-language','accept-encoding') if k in sample.request.headers}
abc='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
def signed(coord):
 q=[(k,str(coord[k]) if k in ('x','y','z') else v) for k,v in params]
 requri=u.path+'?'+urlencode(q)
 nonce=''.join(secrets.choice(abc) for _ in range(16))
 timestamp=int(time.time())+4200
 payload=(requri+str(timestamp)+nonce).encode('utf-8')
 payload+=bytes([16-len(payload)%16])*(16-len(payload)%16)
 cipher=Cipher(algorithms.AES(hashlib.sha256((''.join(keys)+nonce).encode()).digest()),modes.CBC(bytes(16))).encryptor()
 encrypted=cipher.update(payload)+cipher.finalize()
 key=str(timestamp)+'_'+nonce+'_'+base64.b64encode(encrypted).decode()
 return urlunsplit((u.scheme,u.netloc,u.path,urlencode(q)+'&accessKey='+quote(key,safe=''),''))
out=ROOT/'fresh_signed'/a.name/'area_z20'
out.mkdir(parents=True,exist_ok=True,mode=0o700)
summary={'area':a.name,'center':plan['center'],'radius_m':plan['radius_m'],
  'z':20,'requested':len(tiles),'success':0,'existing':0,'invalid':0,'errors':[],
  'files':[],'note':'style98 h0 only; metadata/height sampled separately'}
consecutive_errors=0
for i,t in enumerate(tiles,1):
 path=out/('s98_z{z}_x{x}_y{y}_h0.r3d'.format(**t))
 if path.exists() and path.read_bytes()[:8]==bytes.fromhex('3d96592e02000000'):
  body=path.read_bytes()
  summary['existing']+=1
 else:
  try:
   with urlopen(Request(signed(t),headers=headers),timeout=15) as response:
    body=response.read(3_000_000)
    if body.startswith(b'\x1f\x8b'):body=gzip.decompress(body)
    if not body.startswith(bytes.fromhex('3d96592e02000000')):
     summary['invalid']+=1
     summary['errors'].append({'tile':t,'status':response.status,'bytes':len(body)})
     continue
    path.write_bytes(body);os.chmod(path,0o600)
    summary['success']+=1;consecutive_errors=0
  except HTTPError as e:
   summary['errors'].append({'tile':t,'status':e.code})
   consecutive_errors+=1
  except (URLError,TimeoutError) as e:
   summary['errors'].append({'tile':t,'error':type(e).__name__})
   consecutive_errors+=1
  time.sleep(a.delay)
 if path.exists():
  summary['files'].append({'tile':t,'file':path.name,'bytes':path.stat().st_size,
   'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 if i%10==0 or i==len(tiles):
  print('progress',i,'/',len(tiles),'new_valid',summary['success'],'existing',summary['existing'],
        'invalid',summary['invalid'],'http_errors',len(summary['errors']),flush=True)
 if consecutive_errors>=5:
  print('Aborting after 5 consecutive transport/HTTP errors',flush=True)
  break
manifest=out/'manifest.json'
manifest.write_text(json.dumps(summary,indent=2))
os.chmod(manifest,0o600)
print('Final manifest',manifest,'valid files',len(summary['files']),'total decoded bytes',
      sum(x['bytes'] for x in summary['files']),flush=True)
