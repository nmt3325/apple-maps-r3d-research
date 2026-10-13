#!/usr/bin/env python3
"""Static 7-byte tail audit for the captured BYET/Huff ARM64 function.

No native instructions are executed.  This module verifies four observed
instruction windows and reconstructs only the 56-bit tail of a possible
8-byte integer.  The origin/width of x13's low fragment is NOT established.
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = 0x1B709C7B4
WINDOWS = {
    0x1B70A0784: (248, "shifted_u32"),
    0x1B70A0AB0: (224, "shifted_u56"),
    0x1B70A0D20: (200, "shifted_u56"),
    0x1B70A119C: (272, "shifted_u56"),
}

def read_words():
    blob = base64.b64decode(b"".join((ROOT / "codec-slice-arm64.b64").read_bytes().split()), validate=True)
    if len(blob) != 20832:
        raise ValueError("unexpected capture length")
    return {BASE + i: int.from_bytes(blob[i:i+4], "little") for i in range(0, len(blob), 4)}

def ldr(word, width, rt, offset):
    opcode = {1: 0x39400000, 2: 0x79400000, 4: 0xB9400000, 8: 0xF9400000}[width]
    return word == opcode | ((offset // width) << 10) | (31 << 5) | rt

def orr64(word, rd, rn, rm, shift):
    return word == (0xAA000000 | (rm << 16) | (shift << 10) | (rn << 5) | rd)

def orr32(word, rd, rn, rm, shift):
    return word == (0x2A000000 | (rm << 16) | (shift << 10) | (rn << 5) | rd)

def tail_from_bytes(fragment: bytes, mode: str) -> int:
    """Return bits 8..63 only; x13's low eight bits are not reconstructed."""
    if len(fragment) != 7:
        raise ValueError("seven bytes required")
    low4 = int.from_bytes(fragment[:4], "little")
    upper3 = int.from_bytes(fragment[4:], "little")
    if mode == "shifted_u32":
        # LDR W10; UBFM X10,X10,#56,#55 => LSL #8;
        # ORR X9,X10,X9,LSL #40; ORR X28,X9,X13
        result = (low4 << 8) | (upper3 << 40)
    elif mode == "shifted_u56":
        # ORR X9,X10,X9,LSL #32; ORR X28,X13,X9,LSL #8
        result = (low4 | (upper3 << 32)) << 8
    else:
        raise ValueError("unknown mode")
    return result

def combine_with_low_fragment(tail: int, x13: int) -> int:
    """Hypothesis ONLY: x13 must contain exactly one low byte."""
    if not 0 <= x13 <= 255:
        raise ValueError("x13 is not proven to be a low byte; cannot combine")
    if tail & 255:
        raise ValueError("tail overlaps low fragment")
    return tail | x13

def audit():
    w = read_words()
    rows = []
    for pc, (offset, mode) in WINDOWS.items():
        checks = {
            "byte_load": ldr(w[pc-24], 1, 9, offset+6),
            "half_load": ldr(w[pc-20], 2, 10, offset+4),
            "pack_u24": orr32(w[pc-16], 9, 10, 9, 16),
            "word_load": ldr(w[pc-12], 4, 10, offset),
        }
        if mode == "shifted_u32":
            checks.update({
                "lsl8_ubfm": w[pc-8] == 0xD378DD4A,
                "join56": orr64(w[pc-4], 9, 10, 9, 40),
                "combine_x13": orr64(w[pc], 28, 9, 13, 0),
            })
        else:
            checks.update({
                "join56": orr64(w[pc-8], 9, 10, 9, 32),
                "combine_x13": orr64(w[pc], 28, 13, 9, 8),
            })
        if not all(checks.values()):
            raise AssertionError(f"failed instruction window {pc:#x}: {checks}")
        rows.append({"pc": hex(pc), "fragmentSpOffsets": [offset, offset+4, offset+6],
                     "tailMode": mode, "checks": checks})
    return {"windowsVerified": len(rows), "instructionChecksPassed": sum(len(r["checks"]) for r in rows),
            "sevenByteTailFormula": "little_endian_u56(fragment[0:7]) << 8",
            "lowFragment": "x13, exact source/width/path conditions UNPROVEN",
            "notProven": ["per-kind Huff output count", "BYET predictor", "Splat/mesh numerical parity"],
            "rows": rows}

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
