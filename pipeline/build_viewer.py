"""Build a portable hybrid viewer from the independent decoder's full arrays."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import time

import numpy as np
import pillow_heif
from PIL import Image

from geography import origin_frame, world_positions, world_normals

REPO = Path(__file__).resolve().parents[1]


def read_array(directory, manifest, name, dtype, channels=1):
    data = (directory / name).read_bytes()
    expected = manifest['arrays'][name]
    if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
        raise ValueError(f'Independent array integrity mismatch: {name}')
    array = np.frombuffer(data, dtype=dtype)
    if array.size % channels:
        raise ValueError(f'Independent array shape mismatch: {name}')
    return array.reshape(-1, channels) if channels > 1 else array


def build_viewer(decoded, output, lat, lon, title='R3D · 3D explorer'):
    pillow_heif.register_heif_opener()
    manifest = json.loads((decoded/'manifest.json').read_text())
    if manifest.get('decoder') != 'independent-python' or manifest.get('nativeGoldenInput') is not False:
        raise ValueError('Require outputs of the independent decoder')
    frame = origin_frame(lat, lon)
    output.mkdir(parents=True, exist_ok=True)
    (output/'data').mkdir(exist_ok=True)
    (output/'textures').mkdir(exist_ok=True)
    (output/'vendor').mkdir(exist_ok=True)
    node = REPO/'viewer/node_modules/three'
    vendor = {'three.module.js':node/'build/three.module.js',
              'three.core.js':node/'build/three.core.js',
              'OrbitControls.js':node/'examples/jsm/controls/OrbitControls.js',
              'THREE-LICENSE':node/'LICENSE'}
    for name, source in vendor.items():
        if not source.is_file():
            raise ValueError('Run npm ci in viewer/ before building a viewer')
        shutil.copyfile(source, output/'vendor'/name)
    leaflet = REPO/'viewer/node_modules/leaflet'
    leaflet_vendor = output/'vendor/leaflet'
    leaflet_vendor.mkdir(exist_ok=True)
    for name in ('leaflet.js','leaflet.css'):
        shutil.copyfile(leaflet/'dist'/name,leaflet_vendor/name)
    shutil.copytree(leaflet/'dist/images',leaflet_vendor/'images',dirs_exist_ok=True)
    shutil.copyfile(leaflet/'LICENSE',leaflet_vendor/'LICENSE')
    for name in ('index.html', 'app.js', 'stream-planner.mjs', 'stream-controller.mjs', 'stream-scene.mjs'):
        shutil.copyfile(REPO/'viewer/independent'/name, output/name)
    bounds_min = np.full(3, np.inf)
    bounds_max = np.full(3, -np.inf)
    tiles = []
    started = time.monotonic()
    for i, tile in enumerate(manifest['results']):
        directory = decoded/tile['directory']
        stored = json.loads((directory/'tile.json').read_text())
        if stored['sourceSHA256'] != tile['sourceSHA256']:
            raise ValueError('Decoded manifest/source hash mismatch')
        local = read_array(directory, tile, 'mesh-xyz-f32le.bin', '<f4', 3)
        uv = read_array(directory, tile, 'mesh-uv-f32le.bin', '<f4', 2)
        normals = read_array(directory, tile, 'mesh-normals-f32le.bin', '<f4', 3)
        ip = read_array(directory, tile, 'mesh-position-indices-u32le.bin', '<u4')
        iu = read_array(directory, tile, 'mesh-uv-indices-u32le.bin', '<u4')
        inn = read_array(directory, tile, 'mesh-normal-indices-u32le.bin', '<u4')
        if len(ip) != len(iu) or len(ip) != len(inn) or len(ip) != 3*tile['meshTriangles']:
            raise ValueError('Mesh index shape mismatch')
        if len(ip) and (ip.max() >= len(local) or iu.max() >= len(uv) or inn.max() >= len(normals)):
            raise ValueError('Mesh index out of range')
        world = world_positions(local, tile['georeference'], frame)
        transformed_normals = world_normals(normals, tile['georeference'], frame)
        unique, inverse = np.unique(np.column_stack([ip, iu, inn]), axis=0, return_inverse=True)
        vertices = world[unique[:,0]].astype('<f4')
        texture_uv = uv[unique[:,1]].astype('<f4')
        vertex_normals = transformed_normals[unique[:,2]].astype('<f4')
        indices = inverse.astype('<u4')
        splat_local = read_array(directory, tile, 'splat-xyz-f32le.bin', '<f4', 3)
        splat_world = world_positions(splat_local, tile['georeference'], frame).astype('<f4')
        material = read_array(directory, tile, 'splat-material20.bin', 'u1', 20)
        if len(splat_world) != 3*len(material) or len(material) != tile['splatRecords']:
            raise ValueError('Splat triangle/material shape mismatch')
        if not all(np.isfinite(a).all() for a in (vertices, texture_uv, vertex_normals, splat_world)):
            raise ValueError('Nonfinite viewer geometry')
        stem = f'tile-{i:04d}'
        geometry_name = 'data/'+stem+'.mesh.bin'
        splat_name = 'data/'+stem+'.splats.bin'
        texture_name = 'textures/'+stem+'.png'
        geometry = struct.pack('<4I', 0x56334452, 1, len(unique), tile['meshTriangles'])
        geometry += vertices.tobytes()+texture_uv.tobytes()+vertex_normals.tobytes()+indices.tobytes()
        splats = struct.pack('<4I', 0x53534452, 1, len(material), 0)
        splats += splat_world.tobytes()+material[:,:4].tobytes()
        (output/geometry_name).write_bytes(geometry)
        (output/splat_name).write_bytes(splats)
        if tile['meshTriangles']:
            atlas = (directory/'atlas-0.heic').read_bytes()
            if hashlib.sha256(atlas).hexdigest() != tile['arrays']['atlas-0.heic']['sha256']:
                raise ValueError('Original HEIC integrity mismatch')
            with Image.open(directory/'atlas-0.heic') as image:
                if list(image.size) != tile['atlasDimensions']:
                    raise ValueError('HEIC decoded dimensions differ from UV atlas dimensions')
                image.convert('RGB').save(output/texture_name)
        else:
            texture_name=None
        both = np.concatenate([world, splat_world])
        bounds_min = np.minimum(bounds_min, both.min(axis=0))
        bounds_max = np.maximum(bounds_max, both.max(axis=0))
        tiles.append({'source':tile['source'], 'sourceSHA256':tile['sourceSHA256'],
                      'mesh':geometry_name, 'splats':splat_name, 'texture':texture_name,
                      'vertices':len(unique), 'triangles':tile['meshTriangles'],
                      'splatRecords':len(material),
                      'visibleSplatRecords':int(np.count_nonzero(material[:,3])),
                      'atlasDimensions':tile['atlasDimensions']})
        print(f"prepared {i+1}/{manifest['tiles']} {tile['source']}", flush=True)
    result = {'schemaVersion':1, 'title':title, 'origin':[lat,lon,0],
              'frame':'meters: east, up, south; original R3D local -> ECEF -> shared ENU',
              'decoder':'independent-python', 'nativeGoldenInput':False,
              'tiles':tiles, 'bounds':{'min':bounds_min.tolist(),'max':bounds_max.tolist()},
              'totals':{'tiles':len(tiles),'meshTriangles':sum(t['triangles'] for t in tiles),
                        'splatRecords':sum(t['splatRecords'] for t in tiles),
                        'visibleSplatRecords':sum(t['visibleSplatRecords'] for t in tiles)},
              'textureConversion':'Original HEIC -> RGB PNG via Linux libheif/pillow-heif; UV flipY=true in browser',
              'additionalGoals':'Official pixel parity, exact LOD, native accumulation/color transfer remain unverified',
              'splatCompositing':'Original triangle geometry and packed RGBA; approximate barycentric alpha',
              'elapsedSeconds':round(time.monotonic()-started,3)}
    (output/'scene.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('decoded', type=Path)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--title', default='R3D · 3D explorer')
    args = parser.parse_args()
    result = build_viewer(args.decoded, args.out_dir, args.lat, args.lon, args.title)
    print(json.dumps({'output':str(args.out_dir), 'totals':result['totals']}, indent=2))


if __name__ == '__main__':
    main()
