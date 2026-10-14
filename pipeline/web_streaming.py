"""Bounded, deduplicated server-side Apple acquisition and per-tile preparation.

Only validated display arrays and converted textures are exposed to the browser.
Signing configuration and raw Apple responses remain outside the static root.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import io
import json
import math
import multiprocessing
import os
from pathlib import Path
import shutil
import struct
import sys
import threading
import time
from urllib.error import HTTPError, URLError
import uuid

import numpy as np
from PIL import Image
import pillow_heif

from acquisition import load_config, response_body, tile_name
from build_viewer import read_array
from geography import origin_frame

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'codec'))
from c3mm_v2_parser import parse as parse_index
from nativefree_decode_r3d import decode_file

ASSETS = {'mesh.bin', 'splats.bin', 'texture.png'}
TTL = 3600
EMPTY_TTL = 60
FAILURE_TTL = 20


def coordinates(value):
    """Accept only researched tile coordinates, never browser-supplied URLs."""
    if not isinstance(value, dict):
        raise ValueError('Invalid tile')
    fields = {name: value.get(name, default) for name, default in [('style', 98), ('z', None), ('x', None), ('y', None), ('h', 0)]}
    if any(type(v) is not int for v in fields.values()):
        raise ValueError('Tile coordinates must be integers')
    s, z, x, y, h = (fields[k] for k in ('style', 'z', 'x', 'y', 'h'))
    if not (s == 98 and 18 <= z <= 20 or s == 100 and z == 13 and h == 0):
        raise ValueError('Unsupported style/zoom')
    if not (0 <= x < 1 << z and 0 <= y < 1 << z and 0 <= h < 1 << z):
        raise ValueError('Tile coordinate outside bounds')
    return fields


def expand_heights(index, tile):
    """All LODs use the service's z13 index containing z17 occupied cells."""
    tile = coordinates(tile)
    z, x, y = (tile[k] for k in ('z', 'x', 'y'))
    expected = {'z': 13, 'x': x >> (z - 13), 'y': y >> (z - 13)}
    if index['tile'] != expected:
        raise ValueError('Index coordinates do not match tile')
    factor = 1 << (z - 17)
    local_x, local_y = x // factor % 16, 15 - y // factor % 16
    heights = sorted({factor * cell[2] + child for cell in index['cells']
                      if cell[0] == local_x and cell[1] == local_y for child in range(factor)})
    if len(heights) > 384:
        raise ValueError('Height candidate limit exceeded')
    return [{**tile, 'h': h} for h in heights]


def fetch_response(config, tile):
    for attempt in range(3):
        try:
            body = response_body(config, tile)
            if not body and tile['style'] == 100:
                raise ValueError('Missing height index')
            return body
        except HTTPError as error:
            if tile['style'] == 98 and error.code in (404, 204):
                return b''
            if error.code in (401, 403):
                raise PermissionError('Apple authentication failed') from None
            if (error.code == 429 or error.code >= 500) and attempt < 2:
                try:
                    delay = float(error.headers.get('Retry-After', 2 ** (attempt + 1)))
                except (TypeError, ValueError):
                    delay = 2 ** (attempt + 1)
                time.sleep(min(20, max(1, delay)))
                continue
            raise RuntimeError(f'Apple HTTP {error.code}') from None
    raise RuntimeError('Apple request failed')


