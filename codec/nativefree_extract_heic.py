#!/usr/bin/env python3
"""Pure-Python independent Apple Maps Flyover R3D inspection and HEIC extraction.

Runs on Linux without iOS/VectorKit. Handles *already acquired* R3D tiles only.
Recovers original HEIC byte-for-byte and the global georeference transform.
Does NOT claim to decode the compressed polygon mesh, UVs or triangular splats.

Usage:
  python3 nativefree_extract_heic.py input.r3d
  python3 nativefree_extract_heic.py input_dir --out-dir /some/isolated/path
  python3 nativefree_extract_heic.py input_dir --verify-native-dir /path/to/native/HEIC/files
"""
import argparse, hashlib, json, math, re, struct, sys
from pathlib import Path

MAGIC=bytes.fromhex("3d96592e")
R3D_TRANSFORM_MARK=bytes.fromhex("01010100016a")
TYPES={b"heic",b"heix",b"hevc",b"hevx",b"mif1",b"msf1"}

def image_dimensions(image:bytes):
    """Read the single spatial extent property in the original HEIC atlas."""
    extents=[]
    def visit(start,end,depth=0):
        if depth>8:raise ValueError("HEIC metadata nesting exceeds limit")
        at=start
        while at<end:
            box=iso_box(image,at)
            if box is None or at+box[0]>end:
                raise ValueError("Invalid HEIC box boundary")
            size,kind=box
            header=16 if image[at:at+4]==b'\0\0\0\1' else 8
            if kind==b'ispe':
                if size!=header+12:raise ValueError("Invalid HEIC ispe property")
                extents.append(struct.unpack_from('>2I',image,at+header+4))
            elif kind in (b'meta',b'iprp',b'ipco'):
                visit(at+header+(4 if kind==b'meta' else 0),at+size,depth+1)
            at+=size
    visit(0,len(image))
    if len(extents)!=1 or not all(0<v<=32768 for v in extents[0]):
        raise ValueError("Unsupported HEIC spatial extent properties")
    return extents[0]

def iso_box(buf:bytes,start:int):
    if start+8>len(buf):return None
    size=int.from_bytes(buf[start:start+4],"big")
    box_type=buf[start+4:start+8]
    header=8
    if size==1:
        if start+16>len(buf):return None
        size=int.from_bytes(buf[start+8:start+16],"big")
        header=16
    if size<header or size>len(buf)-start:return None
    if not all(32<=v<=126 for v in box_type):return None
    return size,box_type

def find_heic_payloads(blob:bytes):
    out=[]
    search=0
    while True:
        mark=blob.find(b"ftyp",search)
        if mark<0:break
        search=mark+4
        base=mark-4
        if base<0:continue
        first=iso_box(blob,base)
        if not first or first[1]!=b"ftyp":continue
        brands=blob[base+8:base+min(first[0],64)]
        if not any(b in brands for b in TYPES):continue
        start=base;pos=base;types=[];ends_mdat=False
        for _ in range(24):
            item=iso_box(blob,pos)
            if item is None:break
            size,typ=item
            types.append(typ.decode("ascii"))
            pos+=size
            if typ==b"mdat":ends_mdat=True
            if ends_mdat:break
        if ends_mdat and b"meta" in [x.encode("ascii") for x in types]:
            out.append((start,blob[start:pos],types))
    return out

def metadata(blob:bytes):
    if blob[:4]!=MAGIC:raise ValueError("Not Apple Maps R3D: wrong magic")
    if len(blob)<180:raise ValueError("Truncated R3D")
    offset=blob.find(R3D_TRANSFORM_MARK)
    if offset<0:raise ValueError("R3D georeference marker not located")
    start=offset+len(R3D_TRANSFORM_MARK)
    if start+12*8>len(blob):raise ValueError("Truncated transform")
    data=struct.unpack_from("<12d",blob,start)
    if not all(math.isfinite(v) for v in data):raise ValueError("Nonfinite R3D transform")
    matrix=data[:9];origin=data[9:]
    norm=math.sqrt(sum(t*t for t in origin))
    det=(matrix[0]*(matrix[4]*matrix[8]-matrix[5]*matrix[7])
         -matrix[1]*(matrix[3]*matrix[8]-matrix[5]*matrix[6])
         +matrix[2]*(matrix[3]*matrix[7]-matrix[4]*matrix[6]))
    if abs(det-1)>0.002 or not 6e6<norm<7e6:
        raise ValueError("R3D transform invalid")
    return {"version":int.from_bytes(blob[4:8],"little"),"matrixR3x3":matrix,
            "ecefTranslation":origin,"rotationDeterminant":det}

def process(src:Path,outdir:Path|None,verify:Path|None):
    b=src.read_bytes()
    meta=metadata(b)
    tex=find_heic_payloads(b)
    results=[]
    for i,(offset,raw,boxes) in enumerate(tex):
        hash_=hashlib.sha256(raw).hexdigest()
        matching=None
        if verify:
            candidates=[verify/(src.name+f".texture-0-{i}.heic"),
                        verify/(src.name+f".texture-{i}-0.heic")]
            for f in candidates:
                if f.is_file():
                    matching=(hashlib.sha256(f.read_bytes()).hexdigest()==hash_)
                    break
        if outdir:
            outdir.mkdir(parents=True,exist_ok=True)
            (outdir/(src.stem+f".atlas-{i}.heic")).write_bytes(raw)
        results.append(dict(index=i,byteOffset=offset,bytes=len(raw),
                            sha256=hash_,boxTypes=boxes,exactNativeMatch=matching))
    return dict(sourceFile=src.name,bytes=len(b),r3dVersion=meta["version"],
                rotationDeterminant=round(meta["rotationDeterminant"],8),
                ecefTranslation=[round(v,3) for v in meta["ecefTranslation"]],
                images=results)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("--out-dir",type=Path)
    ap.add_argument("--verify-native-dir",type=Path)
    ap.add_argument("--limit",type=int,default=0)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    files=sorted(args.input.glob("*.r3d")) if args.input.is_dir() else [args.input]
    if args.limit:files=files[:args.limit]
    rows=[];errors=[]
    for f in files:
        try:rows.append(process(f,args.out_dir,args.verify_native_dir))
        except Exception as ex:errors.append({"file":f.name,"error":str(ex)})
    check=[t["exactNativeMatch"] for r in rows for t in r["images"] if t["exactNativeMatch"] is not None]
    summary={"files":len(files),"validR3D":len(rows),
             "imageCount":sum(len(r["images"]) for r in rows),
             "imageBytes":sum(t["bytes"] for r in rows for t in r["images"]),
             "nativeByteComparison":dict(passed=sum(x is True for x in check),failed=sum(x is False for x in check),checked=len(check)),
             "errors":errors,"samples":rows[:4]}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if errors or any(x is False for x in check):sys.exit(1)

if __name__=="__main__":main()
