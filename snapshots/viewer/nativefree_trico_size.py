#!/usr/bin/env python3
"""Portable implementation of Apple's _read_size.64545 compact integer frame.
Reverse-engineered from the iOS27 ARM64 instruction sequence; no Apple runtime
or platform library is required. It is DIFFERENT from ULEB128 in R3D TLVs.

Prefix bits (least-significant first): 0 => one byte; 10 => two bytes;
110 => three bytes; ... seven 1 bits + 0 => eight bytes.
The little-endian integer is shifted right by prefix width.
0xff => eight raw little-endian bytes follow.
"""
import argparse,json
from pathlib import Path

def read_size(data:bytes,start:int=0,end:int|None=None)->tuple[int,int]:
    end=len(data) if end is None else end
    if start>=end:raise ValueError("Truncated size")
    prefix=data[start]
    if prefix==0xff:
        if start+9>end:raise ValueError("Truncated extended size")
        return int.from_bytes(data[start+1:start+9],"little"),start+9
    width=1
    while width<8 and prefix & (1<<(width-1)):
        width+=1
    if start+width>end:raise ValueError("Truncated compact size")
    raw=int.from_bytes(data[start:start+width],"little")
    return raw>>width,start+width

def encode_size(value:int)->bytes:
    if value<0 or value>=1<<64:raise ValueError("Integer out of range")
    for width in range(1,9):
        marker=(1<<(width-1))-1
        packed=(value<<width)|marker
        if packed<1<<(width*8):
            return packed.to_bytes(width,"little")
    return b"\xff"+value.to_bytes(8,"little")

def self_test():
    for n in (0,1,2,15,64,127,128,192,255,256,1024,4096,
              65535,123456,2**32-1,2**40,2**55,2**63,2**64-1):
        compressed=encode_size(n)
        v,k=read_size(compressed)
        assert v==n and k==len(compressed),(n,compressed.hex(),v,k)
    print("Compact size codec roundtrip passed")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('files',type=Path,nargs='*')
    args=ap.parse_args()
    self_test()
    if args.files:
        for file in args.files:
            b=file.read_bytes()
            print(file.name,'magic',b[:4].hex(),'bytes',len(b))
            if b[:4]==bytes.fromhex('d122c907') and len(b)>60:
                size,end=read_size(b,56)
                print('  first compact field start=56 size=',size,'next_offset=',end,
                      'remainder=',len(b)-end)

if __name__=='__main__':main()