def prepare_display(raw, tile, directory):
    """Reuse the audited decoder; retain local float32 arrays and a double transform."""
    source = directory / tile_name(tile)
    source.write_bytes(raw)
    row = decode_file((source, directory / 'decoded'))
    if row['meshTriangles'] > 500_000 or row['splatRecords'] > 500_000:
        raise ValueError('Tile geometry budget exceeded')
    decoded = directory / 'decoded' / row['directory']
    transform = row['georeference']
    n = 1 << tile['z']
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (tile['y'] + .5) / n))))
    lon = (tile['x'] + .5) / n * 360 - 180
    error = float(np.linalg.norm(np.array(transform['ecefTranslation']) - origin_frame(lat, lon)[0]))
    if error > .5:
        raise ValueError('R3D coordinates do not match requested tile')
    xyz = read_array(decoded, row, 'mesh-xyz-f32le.bin', '<f4', 3)
    uv = read_array(decoded, row, 'mesh-uv-f32le.bin', '<f4', 2)
    normal = read_array(decoded, row, 'mesh-normals-f32le.bin', '<f4', 3)
    ip = read_array(decoded, row, 'mesh-position-indices-u32le.bin', '<u4')
    iu = read_array(decoded, row, 'mesh-uv-indices-u32le.bin', '<u4')
    inn = read_array(decoded, row, 'mesh-normal-indices-u32le.bin', '<u4')
    unique, inverse = np.unique(np.column_stack([ip, iu, inn]), axis=0, return_inverse=True)
    geometry = struct.pack('<4I', 0x56334452, 1, len(unique), row['meshTriangles'])
    geometry += xyz[unique[:, 0]].astype('<f4').tobytes()
    geometry += uv[unique[:, 1]].astype('<f4').tobytes()
    geometry += normal[unique[:, 2]].astype('<f4').tobytes() + inverse.astype('<u4').tobytes()
    splat_xyz = read_array(decoded, row, 'splat-xyz-f32le.bin', '<f4', 3)
    material = read_array(decoded, row, 'splat-material20.bin', 'u1', 20)
    splats = struct.pack('<4I', 0x53534452, 1, len(material), 0)
    splats += splat_xyz.tobytes() + material[:, :4].tobytes()
    public = directory / 'public'
    public.mkdir()
    (public / 'mesh.bin').write_bytes(geometry)
    (public / 'splats.bin').write_bytes(splats)
    texture_size = None
    if row['meshTriangles']:
        pillow_heif.register_heif_opener()
        with Image.open(decoded / 'atlas-0.heic') as image:
            if tuple(image.size) != tuple(row['atlasDimensions']):
                raise ValueError('Atlas dimensions mismatch')
            image = image.convert('RGB')
            image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            texture_size = list(image.size)
            image.save(public / 'texture.png')
    points = np.concatenate([xyz, splat_xyz])
    if not len(points) or not np.isfinite(points).all():
        raise ValueError('Missing or nonfinite geometry')
    result = {'tile': tile, 'source': source.name, 'sourceSHA256': row['sourceSHA256'],
              'transform': transform, 'bounds': {'min': points.min(axis=0).tolist(), 'max': points.max(axis=0).tolist()},
              'triangles': row['meshTriangles'], 'vertices': len(unique), 'splatRecords': len(material),
              'visibleSplatRecords': int(np.count_nonzero(material[:, 3])), 'textureSize': texture_size,
              'geometryBytes': len(geometry), 'splatBytes': len(splats), 'georeferenceErrorMeters': error}
    # Decoded intermediates are reproducible from the retained original.
    shutil.rmtree(directory / 'decoded')
    return result


def prepare_request(config_path, tile, destination):
    """Runs in a worker process so Python decoding never blocks the HTTP thread."""
    destination = Path(destination)
    temporary = destination.with_name('.' + destination.name + '-' + uuid.uuid4().hex)
    temporary.mkdir(parents=True)
    try:
        raw = fetch_response(load_config(config_path), tile)
        if tile['style'] == 100:
            sections, cells = parse_index(raw, True)
            header = next(s for s in sections if s['tag'] == 0)
            if header['decodedTile'] != {k: tile[k] for k in ('z', 'x', 'y')}:
                raise ValueError('Height index coordinates mismatch')
            result = {'tile': header['decodedTile'], 'cells': sorted(cells)}
            (temporary / 'raw.c3mm').write_bytes(raw)
            status = 'ready'
        elif raw:
            result = prepare_display(raw, tile, temporary)
            status = 'ready'
        else:
            result, status = None, 'empty'
        record = {'status': status, 'result': result, 'finished': time.time()}
        (temporary / 'result.json').write_text(json.dumps(record, separators=(',', ':')))
        if destination.exists():
            shutil.rmtree(destination)
        temporary.replace(destination)
        return record
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


