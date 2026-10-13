#!/usr/bin/env python3
"""Locate native Huff8/16 stream headers inside recovered TRICO J lanes.

Native iOS 27 _huff8_decompress recognizes high-byte family 0x24 or 0x61.
The J per-byte-lane envelope has a variable 0-5 byte prefix, so the first
four lane bytes are NOT necessarily the Huff header.

This module classifies byte-aligned candidate Huff headers; it does not
decompress entropy-coded symbols or imply that all detected candidates are
genuine Huffman data. Additional format checks are still needed.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j

def detect_huff_headers(payload:bytes,limit:int=7):
    results=[]
    for at in range(max(0,min(limit+1,len(payload)-3))):
        w=int.from_bytes(payload[at:at+4],"little")
        family=(w>>24)&0x7f
        if family not in (0x24,0x61):
            continue
        # Apple Huff8 decompress dispatch first checks family 0x24 or 0x61.
        # For 0x24 its field-validator examines low 8 bits and a secondary
        # flag mask, while 0x61 accepts limited low-bit parameter variants.
        low=w&0xff
        if family==0x24 and low!=0:
            continue
        if family==0x61 and low not in (0,1,2):
            continue
        results.append({"relativeOffset":at,"family":hex(family),
                        "word":hex(w),"lowFlag":low})
    return results

def inspect_r3d(file:Path):
    buf=file.read_bytes()
    meta=dissect(buf)
    soup=meta["splatStream"]
    out=[]
    for frame in soup["blocks"]:
        spec=frame["byet"]
        start=soup["offset"]+spec["compressedPayloadRelativeOffset"]
        payload=buf[start:start+spec["compressedPayloadBytes"]]
        layout=split_j(payload,12 if frame["index"]==0 else 32)
        for lane in layout["descriptors"]:
            n=lane["compressedBytes"]
            if not n:
                continue
            raw=payload[lane["compressedOffset"]:lane["compressedOffset"]+n]
            candidates=detect_huff_headers(raw)
            out.append({"frame":frame["index"],"lane":lane["lane"],
                        "kind":lane["kind"],"compressedBytes":n,
                        "huffCandidates":candidates})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    files=sorted(args.input.glob("*.r3d")) if args.input.is_dir() else [args.input]
    kinds=Counter();families=Counter();locations=Counter();unmarked=Counter()
    samples=[]
    for file in files:
        for row in inspect_r3d(file):
            kinds[row["kind"]]+=1
            matches=row["huffCandidates"]
            if matches:
                match=matches[0]
                families[match["family"]]+=1
                locations[(row["kind"],match["relativeOffset"],match["family"])]+=1
                if len(samples)<6:
                    samples.append(dict(tile=file.name,**row))
            else:
                unmarked[row["kind"]]+=1
    report={"tiles":len(files),"nonemptyLaneKinds":dict(kinds),
            "recognizedHuffmanHeaderFamilies":dict(families),
            "firstMarkerLocations":{str(k):v for k,v in locations.most_common(24)},
            "unmarkedByKind":dict(unmarked),
            "warning":"Header signatures alone do not constitute decompression or parity of XYZ positions.",
            "examples":samples}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
