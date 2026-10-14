#!/usr/bin/env python3
"""Independent Apple Maps style98 R3D-v2 container + trico *header* parser.

Native-free Linux Python. Does not use iOS simulator, VectorKit, Apple proprietary
compiled decoder, or any platform-specific framework.

Verified signatures:
  R3D outer [01 02 00] + tags 1/2/3 (LEB128 TLV)
  Group 1 (tag 1) fields: [1,1,4,2,3]; tag3 is TRICO *triangle soup*.
  Group 2 (tag 2) fields: [1,1,2,3]; tag2 is TRICO *mesh*.
  Group 2.tag3 (texture container) subfields [1,3,5,6,8].
  Soup magic d1 22 c9 07 / version1 / uint64 splat count at +8.
  Mesh magic e1 21 66 24 / version3.
Note: extracted codec streams are still compressed. Positions, UV and face
index arrays cannot yet be recovered using this native-free module.
"""
import argparse
import importlib.util
import json
import struct
import sys
from pathlib import Path
from nativefree_trico_size import read_size
from nativefree_byet_origin import read_origin_int32,UnsupportedAnchorPacking

SOUP_MAGIC=bytes.fromhex("d1 22 c9 07")
MESH_MAGIC=bytes.fromhex("e1 21 66 24")
MAGIC=bytes.fromhex("3d 96 59 2e")
PREFIX=bytes.fromhex("01 02 00")

def leb(b:bytes,p:int,end:int):
    n=0
    for i in range(10):
        if p>=end:raise ValueError("Truncated ULEB")
        x=b[p];p+=1
        if i==9 and x>1:raise ValueError("Overflow ULEB")
        n|=(x&127)<<(i*7)
        if x<128:return n,p
    raise ValueError("Varint too long")

def fields(b:bytes,start:int,end:int):
    out=[];p=start
    while p<end:
        tag,p=leb(b,p,end)
        length,p=leb(b,p,end)
        if length>end-p:raise ValueError(f"TLV out-of-bounds: tag={tag} length={length} at={p}")
        out.append((tag,p,length))
        p+=length
    return out

def want(fields_,expected):
    keys=[x[0] for x in fields_]
    if keys!=expected:raise ValueError(f"Unexpected TLV tags {keys!r}, wanted {expected!r}")
    return fields_