class StreamCache:
    def __init__(self, config_path, root, workers=2, max_pending=8, budget=1024*1024*1024, worker=prepare_request, executor=None):
        self.config_path, self.root = Path(config_path), Path(root)
        config = load_config(config_path)
        self.namespace = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:24]
        self.directory = self.root / self.namespace
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.pool = executor or ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn'))
        self.max_pending, self.budget, self.worker = max_pending, budget, worker
        self.jobs, self.futures, self.sizes, self.touched = {}, {}, {}, {}
        self.auth_failed = False
        for path in self.directory.iterdir():
            if path.is_dir() and len(path.name) == 32 and (path / 'result.json').is_file():
                self.sizes[path.name] = sum(p.stat().st_size for p in path.rglob('*') if p.is_file())
                self.touched[path.name] = (path / 'result.json').stat().st_mtime
        self.trim()

    def key(self, tile):
        return hashlib.sha256((self.namespace + json.dumps(tile, sort_keys=True)).encode()).hexdigest()[:32]

    def state(self, job_id):
        with self.lock:
            state = self.jobs.get(job_id)
            if state:
                self.touched[job_id] = time.time()
                return {**state}
            return None

    def settle(self, job_id, timeout=.15):
        # Empty responses and cache hits should not pay a browser polling cycle.
        with self.lock:
            future = self.futures.get(job_id)
        if future:
            try:
                future.result(timeout=timeout)
            except Exception:
                pass  # The completion callback publishes a sanitized error.
        return self.state(job_id)

    def request(self, value):
        tile = coordinates(value)
        job_id = self.key(tile)
        with self.lock:
            now = time.time()
            state = self.jobs.get(job_id)
            if state and (job_id in self.futures or state.get('expires', 0) > now):
                self.touched[job_id] = now
                return {**state}
            if self.auth_failed:
                raise PermissionError('Apple authentication failed')
            path = self.directory / job_id
            if (path / 'result.json').is_file():
                try:
                    record = json.loads((path / 'result.json').read_text())
                    ttl = EMPTY_TTL if record['status'] == 'empty' else TTL
                    if record['finished'] + ttl > now:
                        return self.complete(job_id, tile, record, cached=True)
                except (ValueError, KeyError, OSError):
                    pass
            if len(self.futures) >= self.max_pending:
                raise BlockingIOError('Tile queue is full')
            self.trim()
            state = {'id': job_id, 'tile': tile, 'status': 'queued', 'expires': now + TTL}
            self.jobs[job_id] = state
            self.touched[job_id] = now
            future = self.pool.submit(self.worker, self.config_path, tile, path)
            self.futures[job_id] = future
            future.add_done_callback(lambda f: self.finished(job_id, tile, f))
            return {**state}

    def complete(self, job_id, tile, record, cached=False):
        ttl = EMPTY_TTL if record['status'] == 'empty' else TTL
        state = {'id': job_id, 'tile': tile, **record, 'cached': cached, 'expires': record['finished'] + ttl}
        if tile['style'] == 98 and record['status'] == 'ready':
            result = dict(record['result'])
            base = f'/stream-assets/{self.namespace}/{job_id}/'
            version = '?v=' + result['sourceSHA256']
            result.update(mesh=base + 'mesh.bin' + version, splats=base + 'splats.bin' + version,
                          texture=base + 'texture.png' + version if result['textureSize'] else None)
            state['result'] = result
        self.jobs[job_id] = state
        self.touched[job_id] = time.time()
        return {**state}

    def finished(self, job_id, tile, future):
        with self.lock:
            try:
                record = future.result()
                self.complete(job_id, tile, record)
                self.sizes[job_id] = sum(p.stat().st_size for p in (self.directory / job_id).rglob('*') if p.is_file())
            except Exception as error:
                self.auth_failed = self.auth_failed or isinstance(error, PermissionError)
                if isinstance(error, PermissionError):
                    message = 'Apple Mapsの取得認証が失効しました。サーバーの取得設定を更新してください。'
                elif isinstance(error, RuntimeError) and str(error).startswith('Apple HTTP '):
                    message = str(error)
                else:
                    message = 'タイルの取得・復号に失敗しました。再試行するか場所を変えてください。'
                self.jobs[job_id] = {'id': job_id, 'tile': tile, 'status': 'failed', 'message': message,
                                     'authenticationFailed': self.auth_failed, 'expires': time.time() + FAILURE_TTL}
            finally:
                self.futures.pop(job_id, None)
                self.trim(protected={job_id})

    def trim(self, protected=frozenset()):
        """Bound retained originals, generated assets, and in-memory job records."""
        total = sum(self.sizes.values())
        now = time.time()
        for job_id in sorted(self.sizes, key=lambda key: self.touched.get(key, 0)):
            if job_id in protected or job_id in self.futures:
                continue
            if total <= self.budget and now - self.touched.get(job_id, 0) <= TTL:
                continue
            total -= self.sizes.pop(job_id)
            shutil.rmtree(self.directory / job_id, ignore_errors=True)
            self.jobs.pop(job_id, None)
            self.touched.pop(job_id, None)
        for job_id in list(self.jobs):
            if job_id not in self.futures and self.jobs[job_id].get('expires', 0) < now:
                self.jobs.pop(job_id, None)
        if len(self.jobs) > 4096:
            for job_id in sorted(self.jobs, key=lambda key: self.touched.get(key, 0)):
                if len(self.jobs) <= 4096:
                    break
                if job_id not in self.futures:
                    self.jobs.pop(job_id)
        # Do not keep expired empty/failure IDs forever as a camera travels.
        self.touched = {key: value for key, value in self.touched.items() if key in self.jobs or key in self.sizes}

    def asset(self, namespace, job_id, name):
        if namespace != self.namespace or name not in ASSETS or len(job_id) != 32 or any(c not in '0123456789abcdef' for c in job_id):
            return None
        with self.lock:
            path = self.directory / job_id / 'public' / name
            if not path.is_file():
                return None
            self.touched[job_id] = time.time()
            # Open under lock so a concurrent LRU eviction cannot race the open.
            return path.open('rb')

    def close(self):
        self.pool.shutdown(wait=True, cancel_futures=True)
