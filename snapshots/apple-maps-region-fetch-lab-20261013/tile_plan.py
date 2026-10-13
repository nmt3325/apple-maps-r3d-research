#!/usr/bin/env python3
"""Plan Flyover tile coordinates for an arbitrary WGS84 bounding box. No network calls."""
import argparse, json, math
from pathlib import Path
def xy(lat,lon,z):
    n=1<<z
    lat=max(-85.0511287,min(85.0511287,lat))
    x=math.floor((lon+180.)/360.*n)
    y=math.floor((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
    return max(0,min(n-1,x)),max(0,min(n-1,y))
def bbox(centerlat,centerlon,radius):
    latdiff=radius/111320
    londiff=radius/(111320*max(0.01,math.cos(math.radians(centerlat))))
    return [centerlat-latdiff,centerlon-londiff,centerlat+latdiff,centerlon+londiff]
def generate(south,west,north,east,z):
    if not (-90<=south<=north<=90 and -180<=west<=east<=180):
        raise ValueError("Invalid bounding box or antimeridian crossing")
    lo,top=xy(north,west,z)
    hi,bottom=xy(south,east,z)
    out=[]
    for y in range(top,bottom+1):
      for x in range(lo,hi+1):
       out.append(dict(x=x,y=y,z=z))
    return out
p=argparse.ArgumentParser()
p.add_argument('--lat',type=float,required=True)
p.add_argument('--lon',type=float,required=True)
p.add_argument('--radius-m',type=float,default=100)
p.add_argument('--zoom',type=int,default=20)
p.add_argument('--max-tiles',type=int,default=1000)
p.add_argument('--output',default='tile_plan.json')
a=p.parse_args()
if a.radius_m<=0 or not 0<=a.zoom<=22: p.error("radius must be positive, zoom between 0 and 22")
area=bbox(a.lat,a.lon,a.radius_m)
tiles=generate(*area,a.zoom)
if len(tiles)>a.max_tiles:p.error(f"Tile count {len(tiles)} exceeds max {a.max_tiles}")
def parents(z):
   if a.zoom<z:return []
   r={(t['x']>>(a.zoom-z),t['y']>>(a.zoom-z)) for t in tiles}
   return [dict(x=x,y=y,z=z) for x,y in sorted(r)]
result=dict(center=[a.lat,a.lon],radius_m=a.radius_m,bbox_swen=area,zoom=a.zoom,
  layers={'style98_3d_h0':tiles,'style98_3d_h1_optional':tiles,
          'style100_metadata_z13':parents(13),'style100_root_z9':parents(9),
          'style99_height_z14':parents(14),
          'style98_context_z19':parents(19),'style98_context_z18':parents(18)},
  notes=['Plan only; style 98 existence and h=1 are not established for arbitrary tiles.',
  'Metadata availability and new-region version/authentication need separate verification.',
  'No requests are made by this script.'])
out=Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'bbox':area,'counts':{k:len(v) for k,v in result['layers'].items()},'first':tiles[:3]},indent=2))
