"""Measure CPU decode/packing and compare every output hash; never use the network."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path, nargs='+')
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--rounds', type=int, default=5)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    if not 1 <= args.rounds <= 20:
        parser.error('Require 1..20 rounds')
    sys.path[:0] = [str(args.source_root/'codec'), str(args.source_root/'ios/Python')]
    from r3d_mobile import decode_tile

    baseline = {}
    if args.baseline:
        baseline = {r['sourceSHA256']: r for r in json.loads(args.baseline.read_text())['tiles']}
    rows = []
    for source in args.inputs:
        raw = source.read_bytes()
        samples = []
        for _ in range(args.rounds):
            started = time.perf_counter()
            output = decode_tile(raw)
            samples.append(time.perf_counter()-started)
        row = {'tile': source.name, 'sourceBytes': len(raw),
               'sourceSHA256': hashlib.sha256(raw).hexdigest(), 'seconds': samples,
               'medianSeconds': statistics.median(samples),
               'outputs': {name: hashlib.sha256(value).hexdigest() for name, value in output.items()}}
        if args.baseline:
            previous = baseline[row['sourceSHA256']]
            if previous['outputs'] != row['outputs']:
                raise ValueError(f'Decoder output changed: {source.name}')
            row.update(outputsMatchBaseline=True, baselineMedianSeconds=previous['medianSeconds'],
                       reductionPercent=100*(1-row['medianSeconds']/previous['medianSeconds']))
        rows.append(row)
    report = {'scope': 'In-process CPU decode and mobile packing; excludes network, Metal and device performance',
              'python': platform.python_version(), 'platform': platform.platform(), 'rounds': args.rounds, 'tiles': rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps([{k: v for k, v in r.items() if k not in ('outputs', 'sourceSHA256', 'seconds')} for r in rows], indent=2))


if __name__ == '__main__':
    main()
