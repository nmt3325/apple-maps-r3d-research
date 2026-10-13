"""Full soup array comparison with saved native goldens; no Apple code runs."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'codec'))
from nativefree_soup import decode_soup
from nativefree_splat_material import pack_material20


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compare(actual: bytes, expected: bytes) -> dict:
    if len(actual) != len(expected) or len(actual) % 4:
        raise ValueError("Array byte length mismatch")
    result = {'floatCount': len(actual) // 4, 'bitMismatches': 0,
              'maxAbsoluteError': 0.0, 'nonFinite': 0, 'matchingNaNSentinels': 0,
              'unexpectedNonFinite': 0, 'maxULP': 0,
              'actualSHA256': sha(actual), 'goldenSHA256': sha(expected),
              'examples': []}
    for i, (a, b) in enumerate(zip(struct.iter_unpack('<I', actual),
                                 struct.iter_unpack('<I', expected))):
        av = struct.unpack('<f', struct.pack('<I', a[0]))[0]
        bv = struct.unpack('<f', struct.pack('<I', b[0]))[0]
        if not math.isfinite(av) or not math.isfinite(bv):
            result['nonFinite'] += 1
            if a[0] == b[0] == 0x7fc00000:
                result['matchingNaNSentinels'] += 1
            else:
                result['unexpectedNonFinite'] += 1
        if a != b:
            result['bitMismatches'] += 1
            result['maxAbsoluteError'] = max(result['maxAbsoluteError'], abs(av - bv))
            if math.isfinite(av) and math.isfinite(bv):
                ordered_a = 0x80000000 - (a[0] & 0x7fffffff) if a[0] >> 31 else 0x80000000 + a[0]
                ordered_b = 0x80000000 - (b[0] & 0x7fffffff) if b[0] >> 31 else 0x80000000 + b[0]
                result['maxULP'] = max(result['maxULP'], abs(ordered_a - ordered_b))
            if len(result['examples']) < 4:
                result['examples'].append({'index': i, 'actual': av, 'golden': bv,
                                          'actualBits': hex(a[0]), 'goldenBits': hex(b[0])})
    return result


def one(task: tuple[Path, Path]) -> dict:
    path, golden_dir = task
    raw = path.read_bytes()
    row = {'tile': path.name, 'inputSHA256': sha(raw)}
    try:
        result = decode_soup(raw)
        decoded = (golden_dir / (path.name + '.decoded')).read_bytes()
        triangles = (golden_dir / (path.name + '.native-triangle-f32')).read_bytes()
        header = struct.unpack_from('<4I', decoded)
        if header != (0x31443352, result.count, 8, 0):
            raise ValueError("Native golden header/count mismatch")
        if len(decoded) != 16 + 44 * result.count:
            raise ValueError("Native golden length mismatch")
        if decoded[16:16 + 12 * result.count] != triangles[:12 * result.count]:
            raise ValueError("Native .decoded positions differ from full triangle prefix")
        row['records'] = result.count
        row['origins'] = result.origins
        row['triangles'] = compare(result.xyz_f32, triangles)
        row['attributes'] = compare(result.attributes_f32, decoded[16 + 12 * result.count:])
        packed = pack_material20(result.attributes_f32)
        material = (golden_dir / (path.name + '.native-material20')).read_bytes()
        if len(packed) != len(material):
            raise ValueError("Material byte length mismatch")
        row['material'] = {'bytes': len(packed),
                           'byteMismatches': sum(a != b for a, b in zip(packed, material)),
                           'actualSHA256': sha(packed), 'goldenSHA256': sha(material)}
        row['status'] = 'exact' if all(
            row[k]['bitMismatches'] == row[k]['unexpectedNonFinite'] == 0
            for k in ('triangles', 'attributes')) else 'mismatch'
        if row['triangles']['nonFinite']:
            row['status'] = 'mismatch'
        if row['material']['byteMismatches']:
            row['status'] = 'mismatch'
    except Exception as error:
        row['status'] = 'error'
        row['error'] = f'{type(error).__name__}: {error}'
    return row


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('r3d_dir', type=Path)
    ap.add_argument('golden_dir', type=Path)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    files = sorted(args.r3d_dir.glob('*.r3d'))
    if not files:
        ap.error('No R3D input files')
    if args.limit:
        files = files[:args.limit]
    started = time.monotonic()
    tasks = [(path, args.golden_dir) for path in files]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(one, tasks):
            rows.append(row)
            if len(rows) % 10 == 0 or row['status'] == 'error':
                print(f"{len(rows)}/{len(files)} {row['tile']} {row['status']} "
                      f"{row.get('error', '')}", flush=True)
    report = {
        'scope': 'All TRICO soup triangle XYZ, eight attributes and packed RGBA/material20; polygon mesh tested separately',
        'nativeRuntimeInvoked': False, 'goldensUsedOnlyForComparison': True,
        'tiles': len(rows), 'exactTiles': sum(r['status'] == 'exact' for r in rows),
        'mismatchTiles': sum(r['status'] == 'mismatch' for r in rows),
        'errors': sum(r['status'] == 'error' for r in rows),
        'elapsedSeconds': round(time.monotonic() - started, 3),
        'command': sys.argv,
        'implementationSHA256': {
            p.name: sha(p.read_bytes()) for p in
            (Path(__file__).resolve().parents[1] / 'codec').glob('*.py')},
        'arrays': {}, 'results': rows,
    }
    for key in ('triangles', 'attributes'):
        report['arrays'][key] = {
            field: sum(r.get(key, {}).get(field, 0) for r in rows)
            for field in ('floatCount', 'bitMismatches', 'nonFinite',
                          'matchingNaNSentinels', 'unexpectedNonFinite')}
    report['arrays']['material'] = {
        field: sum(r.get('material', {}).get(field, 0) for r in rows)
        for field in ('bytes', 'byteMismatches')}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ('results', 'implementationSHA256')}, indent=2))
    if report['errors'] or report['mismatchTiles']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
