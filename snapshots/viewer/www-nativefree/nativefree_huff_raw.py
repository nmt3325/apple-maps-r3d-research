#!/usr/bin/env python3
"""Portable Huff816 uncompressed-envelope subset for Apple R3D BYET lanes.

The Apple huff816_decompress checks header bit31 and for this path copies
the following payload bytes directly, requiring compressed_size=raw_size+4.
The concrete observed marker is uint32 LE 0xe1000002.

This extracts Huff-stage literal bytes from supported lanes. It is NOT a
finished BYET integer decoder, and does not produce Splat XYZ floats.
"""
from pathlib import Path
from collections import Counter
import argparse, json
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j

RAW_HEADER=0xe1000002

def decode_raw_huff_lane(src:bytes):
    # The preceding BYET type-specific envelope is 2-5 bytes.
    matches=[pos for pos in range(2,min(7,len(src)-3))
             if int.from_bytes(src[pos:pos+4],"little")==RAW_HEADER]
    if len(matches)!=1:return None
    start=matches[0]+4
    return {"huffmanHeaderOffset":matches[0],
            "huffmanHeaderVersion":hex(RAW_HEADER),
            "literalBytes":src[start:]}

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("input",type=Path)
    cli.add_argument("--save",type=Path,default=None)
    cli.add_argument("--report",type=Path,default=None)
    args=cli.parse_args()
    files=sorted(args.input.glob("*.r3d")) if args.input.is_dir() else [args.input]
    done=Counter();saved=[];examples=[]
    for f in files:
        b=f.read_bytes();s=dissect(b)["splatStream"]
        for frame in s["blocks"]:
            spec=frame["byet"];p=s["offset"]+spec["compressedPayloadRelativeOffset"]
            whole=b[p:p+spec["compressedPayloadBytes"]]
            lanes=split_j(whole,12 if frame["index"]==0 else 32)
            for d in lanes["descriptors"]:
                n=d["compressedBytes"]
                if n<9:continue
                src=whole[d["compressedOffset"]:d["compressedOffset"]+n]
                raw=decode_raw_huff_lane(src)
                if raw is None:continue
                output=raw["literalBytes"]
                done[(frame["index"],d["kind"])]+=1
                if args.save:
                    args.save.mkdir(parents=True,exist_ok=True)
                    out=args.save/f"{f.stem}.soup{frame['index']}.lane{d['lane']}.raw"
                    out.write_bytes(output)
                    saved.append(str(out))
                if len(examples)<5:
                    examples.append({"file":f.name,"block":frame["index"],
                                     "lane":d["lane"],"kind":d["kind"],
                                     "compressedLaneBytes":n,
                                     "literalHuffmanBytes":len(output),
                                     "headerOffset":raw["huffmanHeaderOffset"]})
    summary={"tilesScanned":len(files),
             "rawHuffmanLaneSamples":sum(done.values()),
             "rawHuffmanByFrameAndLaneType":{str(k):v for k,v in done.items()},
             "literalFilesWritten":len(saved),
             "scope":"Huff816 literal payload extraction only; BYET integer delta stage remains encoded.",
             "samples":examples}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
