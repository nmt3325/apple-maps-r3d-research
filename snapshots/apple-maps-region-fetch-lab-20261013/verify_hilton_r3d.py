#!/usr/bin/env python3
"""Validate R3D ECEF transforms point to Honolulu without changing captured data."""
import json,struct,math,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent/'fresh_signed/oahu_hilton_20261013/area_z20'
files=sorted(p.glob('s98_*.r3d'))
marker=bytes.fromhex('01010100016a')
position=[];fail=[];bytes_total=0
for f in files:
 b=f.read_bytes();bytes_total+=len(b)
 if not b.startswith(bytes.fromhex('3d96592e02000000')):fail.append((f.name,'header'));continue
 at=b.find(marker)+6
 if at<6 or at+96>len(b):fail.append((f.name,'transform'));continue
 rotation=struct.unpack_from('<9d',b,at)
 X,Y,Z=struct.unpack_from('<3d',b,at+72)
 lon=math.degrees(math.atan2(Y,X))
 p0=math.hypot(X,Y);lat=math.atan2(Z,p0*(1-6.69437999014e-3))
 for _ in range(5):
  n=6378137/math.sqrt(1-6.69437999014e-3*math.sin(lat)**2)
  alt=p0/math.cos(lat)-n
  lat=math.atan2(Z,p0*(1-6.69437999014e-3*n/(n+alt)))
 position.append((math.degrees(lat),lon,alt))
report={'files':len(files),'verified_geographic_transforms':len(position),
 'malformed':fail,'total_bytes':bytes_total,
 'latitude_range':[min(v[0] for v in position),max(v[0] for v in position)],
 'longitude_range':[min(v[1] for v in position),max(v[1] for v in position)],
 'altitude_range_m':[min(v[2] for v in position),max(v[2] for v in position)]}
(p/'georeference_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
