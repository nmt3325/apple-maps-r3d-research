"""Decode original TRICO soup vertices and eight attributes using Python only.

Soup record count N represents N triangles, with 3*N positions and N*8
attributes. The native .decoded fixture contains only the first N positions;
the .native-triangle-f32 fixture contains the full 3*N position array.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import struct

from nativefree_bytes import decode_byet
from nativefree_r3d_codec_streams import dissect
from nativefree_trico_size import read_size


@dataclass(frozen=True)
class SoupData:
    count: int
    xyz_f32: bytes
    attributes_f32: bytes
    origins: tuple[tuple[int, ...], ...]
    steps: tuple[float, ...]


def decode_quantized(src: bytes, count: int, channels: int,
                     steps: tuple[float, ...]) -> tuple[bytes, tuple[int, ...]]:
    if src[:2] != b'\x25\x00':
        raise ValueError("Unknown quantized BYET header")
    size, at = read_size(src, 2)
    end = at + size
    if end >= len(src) or len(steps) != channels:
        raise ValueError("Invalid quantized BYET origin length/shape")
    origins = struct.unpack('<' + 'i' * channels,
                            decode_byet(src[at:end], channels, 4))
    integers = decode_byet(src[end:], count, channels * 4)
    out = bytearray(count * channels * 4)
    for i, (delta,) in enumerate(struct.iter_unpack('<i', integers)):
        # -1 is the quantized missing-value sentinel before origin addition.
        # Preserve the native canonical quiet-NaN payload, including for
        # channels with a nonzero origin; do not substitute a numeric value.
        if delta in (-1, -2, -3):
            bits = {-1: 0x7fc00000, -2: 0xff800000, -3: 0x7f800000}[delta]
            struct.pack_into('<I', out, i * 4, bits)
            continue
        channel = i % channels
        value = delta + origins[channel]
        if not -(1 << 31) <= value < 1 << 31:
            raise ValueError("Quantized coordinate integer overflow")
        converted = struct.unpack('<f', struct.pack('<f', value))[0]
        struct.pack_into('<f', out, i * 4, converted * steps[channel])
    return bytes(out), origins


def decode_soup(raw: bytes) -> SoupData:
    meta = dissect(raw)['splatStream']
    offset = meta['offset']
    steps = struct.unpack_from('<9f', raw, offset + 20)
    count = meta['pointCount']
    arrays = []
    origins = []
    for b in meta['blocks']:
        at = offset + b['relativeOffset']
        values, anchor = decode_quantized(
            raw[at:at + b['bytes']],
            3 * count if b['index'] == 0 else count,
            3 if b['index'] == 0 else 8,
            (steps[0],) * 3 if b['index'] == 0 else steps[1:],
        )
        arrays.append(values)
        origins.append(anchor)
    return SoupData(count, arrays[0], arrays[1], tuple(origins), steps)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--out-dir', type=Path, required=True)
    args = ap.parse_args()
    result = decode_soup(args.input.read_bytes())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        'triangle-f32le.bin': result.xyz_f32,
        'attributes-f32le.bin': result.attributes_f32,
    }
    for name, payload in outputs.items():
        (args.out_dir / name).write_bytes(payload)
    manifest = {
        'input': args.input.name, 'decoder': 'independent-python',
        'records': result.count, 'vertices': 3 * result.count,
        'attributesPerRecord': 8, 'origins': result.origins,
        'quantizationSteps': result.steps,
        'outputs': {name: len(payload) for name, payload in outputs.items()},
        'scope': 'TRICO soup only; polygon mesh and material packing are separate',
    }
    (args.out_dir / 'soup.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