def dissect(b:bytes):
    if b[:4]!=MAGIC or len(b)<128:raise ValueError("Not R3D v2")
    if struct.unpack_from('<I',b,4)[0]!=2 or b[8:11]!=PREFIX:raise ValueError("R3D v2 header mismatch")
    top=want(fields(b,11,len(b)),[1,2,3])
    major_a=want(fields(b,top[0][1]+1,top[0][1]+top[0][2]),[1,1,4,2,3])
    major_b=fields(b,top[1][1]+1,top[1][1]+top[1][2])
    if [f[0] for f in major_b] not in ([1,1,2,3],[1,1,2]):
        raise ValueError('Unexpected mesh/texture TLV tags')
    material=want(fields(b,major_b[3][1],major_b[3][1]+major_b[3][2]),[1,3,5,6,8]) if len(major_b)==4 else []
    soup_position=major_a[4][1];soup_size=major_a[4][2]
    mesh_position=major_b[2][1];mesh_size=major_b[2][2]
    soup=b[soup_position:soup_position+soup_size]
    mesh=b[mesh_position:mesh_position+mesh_size]
    if not material and (len(mesh)<=20 or mesh[20]!=0):
        raise ValueError('Nonempty polygon mesh has no texture container')
    if soup[:4]!=SOUP_MAGIC or mesh[:4]!=MESH_MAGIC:
        raise ValueError("Unexpected TRICO stream magic")
    soup_version=struct.unpack_from("<I",soup,4)[0]
    mesh_version=struct.unpack_from("<I",mesh,4)[0]
    if soup_version!=1 or mesh_version!=3:raise ValueError("Unknown TRICO stream version")
    n_splats=struct.unpack_from("<Q",soup,8)[0]
    splat_channels=struct.unpack_from("<I",soup,16)[0]
    soup_scales=struct.unpack_from("<9f",soup,20)
    mesh_scales=struct.unpack_from("<3f",mesh,8)
    if splat_channels!=8:raise ValueError(f"Unknown number of R3D Splat channels {splat_channels}")
    if not all(0.000001<q<10.0 for q in soup_scales+mesh_scales):
        raise ValueError("Implausible native quantization coefficients")
    if n_splats<=0 or n_splats>10000000:raise ValueError("Invalid soup point count")
    frame0len,frame0start=read_size(soup,56)
    frame0end=frame0start+frame0len
    if frame0end>len(soup):raise ValueError("TRICO splat block 0 exceeds stream")
    frame1len,frame1start=read_size(soup,frame0end)
    frame1end=frame1start+frame1len
    if frame1end!=len(soup):
        raise ValueError(f"TRICO splat frames do not cover stream: {frame1end} != {len(soup)}")
    if soup[frame0start:frame0start+2]!=b"\x25\x00" or soup[frame1start:frame1start+2]!=b"\x25\x00":
        raise ValueError("Unexpected BYET quantized float block magic; expected 0x0025 in both soup frames")
    xyz_quant_header,xyz_header_end=read_size(soup,frame0start+2,frame0end)
    attr_quant_header,attr_header_end=read_size(soup,frame1start+2,frame1end)
    # Reconstruct 3x signed XYZ origin integers. Most tiles encode direct
    # 12 bytes; a minority use a sparse bitmask BYET packing (10 or 11 bytes).
    xyz_anchor=None
    xyz_origin_codec="unsupported"
    try:
        xyz_bytes=soup[xyz_header_end:xyz_header_end+xyz_quant_header]
        coords=read_origin_int32(xyz_bytes)
        q0=soup_scales[0]
        xyz_anchor=[round(x*q0,5) for x in coords]
        xyz_origin_codec="int32-le" if xyz_quant_header==12 else "byte-transition-bitmap"
    except UnsupportedAnchorPacking as error:
        xyz_origin_codec=f"unsupported: {error}"
    # The native _byet_decompress sees mode bit7 and checks the 0x004A nested
    # marker before invoking its _bytes_decompress byte-plane stage.
    # All 590 blocks from 295 original network tiles use this path.
    byet_specs=[]
    for start,end,header_end in (
        (frame0start,frame0end,xyz_header_end),
        (frame1start,frame1end,attr_header_end),
    ):
        anchor_bytes=soup[start+2:header_end]
        compressed_start=header_end+read_size(soup,start+2,end)[0]
        if compressed_start+3>end:
            raise ValueError("Truncated BYET compressed payload")
        mode=soup[compressed_start]
        marker=struct.unpack_from("<H",soup,compressed_start+1)[0]
        if mode!=0x80 or marker!=0x004a:
            raise ValueError(f"Unrecognized BYET compression mode {mode:02x}, 16-bit marker {marker:04x}")
        byet_specs.append({
            "codec":"BYET -> J byte-plane compressor (not yet decoded)",
            "modeFlag":mode,"codecMarker":f"{marker:04x}",
            "headerBytes":compressed_start-start,
            "compressedPayloadRelativeOffset":compressed_start+3,
            "compressedPayloadBytes":end-(compressed_start+3),
        })
    soup_blocks=[
        {"index":0,"relativeOffset":frame0start,"bytes":frame0len,
         "role":"first quantized float block (Apple reader requests XYZ coordinates)","quantizedHeader":xyz_quant_header,"lowerAnchorXYZMeters":xyz_anchor,"originCodec":xyz_origin_codec},
        {"index":1,"relativeOffset":frame1start,"bytes":frame1len,
         "role":"second quantized float block (Apple reader requests 8 attribute channels)","quantizedHeader":attr_quant_header}
    ]
    for spec,block in zip(byet_specs,soup_blocks):
        block["byet"]=spec
    return {
        "r3dVersion":2,
        "majorTags":[t for t,p,n in top],
        "geometryTagOrder":[t for t,p,n in major_a],
        "appearanceTagOrder":[t for t,p,n in major_b],
        "textureTags":[t for t,p,n in material],
        "splatStream":{"offset":soup_position,"bytes":soup_size,"magic":SOUP_MAGIC.hex(),"codecVersion":soup_version,"pointCount":n_splats,"channelCount":splat_channels,"quantizationSteps":[round(q,7) for q in soup_scales],"blocks":soup_blocks},
        "meshStream":{"offset":mesh_position,"bytes":mesh_size,"magic":MESH_MAGIC.hex(),"codecVersion":mesh_version,"quantizationSteps":[round(q,7) for q in mesh_scales]},
        "textureContainer":{"offset":major_b[3][1],"bytes":major_b[3][2]} if material else None
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("--out-dir",type=Path)
    ap.add_argument("--expected-native-manifest",type=Path)
    ap.add_argument("--report",type=Path)
    ap.add_argument("--limit",type=int,default=0)
    args=ap.parse_args()
    files=sorted(args.input.glob("*.r3d")) if args.input.is_dir() else [args.input]
    if args.limit:files=files[:args.limit]
    golden={}
    if args.expected_native_manifest:
        golden={x["file"]:x for x in json.loads(args.expected_native_manifest.read_text())["files"]}
    ok=[];fail=[];matching=0;mismatch=0
    for f in files:
        try:
            b=f.read_bytes()
            data=dissect(b)
            data["file"]=f.name
            data["wireBytes"]=len(b)
            native=golden.get(f.name)
            if native:
                data["goldenNativeSplatCount"]=native["vertices"]
                data["splatCountExactMatch"]=native["vertices"]==data["splatStream"]["pointCount"]
                matching+=bool(data["splatCountExactMatch"])
                mismatch+=not data["splatCountExactMatch"]
            if args.out_dir:
                args.out_dir.mkdir(parents=True,exist_ok=True)
                for key,ext in (("splatStream",".trico-soup"),("meshStream",".trico-mesh")):
                    part=data[key];start=part["offset"]
                    (args.out_dir/(f.name+ext)).write_bytes(b[start:start+part["bytes"]])
                soup_meta=data["splatStream"]
                for chunk in soup_meta["blocks"]:
                    begin=soup_meta["offset"]+chunk["relativeOffset"]
                    end=begin+chunk["bytes"]
                    (args.out_dir/(f.name+f".trico-soup-{chunk['index']}")).write_bytes(b[begin:end])
                    codec=chunk["byet"]
                    nested_start=soup_meta["offset"]+codec["compressedPayloadRelativeOffset"]
                    nested_end=nested_start+codec["compressedPayloadBytes"]
                    nested=b[nested_start:nested_end]
                    (args.out_dir/(f.name+f".trico-soup-{chunk['index']}.byet-j")).write_bytes(nested)

            ok.append(data)
        except Exception as ex:fail.append({"file":f.name,"reason":str(ex)})
    summary={"inputFiles":len(files),"parsed":len(ok),"rejected":fail,
      "totalNativeFreeSplatRecords":sum(row["splatStream"]["pointCount"] for row in ok),
      "soupCompressedBytes":sum(row["splatStream"]["bytes"] for row in ok),
      "meshCompressedBytes":sum(row["meshStream"]["bytes"] for row in ok),
      "goldenMatches":matching,"goldenMismatches":mismatch,"goldenCoverage":matching+mismatch,
      "codecState":"Container and codecs identified; geometry and appearance bitstreams not yet decompressed",
      "samples":ok[:4]}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if fail or mismatch:sys.exit(1)

if __name__=="__main__":main()
