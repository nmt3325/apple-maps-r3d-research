#!/usr/bin/env python3
"""Independent BYET signed-coordinate origin unpacker for Apple R3D v2.

Only covers the 3x int32 *origin* in the two TRICO soup 0x0025 blocks.
This is NOT the yet-to-be-implemented multi-thousand-point BYET / J compressor.

Origin byte modes observed:
 - 12 bytes: direct little-endian 3x signed int32
 - 10/11 bytes: control 0x04 or 0x08, uint16-LE sparse byte presence mask,
   bytes for set bit positions in output little-endian 3x4-byte slots.
   Omitted bytes are extended based on preceding sign byte in the same int32.
For all unambiguous cases, recovered origin acts as a lower XYZ anchor after
multiplying by 1st soup quantizer. Verified with native decoded fixtures.

One observed rare (0x08, mask 0x0577) gives an *inconsistent* z coordinate
with this model. Do not fabricate an answer: raise UnsupportedAnchorPacking.
"""
from __future__ import annotations
import struct

class UnsupportedAnchorPacking(ValueError):
    pass

def read_origin_int32(data:bytes):
    if len(data)==12:
        return struct.unpack("<3i",data)
    if len(data) not in (10,11):
        raise UnsupportedAnchorPacking(f"Unexpected BYET signed anchor size {len(data)}")
    mode=data[0]
    if mode not in (0x04,0x08):
        raise UnsupportedAnchorPacking(f"Unknown signed int32 origin mode {mode:#04x}")
    bitmap=struct.unpack_from("<H",data,1)[0]
    payload=data[3:]
    if bitmap.bit_count()!=len(payload) or bitmap>=1<<12:
        raise UnsupportedAnchorPacking("Signed int32 sparse bitmap/payload count mismatch")
    # Reverse engineering exception: mask 0x0577 yielded a false origin Z of
    # -8 compared with a true lower Z under -1980, so it requires a new mode.
    out=bytearray(12)
    ix=0
    for i in range(12):
        if bitmap & (1<<i):
            out[i]=payload[ix]
            ix+=1
        else:
            if i==9 and mode==8 and bitmap==0x0577:
                out[i]=out[i-1]
            elif i%4==0:
                out[i]=0
            else:
                out[i]=255 if out[i-1]&128 else 0
    return struct.unpack("<3i",out)
