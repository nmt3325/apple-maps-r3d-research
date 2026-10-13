#!/usr/bin/env python3
"""Audit the observed BYET/J kind-0 coordinate low-byte path.

This is a golden comparison, not a general BYET decoder: it checks whether
the first N bytes of active kind-0 XYZ lanes match the corresponding low byte
of native-decoded, tile-local quantized coordinates.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "/opt/flyover-viewer")
from nativefree_byet_jdescriptor import split_j
from nativefree_r3d_codec_streams import dissect
from nativefree_trico_size import read_size


def audit(r3d_dir: Path, golden_dir: Path) -> dict:
    tiles_with_gold = 0
    lanes_tested = 0
    exact_lanes = 0
    point_comparisons = 0
    exact_points = 0
    three_n_lanes = 0
    mismatches: list[dict] = []

    for path in sorted(r3d_dir.glob("*.r3d")):
        golden_path = golden_dir / f"{path.name}.decoded"
        if not golden_path.is_file():
            continue

        raw = path.read_bytes()
        soup = dissect(raw)["splatStream"]
        golden = golden_path.read_bytes()
        if len(golden) < 16:
            raise ValueError(f"Truncated native golden: {golden_path}")
        magic, count, channels, _reserved = struct.unpack_from("<4I", golden)
        if magic != 0x31443352 or channels != 8:
            raise ValueError(f"Unexpected native golden header: {golden_path}")
        expected_bytes = 16 + count * (12 + channels * 4)
        if len(golden) != expected_bytes:
            raise ValueError(f"Native golden length mismatch: {golden_path}")
        if count != soup["pointCount"]:
            raise ValueError(f"Point-count mismatch in {path.name}")
        tiles_with_gold += 1

        xyz = [
            struct.unpack_from("<f", golden, 16 + i * 4)[0]
            for i in range(count * 3)
        ]
        block = soup["blocks"][0]
        anchor = block.get("lowerAnchorXYZMeters")
        if anchor is None:
            continue
        scale = soup["quantizationSteps"][0]

        frame_start = soup["offset"] + block["relativeOffset"]
        origin_length, origin_start = read_size(raw, frame_start + 2)
        origin_header = raw[origin_start:origin_start + origin_length]

        byet = block["byet"]
        payload_start = soup["offset"] + byet["compressedPayloadRelativeOffset"]
        payload = raw[payload_start:payload_start + byet["compressedPayloadBytes"]]
        layout = split_j(payload, 12)

        for desc in layout["descriptors"]:
            if desc["kind"] != 0 or desc["compressedBytes"] == 0:
                continue
            if desc["compressedBytes"] < count:
                continue

            axis = desc["lane"] // 4
            byte_index = desc["lane"] % 4
            lane_start = desc["compressedOffset"]
            data = payload[lane_start:lane_start + desc["compressedBytes"]]
            if len(data) == 3 * count:
                three_n_lanes += 1

            expected = bytearray(count)
            for i in range(count):
                coordinate = xyz[i * 3 + axis]
                quantized = round((coordinate - anchor[axis]) / scale)
                expected[i] = (quantized >> (8 * byte_index)) & 0xFF

            observed = data[:count]
            differences = Counter(
                (observed[i] - expected[i]) & 0xFF for i in range(count)
            )
            matches = sum(observed[i] == expected[i] for i in range(count))
            lanes_tested += 1
            point_comparisons += count
            exact_points += matches
            exact_lanes += matches == count
            if matches != count:
                mismatches.append({
                    "tile": path.name,
                    "pointCount": count,
                    "lane": desc["lane"],
                    "axis": axis,
                    "byteIndex": byte_index,
                    "matchingPoints": matches,
                    "differenceHistogram": dict(differences),
                    "originHeaderHex": origin_header.hex(),
                    "originCodec": block.get("originCodec"),
                })

    return {
        "tilesWithNativeGoldens": tiles_with_gold,
        "kind0CoordinateLanesTested": lanes_tested,
        "kind0LanesExactlyMatchingNativeLowByte": exact_lanes,
        "pointComparisons": point_comparisons,
        "exactPointComparisons": exact_points,
        "kind0LanesWithExactly3xPointCountInputBytes": three_n_lanes,
        "mismatches": mismatches,
        "scope": (
            "Golden comparison of the first N bytes only. It does not decode "
            "the remaining lane bytes, other BYET kinds, or complete XYZ values."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("r3d_dir", type=Path)
    parser.add_argument("native_golden_dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.r3d_dir, args.native_golden_dir)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
