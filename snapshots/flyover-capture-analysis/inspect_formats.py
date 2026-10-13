#!/usr/bin/env python3
from mitmproxy import io
from collections import Counter, defaultdict
from urllib.parse import urlsplit,parse_qs
import binascii,math,struct
src="/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm"
types=Counter(); vals=defaultdict(Counter); status=Counter(); hdrs=Counter(); signatures=Counter(); by_style=Counter(); examples=defaultdict(list); postsize=Counter()
safe={"style","v","region","z","h","part","x","y","scale","lod","type","format","version","size","tile"}
with open(src,"rb") as f:
 for i,fl in enumerate(io.FlowReader(f).stream()):
  if not getattr(fl,"request",None): continue
  r=fl.request; resp=fl.response
  u=urlsplit(r.pretty_url)
  q=parse_qs(u.query)
  if u.path not in ("/tile","/tile.vf"):continue
  keys=tuple(sorted(q))
  types[(r.pretty_host,u.path,keys)]+=1
  for k in safe.intersection(q):
   for v in q[k]: vals[k][v]+=1
  if resp is None:continue
  raw=resp.raw_content or b""
  dec=resp.content or b""
  prefix=raw[:24].hex(" ")
  sig=(r.pretty_host,u.path,q.get("style",["?"])[0],prefix[:23])
  signatures[sig]+=1
  style=q.get("style",["?"])[0]
  by_style[(u.path,style,resp.status_code)]+=1
  ctype=resp.headers.get("content-type","")
  encoding=resp.headers.get("content-encoding","")
  hdrs[(style,ctype,encoding)]+=1
  if len(examples[(u.path,style)])<6:
   examples[(u.path,style)].append({"status":resp.status_code,"len_raw":len(raw),"len_dec":len(dec),"raw_first_40_hex":raw[:40].hex(" "),"raw_first_35_ascii":repr(raw[:35]),"dec_first_20_hex":dec[:20].hex(" "), "q":{k:vs for k,vs in q.items() if k in ("style","v","region","z","h","part")}})
print("QUERY-KEY-SHAPES")
for k,n in types.most_common(20):print(n,*k)
print("WHITELISTED QUERY VALUE COUNTS")
for k,c in sorted(vals.items()): print(k,"distinct",len(c),"most-common",c.most_common(18))
print("BY-STYLE")
for k,n in by_style.most_common():print(k,n)
print("HEADER-TYPES")
for k,n in hdrs.most_common(20):print(k,n)
print("MAGIC PREFIXES")
for sig,c in signatures.most_common(28):print(c,sig)
print("EXAMPLES")
for key,rows in examples.items():
 print(key)
 for r in rows: print(r)
