#!/usr/bin/env python3
"""Independent byte-lane directory for Apple R3D BYET/J compressed streams.

Verified by testing 590/590 captured Splat coordinate and attribute streams:
- XYZ: 12 byte lanes (3 signed int32 channels)
- Attributes: 32 byte lanes (8 signed int32 channels)
- Two little-endian lane bitmaps:
    first: ceil(lanes/8) byte active-lane bitmap
    second: ceil(2*(number-of-active-lanes-1)/8) byte control bitmap
- Active lanes have type and byte length (two conditional tokens per additional
  active lane), with absent tokens inherited from the preceding active lane.
- A type 4/6 can mark the previous lane as part of an encoded multi-byte group.
- Every lane's compressed byte count sums to exactly all remaining file bytes,
  no trailing padding, on all 590 genuine streams from Tokyo and Hawaii.
This module frames types 0..6; nativefree_bytes.py performs numeric decoding.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse,json
from nativefree_r3d_codec_streams import dissect
from nativefree_trico_size import read_size

def split_j(src:bytes,lanes:int):
    if lanes not in (1,4,8,12,32):raise ValueError("Expect 1/4/8/12/32 byte lanes")
    bitmap1_len=(lanes+7)//8
    if len(src)<bitmap1_len:raise ValueError("Truncated J active-lane bitmap")
    mask=int.from_bytes(src[:bitmap1_len],"little")
    if mask>>lanes:raise ValueError("J active bitmap has out-of-range lane bits")
    active=mask.bit_count()
    if active==0:
        if len(src)!=bitmap1_len:raise ValueError("Trailing bytes after zero J bitmap")
        return {"recordLaneBytes":lanes,"activeLanes":0,
                "firstBitmapBytes":bitmap1_len,"secondBitmapBytes":0,
                "descriptorBytes":0,"laneCompressedBytes":0,
                "descriptors":[{"lane":i,"kind":1,"compressedBytes":0,
                                "compressedOffset":bitmap1_len} for i in range(lanes)]}
    bitmap2_len=(2*(active-1)+7)//8
    if len(src)<bitmap1_len+bitmap2_len:raise ValueError("Truncated J token bitmap")
    mask2=int.from_bytes(src[bitmap1_len:bitmap1_len+bitmap2_len],"little")
    cursor=bitmap1_len+bitmap2_len
    bitpos=0
    previous=-1
    descriptors=[]
    for index in range(lanes):
        if not ((mask>>index)&1):
            descriptors.append({"lane":index,"kind":1,"compressedBytes":0})
            continue
        if previous<0:
            if cursor>=len(src):raise ValueError("Truncated first J lane type")
            kind=src[cursor];cursor+=1
            length,cursor=read_size(src,cursor)
        else:
            if (mask2>>bitpos)&1:
                if cursor>=len(src):raise ValueError("Truncated J lane type")
                kind=src[cursor];cursor+=1
            else:
                kind=descriptors[previous]["kind"]
            bitpos+=1
            if (mask2>>bitpos)&1:
                length,cursor=read_size(src,cursor)
            else:
                length=descriptors[previous]["compressedBytes"]
            bitpos+=1
        if kind>6:raise ValueError(f"Unsupported J kind {kind}, descriptor {index}")
        descriptors.append({"lane":index,"kind":kind,"compressedBytes":length})
        # Paired 16-bit/32-bit lane operations retroactively mark the prior lane.
        if kind in (4,6) and index>0:
            descriptors[index-1]["kind"]=kind
        previous=index
    if bitpos!=2*(active-1):raise ValueError("J control bitmap not consumed exactly")
    payload_cursor=cursor
    for desc in descriptors:
        length=desc["compressedBytes"]
        if length>len(src)-cursor:
            raise ValueError(f"J lane {desc['lane']} extends beyond compressed bytes")
        desc["compressedOffset"]=cursor
        cursor+=length
    if cursor!=len(src):raise ValueError(f"J leftover {len(src)-cursor} bytes after lane directory")
    return {"recordLaneBytes":lanes,"activeLanes":active,
            "firstBitmapBytes":bitmap1_len,"secondBitmapBytes":bitmap2_len,
            "descriptorBytes":payload_cursor-bitmap1_len-bitmap2_len,
            "laneCompressedBytes":len(src)-payload_cursor,
            "descriptors":descriptors}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("--report",type=Path)
    ap.add_argument("--samples",type=int,default=2)
    args=ap.parse_args()
    files=sorted(args.input.glob("*.r3d")) if args.input.is_dir() else [args.input]
    total=Counter();examples=[];kinds=Counter();bytes_=0
    for f in files:
        data=f.read_bytes()
        meta=dissect(data)
        sp=meta["splatStream"]
        for block in sp["blocks"]:
            j=block["byet"]
            start=sp["offset"]+j["compressedPayloadRelativeOffset"]
            compressed=data[start:start+j["compressedPayloadBytes"]]
            layout=split_j(compressed,12 if block["index"]==0 else 32)
            total[block["index"]]+=1
            bytes_+=len(compressed)
            kinds.update(d["kind"] for d in layout["descriptors"])
            if len(examples)<args.samples:
                examples.append({"source":f.name,"stream":block["index"],**layout})
    out={"tiles":len(files),"decodedXYZLaneDirectories":total[0],
         "decodedAttributeLaneDirectories":total[1],
         "compressedJBytes":bytes_,"laneKinds":dict(kinds),
         "note":"All byte ranges are encoded; decoded numeric Splat XYZ not yet available.",
         "samples":examples}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
