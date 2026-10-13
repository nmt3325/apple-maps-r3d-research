#!/usr/bin/env python3
"""Static ARM64 BL callsite audit for the captured VectorKit codec slice.

Reads only the pre-existing Base64 instruction capture. Does not execute ARM64,
call Apple APIs, write a native binary, or touch production viewer/fetcher.
"""
import argparse
import base64
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = 0x1B709C7B4
TARGETS = {
    0x1B709C7B4: "huff8_decompress",
    0x1B709CBF4: "huff16_decompress",
    0x1B709D024: "huff816_decompress",
}

def audit(blob: bytes):
    if len(blob) % 4:
        raise ValueError("ARM64 instruction slice is not 4-byte aligned")
    rows = []
    for offset in range(0, len(blob), 4):
        word = int.from_bytes(blob[offset:offset+4], "little")
        if word >> 26 != 0b100101:
            continue
        signed = word & 0x03ffffff
        if signed & 0x02000000:
            signed -= 0x04000000
        target = BASE + offset + (signed << 2)
        if target in TARGETS:
            rows.append({
                "callsite": hex(BASE + offset),
                "target": TARGETS[target],
                "targetAddress": hex(target),
                "instructionOffset": offset,
            })
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    blob = base64.b64decode((ROOT / "codec-slice-arm64.b64").read_bytes())
    rows = audit(blob)
    counts = Counter(x["target"] for x in rows)
    in_bytes = [x for x in rows if int(x["callsite"], 16) >= 0x1B709F3D0]
    byte_counts = Counter(x["target"] for x in in_bytes)
    assert len(blob) == 20832
    assert blob[:4] == bytes.fromhex("7f2303d5")
    assert counts["huff816_decompress"] == 10
    assert byte_counts == {"huff8_decompress": 9, "huff16_decompress": 3}
    report = {
        "sliceBase": hex(BASE),
        "sliceBytes": len(blob),
        "huff8Entry": hex(0x1B709C7B4),
        "bytesDecompressEntry": hex(0x1B709F3D0),
        "bytesDecompressOffset": hex(0x1B709F3D0 - BASE),
        "allKnownHuffCallCounts": dict(counts),
        "bytesDecompressCallCounts": dict(byte_counts),
        "bytesDecompressCalls": in_bytes,
        "note": "Static BL target mapping only; no per-kind numeric decoding or golden parity.",
    }
    print(json.dumps(report, indent=2))
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__":
    main()
