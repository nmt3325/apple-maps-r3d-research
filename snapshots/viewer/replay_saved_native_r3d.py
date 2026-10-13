"""Replay saved Apple Maps native R3D tiles through a separate opt-in HTTPS proxy.

Only replays 200 OK /tile style=98 data from a locally saved authorized HTTPS capture,
matching x/y/z/h/style/v/region and ignoring short-lived accessKey/preflight tokens.
Everything else is passed through unchanged. Do not expose outside the Tailnet.
"""
from __future__ import annotations
from mitmproxy import ctx, http
from urllib.parse import parse_qs, urlsplit
import pathlib, json, hashlib, datetime

INDEX=pathlib.Path("/var/lib/flyover-replay/index.json")
HOST="gspe11-ssl.ls.apple.com"
KEYS=("style","v","region","x","y","z","h")

def get_key(host: str, path: str, q: dict):
    if host != HOST or path != "/tile" or q.get("style",[""])[0] != "98":return None
    try:return tuple(q[k][0] for k in KEYS)
    except (KeyError,IndexError):return None

class NativeTileReplay:
    def __init__(self):
        self.cache={}
        self.hits=0
        self.misses=0

    def load(self,loader):
        for item in json.loads(INDEX.read_text("utf8")):
            k=tuple(item[x] for x in KEYS)
            path=INDEX.parent / "tiles" / item["file"]
            data=path.read_bytes()
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError("Recorded tile sha256 mismatch")
            self.cache[k]=data
        ctx.log.info(f"R3D replay ready with {len(self.cache)} authenticated offline tile bodies (credentials stripped)")

    def write_event(self,action, k, size):
        record={"utc":datetime.datetime.now(datetime.UTC).isoformat(),"event":action,"style":k[0],"z":k[5],"x":k[3],"y":k[4],"h":k[6],"bytes":size}
        with (INDEX.parent / "replay_hits.jsonl").open("a",encoding="utf8") as f:
            f.write(json.dumps(record,separators=(",",":"))+"\n")

    def request(self,flow:http.HTTPFlow):
        u=urlsplit(flow.request.pretty_url)
        k=get_key(flow.request.pretty_host.lower(),u.path,parse_qs(u.query))
        if k is None:return
        data=self.cache.get(k)
        if data is not None:
            flow.response=http.Response.make(200,data,{
                "Content-Type":"application/octet-stream",
                "Cache-Control":"no-store",
                "X-Flyover-Cache-Source":"ct104-capture-20261013",
            })
            self.hits+=1
            self.write_event("REPLAY",k,len(data))
            ctx.log.info(f"REPLAY style98 z={k[5]} x={k[3]} y={k[4]} h={k[6]} bytes={len(data)}")
        else:
            self.misses+=1
            self.write_event("MISS",k,0)
            ctx.log.info(f"MISS style98 z={k[5]} x={k[3]} y={k[4]} h={k[6]} (forwarded upstream)")
addons=[NativeTileReplay()]
