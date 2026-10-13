"""Linux-only R3D v2 decoder: original textured polygon arrays and Splat soup."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import struct
import sys
import time

from nativefree_soup import decode_soup
from nativefree_splat_material import pack_material20
from nativefree_mesh import decode_mesh
from nativefree_extract_heic import find_heic_payloads, metadata
from nativefree_validate import validate_arrays


def decode_file(task):
    source, output = task
    raw = source.read_bytes()
    soup = decode_soup(raw)
    mesh = decode_mesh(raw)
    validation = validate_arrays(soup, mesh)
    images = find_heic_payloads(raw)
    parts = {
        'splat-xyz-f32le.bin': soup.xyz_f32,
        'splat-attributes-f32le.bin': soup.attributes_f32,
        'splat-material20.bin': pack_material20(soup.attributes_f32),
        'mesh-xyz-f32le.bin': mesh['positions_f32'],
        'mesh-uv-f32le.bin': mesh['uv_f32'],
        'mesh-normals-f32le.bin': mesh['normals_f32'],
    }
    for key, name in [('faces', 'position-indices'), ('uv_indices', 'uv-indices'),
                       ('normal_indices', 'normal-indices'), ('face_materials', 'face-materials')]:
        parts[f'mesh-{name}-u32le.bin'] = struct.pack('<' + 'I' * len(mesh[key]), *mesh[key])
    for i, (_, image, _) in enumerate(images):
        parts[f'atlas-{i}.heic'] = image
    transform = metadata(raw)
    manifest = {
        'source': source.name, 'sourceSHA256': hashlib.sha256(raw).hexdigest(),
        'decoder': 'independent-python', 'schemaVersion': 1,
        'splatRecords': soup.count, 'splatVertices': 3 * soup.count,
        'splatAttributesPerRecord': 8,
        'meshPositions': mesh['vertices'], 'meshUVs': mesh['uvCount'],
        'meshNormals': mesh['normalCount'], 'meshTriangles': mesh['faceCount'],
        'atlasDimensions': mesh['atlasDimensions'], 'georeference': transform,
        'missingValue': '0x7fc00000 canonical NaN, encoded delta -1; RGB missing values pack to zero',
        'normalMath': 'Float32 intermediate arithmetic, paired sine/cosine via Python math; Tokyo audit explains <=1 ULP native differences',
        'validation': validation,
        'arrays': {name: {'bytes': len(part), 'sha256': hashlib.sha256(part).hexdigest()}
                   for name, part in parts.items()},
    }
    directory = output / source.stem
    directory.mkdir(parents=True, exist_ok=True)
    for name, part in parts.items():
        temporary = directory / (name + '.tmp')
        temporary.write_bytes(part)
        temporary.replace(directory / name)
    temporary = directory / 'tile.json.tmp'
    temporary.write_text(json.dumps(manifest, indent=2) + '\n')
    temporary.replace(directory / 'tile.json')
    return {'tile': source.name, 'directory': directory.name, **manifest}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=1)
    args = ap.parse_args()
    files = sorted(args.input.glob('*.r3d')) if args.input.is_dir() else [args.input]
    if not files or not 1 <= args.workers <= 32:
        ap.error('Require R3D input files and 1..32 workers')
    args.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(decode_file, [(p, args.out_dir) for p in files]):
            rows.append(row)
            print(f"decoded {len(rows)}/{len(files)} {row['tile']} "
                  f"Splat={row['splatRecords']} polygon={row['meshTriangles']}", flush=True)
    report = {'schemaVersion': 1, 'decoder': 'independent-python',
              'nativeRuntimeInvoked': False, 'nativeGoldenInput': False,
              'tiles': len(rows), 'command': sys.argv,
              'elapsedSeconds': round(time.monotonic() - started, 3),
              'splatRecords': sum(x['splatRecords'] for x in rows),
              'meshTriangles': sum(x['meshTriangles'] for x in rows),
              'results': rows}
    (args.out_dir / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, indent=2))


if __name__ == '__main__':
    main()
