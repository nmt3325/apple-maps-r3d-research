#!/usr/bin/env python3
"""Georeference independently recovered TRICO 12-bit Splat XYZ lower-bound anchors.

GeoJSON output is ONE marker per *tile* with identifiable XYZ lower-bound anchor,
not a decoded Splat point cloud. Requires no macOS/iOS or proprietary library.
"""
import argparse,json,math
from pathlib import Path
from nativefree_r3d_codec_streams import dissect
from nativefree_extract_heic import metadata
ESQ=6.69437999014e-3
EQUATORIAL=6378137.

def ecef_to_geodetic(x,y,z):
    lon=math.atan2(y,x);p=math.hypot(x,y)
    lat=math.atan2(z,p*(1-ESQ))
    for _ in range(8):
        rn=EQUATORIAL/math.sqrt(1-ESQ*math.sin(lat)**2)
        alt=p/math.cos(lat)-rn
        lat=math.atan2(z,p*(1-ESQ*rn/(rn+alt)))
    rn=EQUATORIAL/math.sqrt(1-ESQ*math.sin(lat)**2)
    alt=p/math.cos(lat)-rn
    return math.degrees(lon),math.degrees(lat),alt

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    files=sorted(args.input.glob('*.r3d')) if args.input.is_dir() else [args.input]
    features=[];skipped=[]
    for file in files:
        b=file.read_bytes()
        s=dissect(b)['splatStream'];anchor=s['blocks'][0]['lowerAnchorXYZMeters']
        if anchor is None:
            skipped.append(file.name)
            continue
        meta=metadata(b)
        R=meta['matrixR3x3']
        T=meta['ecefTranslation']
        vec=[T[axis]+sum(R[3*axis+j]*anchor[j] for j in range(3)) for axis in range(3)]
        lon,lat,alt=ecef_to_geodetic(*vec)
        if not all(math.isfinite(v) for v in (lon,lat,alt)):
            raise ValueError(f'Invalid geodetic anchor in {file.name}')
        features.append({'type':'Feature',
                         'properties':{
                           'sourceTile':file.name,
                           'meaning':'Quantized coordinate lower anchor of compressed Splat block, NOT splat point',
                           'splatCountFromHeader':s['pointCount'],
                           'originalXYZLowerAnchorMeters':anchor},
                         'geometry':{'type':'Point','coordinates':[round(lon,9),round(lat,9),round(alt,3)]}})
    result={'type':'FeatureCollection','name':'R3D-v2-nativefree-tile-XYZ-lower-anchors',
            'note':'One lower XYZ anchor per supported compressed tile. These are NOT pointcloud vertices or true mesh geometries.',
            'tilesScanned':len(files),'features':features,'skippedTilesNot12Bit':skipped}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False))
    if not features:raise ValueError('No compressed coordinate anchors found')
    print(json.dumps({'output':str(args.out),'tiles':len(files),'coordinatesDecoded':len(features),
                      'skipped':len(skipped),'first':features[0]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
