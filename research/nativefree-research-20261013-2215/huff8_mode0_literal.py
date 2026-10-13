#!/usr/bin/env python3
"""Verified portable Huff8 envelope subset. Only mode0 0x24 and literal Huff816."""
from __future__ import annotations
import struct
class UnsupportedHuff8(ValueError): pass
def peel_huff8(data:bytes, expected_bytes:int|None=None)->bytes:
    if len(data)<4:raise ValueError('Truncated Huff8 header')
    h=struct.unpack_from('<I',data)[0]
    if (h & 0x7f000000)==0x61000000:
        inner=data
    elif (h>>24)==0x24 and (h&0xff)==0 and ((h>>8)&0xff)==0:
        if len(data)<20:raise ValueError('Truncated Huff8 16-byte wrapper')
        inner=data[16:]
    else:
        raise UnsupportedHuff8(f'Unsupported Huff8 header: {h:#010x}')
    if len(inner)<4:raise ValueError('Truncated inner Huff816')
    ih=struct.unpack_from('<I',inner)[0]
    if ih!=0xe1000002:
        raise UnsupportedHuff8(f'Compressed Huff816 not yet supported: {ih:#010x}')
    payload=inner[4:]
    if expected_bytes is not None and len(payload)!=expected_bytes:
        raise ValueError(f'Output byte length mismatch: {len(payload)} != {expected_bytes}')
    return payload

def self_test():
    for n in (0,1,9,100,10000):
        raw=bytes(i%256 for i in range(n))
        inner=struct.pack('<I',0xe1000002)+raw
        for data in (inner,struct.pack('<IIQ',0x24000000,0,0)+inner,struct.pack('<IIQ',0x24000000,32,128)+inner):
            assert peel_huff8(data,n)==raw
            try:peel_huff8(data,n+1);raise AssertionError('Accepted wrong length')
            except ValueError:pass
    for data in (b'',b'\0'*4,b'\0'*19,struct.pack('<IIQ',0x24000100,0,0)+struct.pack('<I',0xe1000002)):
        try:peel_huff8(data);raise AssertionError('Accepted malformed data')
        except ValueError:pass
    print('PASS: Huff8 mode0 wrapper + Huff816 literal, 15 roundtrips and malformed-input checks')
if __name__=='__main__':self_test()
