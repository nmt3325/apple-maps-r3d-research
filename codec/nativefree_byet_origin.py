#!/usr/bin/env python3
"""Independent BYET signed-coordinate origin unpacker for Apple R3D v2.

Only covers the 3x int32 *origin* in the two TRICO soup 0x0025 blocks.
The general BYET/J numeric decoder is in nativefree_bytes.py.

Origin byte modes observed:
 - 12 bytes: direct little-endian 3x signed int32
 - control 0x08: byte transition bitmap; unset bits repeat the previous byte,
   including across int32 boundaries (initial previous byte is zero).
 - control 0x04: byte transition bitmap with a 256-entry predictor table.
   Set bits supply and record a successor of the previous byte; unset bits
   use that successor (initial table and previous byte are zero).
These rules follow the saved inert ARM64 capture at 0x1b709e568..0x1b709e5c4
and 0x1b709e8b4..0x1b709e920 respectively. No native code is executed.
"""
from __future__ import annotations
import struct

class UnsupportedAnchorPacking(ValueError):
    pass

def read_origin_int32(data:bytes):
    if len(data)==12:
        return struct.unpack("<3i",data)
    if len(data)<3:
        raise UnsupportedAnchorPacking("Truncated BYET signed anchor bitmap")
    mode=data[0]
    if mode not in (0x04,0x08):
        raise UnsupportedAnchorPacking(f"Unknown signed int32 origin mode {mode:#04x}")
    bitmap=struct.unpack_from("<H",data,1)[0]
    payload=data[3:]
    if bitmap.bit_count()!=len(payload) or bitmap>=1<<12:
        raise UnsupportedAnchorPacking("Signed int32 sparse bitmap/payload count mismatch")
    out=bytearray(12)
    ix=0
    previous=0
    predictor=bytearray(256)
    for i in range(12):
        if bitmap & (1<<i):
            value=payload[ix]
            ix+=1
            if mode==4 and i>0:
                predictor[previous]=value
        else:
            value=previous if mode==8 else predictor[previous]
        out[i]=value
        previous=value
    return struct.unpack("<3i",out)
