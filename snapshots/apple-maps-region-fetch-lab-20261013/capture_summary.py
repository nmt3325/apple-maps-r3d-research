#!/usr/bin/env python3
"""Read-only summary of already captured tile coordinates."""
from pathlib import Path
from collections import Counter,defaultdict
from urllib.parse import urlsplit,parse_qs
from mitmproxy import io
f=Path("/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm")
count=Counter()
groups=defaultdict(list)
params=defaultdict(set)
with f.open("rb") as stream:
    for flow in io.FlowReader(stream).stream():
        if flow.response is None: continue
        q=parse_qs(urlsplit(flow.request.pretty_url).query)
        style=q.get("style",["other"])[0]
        count[(style,flow.response.status_code)]+=1
        params[style].update(q.keys())
        try:
            groups[(style,int(q["z"][0]))].append((int(q["x"][0]),int(q["y"][0]),int(q.get("h",["0"])[0])))
        except (KeyError,ValueError,IndexError):pass
for (s,status),n in count.most_common():
    print("style",s,"status",status,"count",n,"parameter names",sorted(params[s]))
for (s,z),lst in sorted(groups.items()):
    xs=[x for x,y,h in lst]; ys=[y for x,y,h in lst]; hs=Counter(h for x,y,h in lst)
    print("tile style",s,"z",z,"requests",len(lst),"unique",len(set(lst)),"x",min(xs),max(xs),"y",min(ys),max(ys),"h",dict(hs))
