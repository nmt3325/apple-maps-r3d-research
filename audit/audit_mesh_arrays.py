"""Compare every original polygon array and primary HEIC with Tokyo goldens."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import json
from pathlib import Path
import struct
import sys
import time

from audit_soup_arrays import compare, sha
from nativefree_mesh import decode_mesh
from nativefree_extract_heic import find_heic_payloads
from normal_math_evidence import explain


def one(task):
    path, golden = task
    raw = path.read_bytes()
    row = {'tile': path.name, 'inputSHA256': sha(raw)}
    try:
        result = decode_mesh(raw)
        arrays = {}
        for name, suffix in [('positions_f32', '2b0'), ('uv_f32', '2c8'),
                             ('normals_f32', '2e0')]:
            expected = (golden / f'{path.name}.c3m-{suffix}.bin').read_bytes()
            arrays[name] = compare(result[name], expected)
        for name, suffix in [('faces', '2f8'), ('uv_indices', '310'), ('normal_indices', '328')]:
            actual = struct.pack('<' + 'i' * len(result[name]), *result[name])
            expected = (golden / f'{path.name}.c3m-{suffix}.bin').read_bytes()
            if len(actual) != len(expected):
                raise ValueError(f'{name} length mismatch')
            arrays[name] = {'indexCount': len(actual) // 4,
                            'bitMismatches': sum(a != b for a, b in zip(
                                struct.iter_unpack('<I', actual), struct.iter_unpack('<I', expected))),
                            'actualSHA256': sha(actual), 'goldenSHA256': sha(expected)}
        image = find_heic_payloads(raw)[0][1]
        expected = (golden / (path.name + '.texture-0-0.heic')).read_bytes()
        arrays['texture'] = {'bytes': len(image), 'exact': image == expected,
                             'actualSHA256': sha(image), 'goldenSHA256': sha(expected)}
        row['arrays'] = arrays
        row['vertices'] = result['vertices']
        row['faces'] = result['faceCount']
        row['uvCount'] = result['uvCount']
        row['normalCount'] = result['normalCount']
        row['atlasDimensions'] = result['atlasDimensions']
        bad = [name for name, stats in arrays.items()
               if stats.get('bitMismatches', 0) or stats.get('nonFinite', 0) or stats.get('exact') is False]
        row['status'] = 'exact' if not bad else 'mismatch'
        row['differingArrays'] = bad
        if bad == ['normals_f32'] and arrays['normals_f32']['maxULP'] <= 1:
            expected = (golden / (path.name + '.c3m-2e0.bin')).read_bytes()
            row['normalRoundingEvidence'] = explain(result['normalWords'], result['steps'][2],
                                                    result['normals_f32'], expected)
            row['status'] = 'explained-normal-rounding'
    except Exception as error:
        row['status'] = 'error'
        row['error'] = f'{type(error).__name__}: {error}'
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('r3d_dir', type=Path)
    ap.add_argument('golden_dir', type=Path)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    files = sorted(args.r3d_dir.glob('*.r3d'))
    if not files:
        ap.error('No R3D inputs')
    if args.limit:
        files = files[:args.limit]
    started = time.monotonic()
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(one, [(p, args.golden_dir) for p in files]):
            rows.append(row)
            if len(rows) % 20 == 0 or row['status'] == 'error':
                print(f"{len(rows)}/{len(files)} {row['tile']} {row['status']} {row.get('error', '')}", flush=True)
    names = ('positions_f32', 'uv_f32', 'normals_f32', 'faces', 'uv_indices', 'normal_indices', 'texture')
    summary = {}
    for name in names:
        items = [r.get('arrays', {}).get(name, {}) for r in rows]
        summary[name] = {
            key: sum(s.get(key, 0) for s in items)
            for key in ('floatCount', 'indexCount', 'bitMismatches', 'nonFinite', 'bytes')}
        summary[name]['maxULP'] = max(s.get('maxULP', 0) for s in items)
        summary[name]['maxAbsoluteError'] = max(s.get('maxAbsoluteError', 0) for s in items)
        if name == 'texture':
            summary[name]['exactImages'] = sum(s.get('exact', False) for s in items)
    report = {'scope': 'All six polygon arrays and original primary HEIC per tile',
              'floatPolicy': 'Bit exact except normal Y differences individually explained by Decimal sine and adjacent native float32 rounding; maximum 1 ULP and 5.960464477539063e-8 absolute',
              'nativeRuntimeInvoked': False, 'goldensUsedOnlyForComparison': True,
              'tiles': len(rows), 'statuses': dict(Counter(r['status'] for r in rows)),
              'elapsedSeconds': round(time.monotonic() - started, 3),
              'command': sys.argv, 'arrays': summary, 'results': rows,
              'implementationSHA256': {p.name: sha(p.read_bytes()) for p in
                  (Path(__file__).resolve().parents[1] / 'codec').glob('*.py')}}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('results', 'implementationSHA256')}, indent=2))
    if any(r['status'] not in ('exact', 'explained-normal-rounding') for r in rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
