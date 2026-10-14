"""Linux coordinate -> R3D acquisition -> independent decoding -> hybrid viewer."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
from acquisition import plan_area, tile_name, load_config, fetch_area
from build_viewer import build_viewer
from export_scene import export
from geography import origin_frame

REPO = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lat',type=float,required=True);ap.add_argument('--lon',type=float,required=True)
    ap.add_argument('--radius-m',type=float,required=True);ap.add_argument('--zoom',type=int,default=20)
    ap.add_argument('--max-tiles',type=int,default=4096);ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--config',type=Path,default=os.environ.get('R3D_FETCH_CONFIG'))
    ap.add_argument('--source-dir',type=Path,help='Offline raw-R3D source, selects planned coordinates; no native output')
    ap.add_argument('--refresh',action='store_true');ap.add_argument('--export',action='store_true')
    ap.add_argument('--serve',action='store_true');ap.add_argument('--port',type=int,default=8973)
    args = ap.parse_args()
    plan = plan_area(args.lat,args.lon,args.radius_m,args.zoom,args.max_tiles)
    if not args.source_dir and not args.config: ap.error('Live acquisition requires --config or R3D_FETCH_CONFIG')
    output = args.out_dir.resolve();output.mkdir(parents=True,exist_ok=True)
    raw = output/'raw';raw.mkdir(exist_ok=True)
    expected = {tile_name(c) for c in plan['tiles']}
    if set(p.name for p in raw.glob('*.r3d'))-expected: raise ValueError('Output raw directory contains a different area; choose a fresh out-dir')
    (output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    report = {'schemaVersion':1,'plan':plan,'nativeRuntimeInvoked':False,'nativeGoldenInput':False,'steps':[],
              'mode':'offline-original-R3D' if args.source_dir else 'live-Linux-HTTPS','startedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    started = time.monotonic()
    try:
        if args.source_dir:
            for coord in plan['tiles']:
                name = tile_name(coord);source = args.source_dir/name
                if not source.is_file(): raise ValueError(f'Offline original tile unavailable: {name}')
                shutil.copyfile(source,raw/name)
            report['steps'].append({'step':'original-input-selection','tiles':len(expected),'pass':True})
        else:
            fetched = fetch_area(plan,load_config(args.config),raw,refresh=args.refresh)
            report['steps'].append({'step':'fetch','tiles':len(fetched['files']),'freshResponses':fetched['freshResponses'],'pass':True})
        command = [sys.executable,str(REPO/'codec/nativefree_decode_r3d.py'),str(raw),'--out-dir',str(output/'decoded'),'--workers',str(args.workers)]
        with (output/'decode.log').open('w') as log:
            code = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT).returncode
        report['steps'].append({'step':'independent-decode','exitCode':code,'log':'decode.log','pass':code==0})
        if code: raise RuntimeError('Independent decoder rejected input; see decode.log')
        decoded_manifest = json.loads((output/'decoded/manifest.json').read_text())
        rows = {r['source']:r for r in decoded_manifest['results']}
        maximum = 0.0
        for coord in plan['tiles']:
            n = 1<<coord['z'];lon = (coord['x']+.5)/n*360-180
            lat = math.degrees(math.atan(math.sinh(math.pi*(1-2*(coord['y']+.5)/n))))
            expected_origin,_ = origin_frame(lat,lon)
            actual_origin = np.array(rows[tile_name(coord)]['georeference']['ecefTranslation'])
            error = float(np.linalg.norm(actual_origin-expected_origin));maximum = max(maximum,error)
            if error>.5: raise ValueError('R3D georeference does not match requested tile center (0.5 meter tolerance)')
        report['steps'].append({'step':'requested-coordinate-check','tiles':len(rows),'maxECEFOriginErrorMeters':maximum,'toleranceMeters':.5,'pass':True})
        viewer = build_viewer(output/'decoded',output/'viewer',args.lat,args.lon)
        report['steps'].append({'step':'hybrid-viewer','counts':viewer['totals'],'pass':True})
        if args.export:
            exported = export(output/'viewer',output/'decoded',output/'export')
            report['steps'].append({'step':'GLB/PLY','outputs':exported['outputs'],'pass':True})
        report['pass'] = True
    except Exception as error:
        report['pass'] = False;report['error'] = {'type':type(error).__name__,'message':str(error)}
        raise
    finally:
        report['elapsedSeconds'] = round(time.monotonic()-started,3)
        (output/'run.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'viewer':str(output/'viewer'),'tiles':len(expected),'runReport':str(output/'run.json')},indent=2),flush=True)
    if args.serve:
        print(f'Open http://127.0.0.1:{args.port}/',flush=True)
        subprocess.run([sys.executable,'-m','http.server',str(args.port),'--bind','127.0.0.1','--directory',str(output/'viewer')],check=True)

if __name__=='__main__':main()
