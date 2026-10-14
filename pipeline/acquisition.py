"""Coordinate planning and bounded Linux HTTPS acquisition with fresh signatures."""
from __future__ import annotations
import base64
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import secrets
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = bytes.fromhex('3d96592e02000000')
MERCATOR_LIMIT = 85.0511287798066
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'codec'))
from c3mm_v2_parser import parse as parse_height_index


def plan_area(lat, lon, radius, zoom=20, max_tiles=4096):
    if not all(math.isfinite(x) for x in (lat,lon,radius)) or not -MERCATOR_LIMIT <= lat <= MERCATOR_LIMIT or not -180 <= lon <= 180 or not 0 < radius <= 100000 or not 0 <= zoom <= 22:
        raise ValueError('Require finite Mercator lat/lon, radius 0..100000 meters and zoom 0..22')
    angle = radius/6378137.0
    south = max(-MERCATOR_LIMIT,lat-math.degrees(angle));north = min(MERCATOR_LIMIT,lat+math.degrees(angle))
    dlon = math.degrees(math.asin(min(1,math.sin(angle)/math.cos(math.radians(lat)))))
    n = 1<<zoom
    x0 = math.floor((lon-dlon+180)/360*n);x1 = math.floor((lon+dlon+180)/360*n)
    def y(p): return max(0,min(n-1,math.floor((1-math.asinh(math.tan(math.radians(p)))/math.pi)/2*n)))
    y0,y1 = y(north),y(south)
    count = min(n,x1-x0+1)*(y1-y0+1)
    if not 1 <= count <= max_tiles: raise ValueError(f'Planned {count} tiles exceeds max-tiles {max_tiles}')
    coords = [{'z':zoom,'x':x,'y':yy,'h':0} for x in sorted({xx%n for xx in range(x0,x1+1)}) for yy in range(y0,y1+1)]
    return {'center':[lat,lon],'radiusMeters':radius,'rangeMeaning':'Bounding square enclosing requested spherical radius; complete intersecting tiles',
            'zoom':zoom,'style':98,'tiles':coords,'boundsUnwrappedSWNE':[south,lon-dlon,north,lon+dlon],
            'lodSelection':'Explicit zoom; Apple exact LOD selection is an additional goal'}


def tile_name(coord):
    return 's98_z{z}_x{x}_y{y}_h{h}.r3d'.format(**coord)


def load_config(path):
    config = json.loads(Path(path).read_text())
    u = urlsplit(config['endpoint'])
    if u.scheme != 'https' or not u.hostname or u.query or u.fragment or u.username or u.password:
        raise ValueError('Signing endpoint must be HTTPS with no credentials/query/fragment')
    params = config['queryParameters']
    if not isinstance(params,list) or any(not isinstance(p,list) or len(p)!=2 or not all(isinstance(v,str) for v in p) for p in params):
        raise ValueError('queryParameters must be ordered string pairs')
    keys = [p[0] for p in params]
    if len(keys)!=len(set(keys)) or 'accessKey' in keys or not set(('x','y','z','h','style')).issubset(keys) or dict(params)['style']!='98':
        raise ValueError('Require style98 coordinate query without saved accessKey')
    if not isinstance(config['signingParts'],list) or len(config['signingParts'])!=2 or not all(isinstance(v,str) and v for v in config['signingParts']):
        raise ValueError('Require two locally supplied signing parts')
    return config


def signed_url(config, coord):
    endpoint = urlsplit(config['endpoint'])
    params = [(k,str(coord[k]) if k in coord else v) for k,v in config['queryParameters']]
    query = urlencode(params);uri = endpoint.path+'?'+query
    nonce = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16))
    expiration = int(time.time())+4200
    payload = (uri+str(expiration)+nonce).encode();padding = 16-len(payload)%16;payload += bytes([padding])*padding
    key = hashlib.sha256((''.join(config['signingParts'])+nonce).encode()).digest()
    cipher = Cipher(algorithms.AES(key),modes.CBC(bytes(16))).encryptor()
    encrypted = cipher.update(payload)+cipher.finalize()
    access = f'{expiration}_{nonce}_'+base64.b64encode(encrypted).decode()
    return urlunsplit((endpoint.scheme,endpoint.netloc,endpoint.path,query+'&accessKey='+quote(access,safe=''),''))


def response_body(config, coord):
    with urlopen(Request(signed_url(config,coord),headers=config.get('headers',{})),timeout=30) as response:
        body = response.read(3_000_001)
        if len(body)>3_000_000: raise ValueError('Response exceeds 3 MB limit')
        if body.startswith(b'\x1f\x8b'):
            with gzip.GzipFile(fileobj=io.BytesIO(body)) as compressed: body = compressed.read(16_000_001)
            if len(body)>16_000_000: raise ValueError('Expanded response exceeds 16 MB limit')
    return body


