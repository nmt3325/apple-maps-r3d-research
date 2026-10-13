#!/usr/bin/env python3
"""Static-only reconstruction of Huff output-count register constructors.

Reads a captured AArch64 instruction slice as inert data. It never executes
Apple code, and never claims that an ORR chain alone proves a BYET lane kind.
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = 0x1B709C7B4
EXPECTED_X28 = {
    0x1B70A0784: (248, 252, 254),
    0x1B70A0AB0: (224, 228, 230),
    0x1B70A0D20: (200, 204, 206),
    0x1B70A119C: (272, 276, 278),
}
EXPECTED_X24 = {
    0x1B70A1428: (23, 28, 8),
    0x1B70A152C: (23, 28, 8),
    0x1B70A16AC: (28, 23, 8),
}

def orr(word):
    """Logical shifted register ORR, returning width, rd, rn, rm, shift."""
    if word & 0x7F200000 != 0x2A000000 or ((word >> 22) & 3):
        return None
    return (64 if word >> 31 else 32, word & 31,
            (word >> 5) & 31, (word >> 16) & 31,
            (word >> 10) & 63)

def load_unsigned(word):
    """LDRB/LDRH/LDR W/X unsigned immediate, including SP-based loads."""
    sizes = {0x39400000: 1, 0x79400000: 2,
             0xB9400000: 4, 0xF9400000: 8}
    width = sizes.get(word & 0xFFC00000)
    if width is None:
        return None
    return (width, word & 31, (word >> 5) & 31,
            ((word >> 10) & 4095) * width)

def words():
    src = b"".join((ROOT / "codec-slice-arm64.b64").read_bytes().split())
    blob = base64.b64decode(src, validate=True)
    if len(blob) != 20832:
        raise ValueError("unexpected instruction slice length")
    return {i: int.from_bytes(blob[i-BASE:i-BASE+4], "little")
            for i in range(BASE, BASE+len(blob), 4)}

def audit():
    w = words()
    result = []
    for pc, offsets in EXPECTED_X28.items():
        instr = orr(w[pc])
        if instr is None or instr[1] != 28:
            raise AssertionError(f"missing x28 constructor at {pc:#x}")
        window = [(p, load_unsigned(w[p]), orr(w[p]))
                  for p in range(pc-40, pc, 4)]
        sp = {(ins[0], ins[3]): (p, ins[1])
              for p, ins, _ in window if ins and ins[2] == 31}
        for width, offset in zip((4, 2, 1), offsets):
            if (width, offset) not in sp:
                raise AssertionError(f"missing SP fragment at {pc:#x}: {width}@{offset}")
        if (8, 16) not in sp:
            raise AssertionError(f"missing saved low-order fragment at {pc:#x}")
        result.append({
            "pc":hex(pc), "destination":"x28",
            "source":"x13 from [sp,#16] OR packed SP fragments",
            "fragments":[{"bytes":4,"spOffset":offsets[0]},
                         {"bytes":2,"spOffset":offsets[1]},
                         {"bytes":1,"spOffset":offsets[2]}],
            "combineORR":{"rn":instr[2],"rm":instr[3],"lsl":instr[4]},
            "interpretation":"candidate 64-bit output count; exact source of low byte and branch condition unresolved"
        })
    for pc, (rn, rm, shift) in EXPECTED_X24.items():
        ins = orr(w[pc])
        if ins != (64, 24, rn, rm, shift):
            raise AssertionError(f"unexpected x24 construction at {pc:#x}: {ins}")
        result.append({"pc":hex(pc),"destination":"x24",
                       "combineORR":{"rn":rn,"rm":rm,"lsl":shift},
                       "interpretation":"register-level packing only; field provenance unresolved"})
    return {"instructionSliceBytes":20832,"verifiedConstructors":len(result),
            "x28WideCandidates":4,"x24Candidates":3,
            "note":"Static instruction evidence, not Huff decompression or numeric golden parity",
            "constructors":result}

if __name__ == "__main__":
    print(json.dumps(audit(),indent=2))
