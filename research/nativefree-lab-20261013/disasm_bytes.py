#!/usr/bin/env python3
"""Offline AArch64 instruction-text audit of already captured interoperability slice.
No ARM instructions executed; no native runtime loaded. Private research lab only.
"""
import base64
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
ROOT=Path(__file__).resolve().parent
BASE=0x1b709c7b4
START=0x1b709f3d0
END=0x1b70a1914
data=base64.b64decode(b"".join((ROOT/"codec-slice-arm64.b64").read_bytes().split()),validate=True)
assert len(data)==20832 and BASE+len(data)==END
cs=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
cs.detail=True
ins=list(cs.disasm(data[START-BASE:],START))
assert ins and ins[0].address==START and ins[-1].address+ins[-1].size==END
text="\n".join(f"{i.address:011x}: {i.mnemonic:9s} {i.op_str}" for i in ins)+"\n"
out=ROOT/"bytes_decompress_arm64_disasm.txt"
out.write_text(text)
print(f"Disassembled {len(ins)} instructions, text {len(text)} chars, output {out}")
sites=[0x1b70a06e8,0x1b70a0980,0x1b70a0a14,0x1b70a0bf0,0x1b70a0c84,0x1b70a0e60,0x1b70a1008,0x1b70a1100,0x1b70a14e4,0x1b70a12f0,0x1b70a1578,0x1b70a16e0]
for pc in sites:
    print(f"\n== Huff call {pc:#x} ==")
    for i in ins:
        if pc-48<=i.address<=pc+12:
            print(f"{i.address:x} {i.mnemonic:8s} {i.op_str}")
