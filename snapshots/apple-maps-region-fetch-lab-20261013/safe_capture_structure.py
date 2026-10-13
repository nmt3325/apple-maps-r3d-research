#!/usr/bin/env python3
"""Read-only Apple Maps capture structural summary, never print URLs or tokens."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
from pathlib import Path
import re,json
cap=Path("/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm")
counts=Counter();auth=defaultdict(lambda:{"total":0,"timestamp_like":0,"unique_lengths":Counter(),"prefix_separator":Counter(),"versions":Counter(),"query_names":Counter()})
other=[]
with cap.open("rb") as fd:
 for f in io.FlowReader(fd).stream():
  if not getattr(f,"response",None):continue
  u=urlsplit(f.request.pretty_url)
  q=parse_qs(u.query)
  style=q.get("style",["unspecified"])[0]
  counts[(u.hostname,u.path,style,f.response.status_code)]+=1
  d=auth[style];d["total"]+=1
  d["versions"].update(q.get("v",[]));d["query_names"].update(q.keys())
  keys=q.get("accessKey",[])
  if keys:
   s=keys[0];d["unique_lengths"][len(s)]+=1
   parts=s.split("_",2)
   d["prefix_separator"][len(parts)]+=1
   if len(parts)==3 and parts[0].isdecimal() and len(parts[0])==10:d["timestamp_like"]+=1
  if u.path not in ("/tile","/tile.vf") and len(other)<35:
   other.append({"host":u.hostname,"path":u.path,"status":f.response.status_code,
                 "content_type":f.response.headers.get("content-type","").split(";")[0],
                 "body_header_hex":(f.response.content or b"")[:8].hex(),"style":style})
report={"counts":[{"host":h,"path":p,"style":s,"http_status":code,"count":n} for (h,p,s,code),n in counts.most_common()],
 "auth_structure":{s:{"total":d["total"],"timestamp_like":d["timestamp_like"],"lengths":dict(d["unique_lengths"]),"token_parts":dict(d["prefix_separator"]),
 "versions":dict(d["versions"]),"param_names":dict(d["query_names"])} for s,d in auth.items()},
 "non_tile_flow_examples":other}
print(json.dumps(report,indent=2)[:12500])