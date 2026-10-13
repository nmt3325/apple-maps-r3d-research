#!/usr/bin/env python3
"""Read-only AArch64 Huff8/Huff16 x3 argument audit.

Parses a saved instruction *capture* as bytes; never loads or executes it.
A nearest-write scan is only local dataflow evidence, not a CFG proof.
"""
import base64
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = 0x1B709C7B4
BYTES_START = 0x1B709F3D0
HUFF = {0x1B709C7B4: "huff8", 0x1B709CBF4: "huff16"}
EXPECTED = {
    0x1B70A06E8: 20, 0x1B70A0980: 28,
    0x1B70A0A14: 20, 0x1B70A0BF0: 28,
    0x1B70A0C84: 20, 0x1B70A0E60: 28,
    0x1B70A1008: 19, 0x1B70A1100: 20,
    0x1B70A12F0: 28, 0x1B70A14E4: 19,
    0x1B70A1578: 24, 0x1B70A16E0: 24,
}

def orr(word):
    """Return (dest, first, second, shift) for ORR Xd,Xn,Xm,LSL #n."""
    if (word & 0xFF200000) != 0xAA000000:
        return None
    if ((word >> 22) & 3) != 0:
        return None
    return (word & 31, (word >> 5) & 31,
            (word >> 16) & 31, (word >> 10) & 63)

def ldr_sp(word):
    """Return (register, byte_offset) for unsigned-immediate LDR Xt,[SP,#n]."""
    if (word & 0xFFC003E0) != 0xF94003E0:
        return None
    return (word & 31, ((word >> 10) & 0xFFF) * 8)

def call_target(word, pc):
    if word >> 26 != 0b100101:
        return None
    imm = word & 0x03FFFFFF
    if imm & 0x02000000:
        imm -= 0x04000000
    return pc + 4 * imm

def audit():
    blob = base64.b64decode(b"".join((ROOT / "codec-slice-arm64.b64").read_bytes().split()), validate=True)
    if len(blob) != 20832 or len(blob) % 4:
        raise ValueError("unexpected instruction capture length")
    words = [int.from_bytes(blob[i:i+4], "little") for i in range(0,len(blob),4)]
    rows = []
    for index, word in enumerate(words):
        pc = BASE + index * 4
        target = call_target(word, pc)
        if pc < BYTES_START or target not in HUFF:
            continue
        candidates = [orr(words[j]) for j in range(max(0,index-5),index)]
        moves = [op for op in candidates if op and op[0] == 3
                 and op[1] == 31 and op[3] == 0]
        if not moves:
            raise ValueError(f"no nearby MOV x3 before Huff call at {pc:#x}")
        reg = moves[-1][2]
        definitions = []
        for j in range(max(0,index-220), index-1):
            insn = words[j]
            o = orr(insn)
            l = ldr_sp(insn)
            if o and o[0] == reg:
                definitions.append({"pc":hex(BASE+4*j), "type":"orr",
                    "xN":o[1],"xM":o[2],"lsl":o[3]})
            if l and l[0] == reg:
                definitions.append({"pc":hex(BASE+4*j), "type":"ldr_sp",
                    "offset":l[1]})
        rows.append({"pc":hex(pc), "huff":HUFF[target], "x3From":f"x{reg}",
                     "nearestCandidateDefinitions":definitions[-3:]})
    actual = {int(row["pc"],16):int(row["x3From"][1:]) for row in rows}
    if actual != EXPECTED:
        raise AssertionError(f"callsite provenance changed: {actual!r}")
    return {"sliceBytes":len(blob), "callsiteCount":len(rows),
            "sources":dict(Counter(row["x3From"] for row in rows)),
            "calls":rows,
            "warning":"Nearest definitions are not path-sensitive; exact BYET lane output-count formulas still require CFG/stack provenance."}

if __name__ == "__main__":
    print(json.dumps(audit(),indent=2))
