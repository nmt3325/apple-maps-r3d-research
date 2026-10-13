#!/usr/bin/env python3
"""Build a sanitized 3D spatial index and observed 16-bit heightfields from an authorized mitmproxy capture.
Original authentication URLs and accessKey tokens are deliberately NOT exported."""
import io as bio, json, math, struct, pathlib, collections, datetime
import numpy as np
from PIL import Image
from mitmproxy import io
from urllib.parse import urlsplit, parse_qs
CAPTURE=pathlib.Path("/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm")
OUT=pathlib.Path("/opt/flyover-viewer/www/data")
OUT.mkdir(parents=True, exist_ok=True)
features={}; rasters={}; stats=collections.Counter(); sizes=collections.Counter()
def geo(x,y,z):
    a=6378137.;e2=6.69437999014e-3;lon=math.degrees(math.atan2(y,x))
    p=math.hypot(x,y);lat=math.atan2(z,p*(1-e2))
    for _ in range(5):
        N=a/math.sqrt(1-e2*math.sin(lat)**2)
        alt=p/math.cos(lat)-N
        lat=math.atan2(z,p*(1-e2*N/(N+alt)))
    return [round(math.degrees(lat),9),round(lon,9),round(alt,4)]
def read_leb(b,i):
    val=0; shift=0
    while True:
        v=b[i];i+=1;val|=(v&127)<<shift;shift+=7
        if not v&128:return val,i
        if shift>28:raise ValueError("large varint")
with CAPTURE.open("rb") as f:
 for fl in io.FlowReader(f).stream():
    if not getattr(fl,"response",None):continue
    u=urlsplit(fl.request.pretty_url)
    q=parse_qs(u.query)
    s=q.get("style",[""])[0]
    if s in ("99","100"): print("PRE",s,fl.response.status_code,len(fl.response.content or b""))
    if fl.response.status_code !=200 or not fl.response.content:continue
    b=fl.response.content
    if s=="99": print("DEBUG99", b[:8].hex(), b.startswith(bytes.fromhex("89504e47")))
    if s=="98" and len(b)>128 and b[:4]==bytes.fromhex("3d96592e"):
        x,y,z,h=(int(q[k][0]) for k in ("x","y","z","h"))
        cnt,i=read_leb(b,12)
        off=i+6
        rot=struct.unpack_from("<9d",b,off)
        ecef=struct.unpack_from("<3d",b,off+9*8)
        if not all(abs(a)<1.0002 for a in rot):continue
        loc=geo(*ecef)
        if not 30<loc[0]<40 or not 130<loc[1]<150:continue
        key=(x,y,z,h)
        v={"id":f"{z}-{x}-{y}-h{h}","x":x,"y":y,"z":z,"h":h,
           "countField":cnt,"bytes":len(b),"lat":loc[0],"lon":loc[1],
           "rot":[round(t,7) for t in rot]}
        features[key]=v
        stats["style98"]+=1
    elif s=="99" and b.startswith(b"\x89PNG"):
        x,y,z=(int(q[k][0]) for k in ("x","y","z"))
        rasters[(x,y,z)]=b
        stats["style99"]+=1
    elif s=="100" and b.startswith(b"C3MM\x02"):
        stats["style100"]+=1
dataset={"generatedUTC":datetime.datetime.now(datetime.UTC).isoformat(),
 "source":"saved mitmproxy HTTP payload; accessKey stripped",
 "captureFileSize":CAPTURE.stat().st_size,
 "style98Records":sorted(features.values(),key=lambda x:(x["y"],x["x"],x["h"])),
 "style99Tiles":[],"spatialCoords":"XYZ map tile with Y increasing south",
 "style98DecodedFields":"tile x,y,z,h; variable-length count field; 3x3 rotation matrix; ECEF translation"}
for (x,y,z),b in sorted(rasters.items()):
    a=np.asarray(Image.open(bio.BytesIO(b)),dtype=np.uint16)
    assert a.shape==(512,512)
    # retain every other pixel, preserve actual unsigned 16-bit samples
    sampled=a[::2,::2].copy()
    fn=f"elevation_z{z}_x{x}_y{y}.bin"
    (OUT/fn).write_bytes(sampled.astype("<u2").tobytes())
    # 8-bit inspectable diagnostic grayscale, contrast stretched; NOT a source elevation asset
    den=max(1,int(a.max())-int(a.min()))
    img=np.rint((a-a.min())*(255/den)).astype("uint8")
    Image.fromarray(img).save(OUT/f"preview_z{z}_x{x}_y{y}.png")
    dataset["style99Tiles"].append({"x":x,"y":y,"z":z,"file":fn,"preview":f"preview_z{z}_x{x}_y{y}.png",
        "rows":256,"columns":256,"rasterMax":int(a.max()),"rasterMin":int(a.min()),
        "rasterMean":round(float(a.mean()),2)})
(OUT/"dataset.json").write_text(json.dumps(dataset,ensure_ascii=False,separators=(',',':')),"utf8")
print(json.dumps({"unique_style98":len(features),"unique_style99":len(rasters),"raw_styles":stats,
                   "style99_tiles":dataset["style99Tiles"],"total_bytes":CAPTURE.stat().st_size},indent=2))
