#!/usr/bin/env python3
"""Portable *verified mode* of Apple _huff816_decompress, not full Huffman.

Reverse-engineered ARM64 dispatch at 0x1b709d024: for valid 0x61-family
header with bit31 set, the native implementation copies payload bytes from
byte offset 4. It requires the complete encoded stream to be exactly 4 plus
the byte count requested by the caller. Actual expected decoded size must be
provided explicitly; no guessing from compressed file size or searching for
magic inside unrelated data.

Remaining encoded Huffman8/16 variants have NO implementation here.
"""
from __future__ import annotations
import argparse,struct
from pathlib import Path

class HuffmanNotImplemented(Exception):pass

def huff816_raw_decode(stream:bytes, expected_output_bytes:int):
    if not 0<=expected_output_bytes<=1<<30:raise ValueError("Invalid expected size")
    if len(stream)<4:raise ValueError("Truncated Huff816 header")
    h=struct.unpack_from("<I",stream)[0]
    family=h&0x7f000000
    if family!=0x61000000 or (h & 0x7ffffffe)!=0x61000002:
        raise HuffmanNotImplemented(f"Not supported Huff816 literal header: {h:#010x}")
    if not h&0x80000000:
        raise HuffmanNotImplemented("Compressed Huff816 Huffman bitstream not yet implemented")
    if len(stream)!=expected_output_bytes+4:
        raise ValueError(f"Huff816 literal length mismatch: expected {expected_output_bytes}, got {len(stream)-4}")
    return stream[4:]

def self_test():
    for n in (0,1,7,255,1000,65535):
        expected=bytes((x*31+7)&0xff for x in range(n))
        stream=struct.pack("<I",0xe1000002)+expected
        assert huff816_raw_decode(stream,n)==expected
        for size in (n-1,n+1):
            if size<0:continue
            try:huff816_raw_decode(stream,size);raise AssertionError("bad length accepted")
            except ValueError:pass
    for corrupt in (b"",b"test",b"abcd"*15):
        try:huff816_raw_decode(corrupt,len(corrupt)-4);raise AssertionError("bad header accepted")
        except (ValueError,HuffmanNotImplemented):pass
    print("PASS Huff816 literal dispatch: 6 synthetic roundtrips + size/header rejection")

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--test',action='store_true')
    p.add_argument('--input',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--expected-bytes',type=int)
    a=p.parse_args()
    if a.test:self_test();return
    if not (a.input and a.output and a.expected_bytes is not None):
        p.error('Provide --input, --output, --expected-bytes or --test')
    a.output.write_bytes(huff816_raw_decode(a.input.read_bytes(),a.expected_bytes))
    print('Wrote',a.output,a.output.stat().st_size,'bytes (Huff816 literal subset)')
if __name__=='__main__':main()
