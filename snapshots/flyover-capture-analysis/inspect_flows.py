#!/usr/bin/env python3
from mitmproxy import io
from collections import Counter, defaultdict
from urllib.parse import urlsplit
from pathlib import Path
import sys, re, time

p=Path(sys.argv[1] if len(sys.argv)>1 else "/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm")
st=p.stat()
print("file_size_bytes",st.st_size,"mtime",time.strftime("%Y-%m-%d %H:%M:%S %Z",time.localtime(st.st_mtime)))
hostcounts=Counter(); statuses=Counter(); types=Counter(); methods=Counter(); paths=Counter(); samples=defaultdict(list); hostbytes=Counter(); pathbytes=Counter(); sizes=[]; reqts=[]; errors=Counter()
n=0
try:
 with p.open("rb") as f:
  reader=io.FlowReader(f)
  for flow in reader.stream():
   if not hasattr(flow,"request") or flow.request is None: continue
   req=flow.request; resp=flow.response
   host=req.pretty_host.lower()
   u=urlsplit(req.pretty_url)
   path=u.path or "/"
   # Remove opaque tokens / GUIDs / long number chunks and restrict URL to path only
   norm=re.sub(r"[a-fA-F0-9]{24,}","{HEX}",path)
   norm=re.sub(r"\\d{4,}","{N}",norm)
   norm=norm[:190]
   size=len(resp.raw_content or b"") if resp else 0
   status=resp.status_code if resp else "none"
   ct=(resp.headers.get("content-type","?").split(";")[0] if resp else "?")
   hostcounts[host]+=1; hostbytes[host]+=size;statuses[(host,status)]+=1;types[(host,ct)]+=1;methods[req.method]+=1;paths[(host,norm)]+=1;pathbytes[(host,norm)]+=size;n+=1
   if len(samples[host])<12: samples[host].append((req.method,norm,status,ct,size, round(req.timestamp_start or 0)))
   if size>250000: sizes.append((size,host,norm,status,ct,round(req.timestamp_start or 0)))
   if resp is None: errors[str(getattr(flow,"error",None))[:100]]+=1
except Exception as e:
 print("reader_warning:",type(e).__name__,str(e)[:300])
print("total_flows",n)
print("HOSTS (count,response_bytes)")
for h,c in hostcounts.most_common(45): print(h,c,hostbytes[h])
print("STATUS")
for (h,st),c in statuses.most_common(35):print(h,st,c)
print("CONTENT_TYPES")
for (h,ct),c in types.most_common(40):print(h,ct,c)
print("TOP_PATHS")
for (h,pa),c in paths.most_common(40):print(h,pa,c,"bytes",pathbytes[(h,pa)])
print("LARGEST_BODIES")
for row in sorted(sizes,reverse=True)[:35]:print(*row)
print("HOST_SAMPLES")
for h,c in hostcounts.most_common(15):
 print("==",h)
 for s in samples[h]:print(*s)
print("errors",errors.most_common(8))
