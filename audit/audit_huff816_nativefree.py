#!/usr/bin/env python3
"""Cross-check native-free Huff816 decoding over captured R3D lanes.

Requires the existing read-only framing helpers in /opt/flyover-viewer.
Reports Huff816 frames for which the captured 0x24 wrapper provides an exact
output byte count. It intentionally does not claim BYET reconstruction.
"""
from __future__ import annotations

import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codec"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_huffman_header import detect_huff_headers
from nativefree_trico_size import read_size
from huff816_nativefree import HuffError, decode, parse_table


def scan(root: Path) -> dict:
    counts: Counter = Counter()
    samples: list[dict] = []
    failures: list[dict] = []
    tile_count = 0
    for file in sorted(root.rglob("*.r3d")):
        tile_count += 1
        raw = file.read_bytes()
        soup = dissect(raw)["splatStream"]
        for frame in soup["blocks"]:
            byet = frame["byet"]
            start = soup["offset"] + byet["compressedPayloadRelativeOffset"]
            payload = raw[start:start + byet["compressedPayloadBytes"]]
            lanes = split_j(payload, 12 if frame["index"] == 0 else 32)
            for lane in lanes["descriptors"]:
                size = lane["compressedBytes"]
                if not size:
                    continue
                encoded = payload[lane["compressedOffset"]:lane["compressedOffset"] + size]
                candidates = detect_huff_headers(encoded)
                if not candidates:
                    counts["no_header_candidate"] += 1
                    continue
                marker = candidates[0]
                start = marker["relativeOffset"]
                header_stream = encoded[start:]
                first_word = struct.unpack_from("<I", header_stream)[0]
                prefix_values = []
                prefix_pos = 0
                try:
                    while prefix_pos < start:
                        value, prefix_pos = read_size(encoded, prefix_pos, start)
                        prefix_values.append(value)
                except ValueError:
                    prefix_values = []
                if first_word == 0xE1000002:
                    counts["literal_huff816_dispatch"] += 1
                    counts["literal_huff816_payload_bytes"] += max(0, len(header_stream) - 4)
                    continue
                if marker["family"] == "0x61" and not (first_word & 0x80000000):
                    if not prefix_values:
                        counts["other_or_unbounded_frame"] += 1
                        continue
                    requested_symbols = prefix_values[0]
                    try:
                        table = parse_table(header_stream, width=8)
                        decoded = decode(header_stream, requested_symbols, width=8)
                        counts["direct_huff816_frames_decoded"] += 1
                        counts["direct_huff816_output_bytes"] += len(decoded)
                        if len(samples) < 12:
                            samples.append({
                                "tile": file.name,
                                "soup": frame["index"],
                                "lane": lane["lane"],
                                "byet_kind": lane["kind"],
                                "frame_kind": "direct-0x61",
                                "prefix_fields": prefix_values,
                                "output_bytes_requested": requested_symbols,
                                "output_bytes_decoded": len(decoded),
                                "table_symbols": table.count,
                                "table_bits": table.bit_offset,
                                "first_16_bytes": decoded[:16].hex(),
                            })
                    except Exception as exc:
                        counts[("frame_rejected", type(exc).__name__)] += 1
                        if len(failures) < 12:
                            failures.append({
                                "tile": file.name,
                                "soup": frame["index"],
                                "lane": lane["lane"],
                                "byet_kind": lane["kind"],
                                "frame_kind": "direct-0x61",
                                "prefix_fields": prefix_values,
                                "error": str(exc),
                            })
                    continue
                if marker["family"] != "0x24" or len(header_stream) < 20:
                    counts["other_or_unbounded_frame"] += 1
                    continue
                wrapper_tag = (first_word >> 8) & 0xFF
                requested_bytes = struct.unpack_from("<Q", header_stream, 8)[0]
                inner = header_stream[16:]
                inner_word = struct.unpack_from("<I", inner)[0] if len(inner) >= 4 else 0
                if inner_word == 0xE1000002:
                    counts["literal_inside_huff8_wrapper"] += 1
                    counts["literal_inside_wrapper_bytes"] += max(0, len(inner) - 4)
                    continue
                try:
                    table = parse_table(inner, width=8)
                    decoded = decode(inner, requested_bytes, width=8)
                    if len(decoded) != requested_bytes:
                        raise HuffError("decoded output length mismatch")
                    counts["compressed_huff816_frames_decoded"] += 1
                    counts["decoded_output_bytes"] += len(decoded)
                    counts[("wrapper_tag", wrapper_tag)] += 1
                    if len(samples) < 12:
                        samples.append({
                            "tile": file.name,
                            "soup": frame["index"],
                            "lane": lane["lane"],
                            "byet_kind": lane["kind"],
                            "wrapper_tag": wrapper_tag,
                            "output_bytes_requested": requested_bytes,
                            "output_bytes_decoded": len(decoded),
                            "table_symbols": table.count,
                            "table_bits": table.bit_offset,
                            "first_16_bytes": decoded[:16].hex(),
                        })
                except Exception as exc:
                    counts[("frame_rejected", type(exc).__name__)] += 1
                    if len(failures) < 12:
                        failures.append({
                            "tile": file.name,
                            "soup": frame["index"],
                            "lane": lane["lane"],
                            "byet_kind": lane["kind"],
                            "wrapper_tag": wrapper_tag,
                            "requested_bytes": requested_bytes,
                            "error": str(exc),
                            "inner_header": inner[:16].hex(),
                        })
    return {
        "tiles": tile_count,
        "counts": {str(k): v for k, v in counts.items()},
        "samples": samples,
        "rejections": failures,
        "scope": "Huff816 byte decode only; BYET predictor and float reconstruction remain separate.",
    }


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: audit_huff816_nativefree.py ROOT [ROOT ...] [--report PATH]")
    roots: list[Path] = []
    report = None
    args = iter(sys.argv[1:])
    for arg in args:
        if arg == "--report":
            report = Path(next(args))
        else:
            roots.append(Path(arg))
    result = {str(root): scan(root) for root in roots}
    rendered = json.dumps(result, indent=2)
    if report:
        report.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