def discover_height_tiles(plan, config, output, max_candidates=32768, refresh=False):
    """Expand occupied C3MM coarse XYZ cells to every possible height at target z.

    This conservatively probes all eight vertical children, rather than assuming
    that an empty lower layer means the higher layers are empty too.
    """
    zoom=plan['zoom']
    if zoom<7: raise ValueError('Automatic height discovery requires zoom >= 7')
    output.mkdir(parents=True,exist_ok=True)
    horizontal=plan['tiles']
    index_zoom=zoom-7
    parents=sorted({(t['x']//128,t['y']//128) for t in horizontal})
    indices={};records=[]
    for x,y in parents:
        coord={'style':100,'z':index_zoom,'x':x,'y':y,'h':0}
        name=f's100_z{index_zoom}_x{x}_y{y}_h0.c3mm'
        path=output/name
        try:
            body=path.read_bytes() if path.is_file() and not refresh else response_body(config,coord)
            sections,cells=parse_height_index(body,True)
        except HTTPError as error:
            raise RuntimeError(f'Height index HTTP {error.code}; check coverage/configuration') from None
        except (URLError,TimeoutError,ValueError,OSError) as error:
            raise RuntimeError(f'Height index unavailable or invalid ({type(error).__name__})') from None
        header=next(s for s in sections if s['tag']==0)
        if header['decodedTile']!={'z':index_zoom,'x':x,'y':y}:
            raise ValueError('Height index coordinates do not match request')
        path.write_bytes(body)
        indices[x,y]=cells
        records.append({'file':name,'sha256':hashlib.sha256(body).hexdigest(),'cells':len(cells)})
    candidates=[]
    for tile in horizontal:
        cells=indices[tile['x']//128,tile['y']//128]
        local_x=(tile['x']//8)%16;local_y=15-(tile['y']//8)%16
        heights=sorted(h for x,y,h in cells if (x,y)==(local_x,local_y))
        for h in heights:
            for child in range(8):
                candidates.append({**tile,'h':8*h+child})
        if len(candidates)>max_candidates:
            raise ValueError(f'Height discovery exceeds {max_candidates} candidate requests; reduce area')
    if not candidates: raise ValueError('No indexed 3D coverage in requested area')
    discovery={'selection':'All vertical children of occupied C3MM coarse cells; empty responses omitted',
               'indexZoom':index_zoom,'coarseZoom':zoom-3,'targetZoom':zoom,
               'horizontalTileCount':len(horizontal),'candidateCount':len(candidates),'indexes':records}
    (output/'manifest.json').write_text(json.dumps(discovery,indent=2)+'\n')
    return {**plan,'horizontalTiles':horizontal,'heightDiscovery':discovery,'tiles':candidates}


def fetch_area(plan, config, output, delay=.4, refresh=False):
    output.mkdir(parents=True,exist_ok=True)
    empty_cache={}
    previous=output/'fetch.json'
    if previous.is_file() and plan.get('heightDiscovery') and not refresh:
        try:
            old=json.loads(previous.read_text())
            if old['plan'].get('heightDiscovery',{}).get('indexes')==plan['heightDiscovery']['indexes']:
                empty_cache={tuple(t['tile'][k] for k in ('z','x','y','h')):t for t in old.get('emptyTiles',[])}
        except (ValueError,KeyError,TypeError,OSError):pass
    report = {'requested':len(plan['tiles']),'files':[],'emptyTiles':[],'errors':[],'freshResponses':0,'cached':0,'cachedEmpty':0,
              'authentication':'Fresh per-request signatures; no saved signed URLs or access keys',
              'source':'Linux HTTPS; configured style/region/version template', 'plan':plan}
    try:
        for i,coord in enumerate(plan['tiles'],1):
            path = output/tile_name(coord)
            from_cache=path.is_file() and not refresh
            try:
                cached_empty=empty_cache.get(tuple(coord[k] for k in ('z','x','y','h')))
                if cached_empty and not path.is_file():
                    report['emptyTiles'].append(cached_empty);report['cachedEmpty']+=1
                    continue
                if from_cache:
                    body = path.read_bytes();report['cached']+=1
                else:
                    body = response_body(config,coord)
                    report['freshResponses']+=1
                if not body and plan.get('heightDiscovery'):
                    report['emptyTiles'].append({'tile':coord,'response':'HTTP 200/204 empty'})
                    continue
                if not body.startswith(MAGIC): raise ValueError('Response is not supported R3D v2')
                temporary = path.with_suffix('.r3d.tmp');temporary.write_bytes(body);temporary.replace(path)
                report['files'].append({'tile':coord,'file':path.name,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
                print(f'fetch {i}/{len(plan["tiles"])} {path.name} bytes={len(body)}',flush=True)
            except HTTPError as error:
                if error.code==404 and plan.get('heightDiscovery'):
                    report['emptyTiles'].append({'tile':coord,'response':'HTTP 404'})
                    continue
                report['errors'].append({'tile':coord,'httpStatus':error.code})
                raise RuntimeError(f'Acquisition HTTP {error.code}; check coverage and configured region/version/authentication') from None
            except (URLError,TimeoutError,ValueError,OSError) as error:
                report['errors'].append({'tile':coord,'errorType':type(error).__name__})
                raise RuntimeError(f'Acquisition failed ({type(error).__name__}); see fetch manifest') from None
            if delay>0 and not from_cache:
                time.sleep(delay)
        if not report['files']: raise RuntimeError('No nonempty R3D tiles in indexed area')
    finally:
        (output/'fetch.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
