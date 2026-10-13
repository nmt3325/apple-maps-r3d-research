#!/usr/bin/env python3
"""Stage already captured R3D tiles for a future *fully* native-free Flyover decoder.

Produces original HEIC atlases, untouched TRICO Splat and mesh bitstreams, and
per-tile georeference / quantization / Splat record metadata. No Apple APIs or
native system decoder. Does NOT yet produce decoded polygons or Splat XYZ.

Usage:
 python3 /opt/flyover-viewer/nativefree_prepare_region.py \
    --name oahu-hilton --input-dir /path/to/captured/r3d \
    --output-root /opt/flyover-viewer/nativefree-regions
"""
from __future__ import annotations
import argparse,json,os,re,struct
from pathlib import Path
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_extract_heic import metadata,find_heic_payloads

def prepare(folder:Path,output:Path,name:str):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,70}",name):
        raise ValueError("Only simple region names: [a-z0-9_-], 1 to 71 chars")
    files=sorted(folder.glob("*.r3d"))
    if not files:raise ValueError("No *.r3d input files")
    root=output/name
    if root.exists():raise FileExistsError(f"Region already exists: {root}. Preserve previous exports, choose another --name.")
    root.mkdir(parents=True,mode=0o700)
    (root/"heic").mkdir(mode=0o700)
    (root/"compressed").mkdir(mode=0o700)
    report=[]
    for f in files:
        b=f.read_bytes()
        info=dissect(b)
        ecef=metadata(b)
        images=find_heic_payloads(b)
        if len(images)!=3:raise ValueError(f"{f.name}: unexpected number of HEIC images: {len(images)}")
        fileset={}
        for i,(start,content,boxes) in enumerate(images):
            dest=root/"heic"/(f.stem+f".{i}.heic")
            dest.write_bytes(content)
            fileset[f"atlas{i}"]="heic/"+dest.name
        for key,extension in (("splatStream",".trico-soup"),("meshStream",".trico-mesh")):
            raw=info[key]
            chunk=b[raw["offset"]:raw["offset"]+raw["bytes"]]
            dest=root/"compressed"/(f.stem+extension)
            dest.write_bytes(chunk)
            fileset[key]="compressed/"+dest.name
        # Standalone nested BYET J byte-plane compressed streams: feed these
        # to a future pure-Linux entropy decoder without re-parsing source R3D.
        meta=info["splatStream"]
        lane_dirs=[]
        for frame in meta["blocks"]:
            codec=frame["byet"]
            start=meta["offset"]+codec["compressedPayloadRelativeOffset"]
            end=start+codec["compressedPayloadBytes"]
            ext=f".splat-frame-{frame['index']}.byet-j"
            dest=root/"compressed"/(f.stem+ext)
            payload=b[start:end]
            dest.write_bytes(payload)
            fileset[f"byetJ{frame['index']}"]="compressed/"+dest.name
            lane_dirs.append(split_j(payload,12 if frame["index"]==0 else 32))
        item={"source":f.name,"size":len(b),"splatRecords":info["splatStream"]["pointCount"],
              "splatChannels":info["splatStream"]["channelCount"],
              "xyzLocalLowerAnchorMeters":info["splatStream"]["blocks"][0]["lowerAnchorXYZMeters"],
              "xyzAnchorCodec":info["splatStream"]["blocks"][0]["originCodec"],
              "splatQuantization":info["splatStream"]["quantizationSteps"],
              "meshQuantization":info["meshStream"]["quantizationSteps"],
              "splatCompressedFrames":info["splatStream"]["blocks"],
              "JByteLaneDirectories":lane_dirs,
              "translationECEF":ecef["ecefTranslation"],
              "rotationR":ecef["matrixR3x3"],"files":fileset}
        report.append(item)
    manifest={"region":name,"originalR3DTiles":len(report),
              "splatsNotYetXYZDecoded":sum(x["splatRecords"] for x in report),
              "totalHEICAtlases":len(report)*3,
              "decodedQuantizedXYZLowerAnchors":sum(t["xyzLocalLowerAnchorMeters"] is not None for t in report),
              "nestedBYETJStreams":len(report)*2,
              "JLaneDirectoriesDecoded":len(report)*2,
              "nativeCodeUsed":False,
              "hasDecodedPolygonMesh":False,"hasDecodedSplatXYZ":False,
              "pipelineState":"R3D network tiles -> independent TLV parser -> TRICO compressed streams + original HEIC; geometry codec port pending",
              "tiles":report}
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    (root/"README.txt").write_text(
        f"Region: {name}\nSource files: {len(report)}\n"
        f"Native-free Splat record count (header only): {manifest['splatsNotYetXYZDecoded']}\n"
        "The .trico-soup, .trico-mesh and .byet-j files are compressed, NOT reconstructed geometry.\n"
        "HEIC image atlases and R3D georeferences are original network data.\n"
        "This directory is separate from the existing Tokyo viewer to avoid overwriting it.\n")
    print(json.dumps({"created":str(root),"r3d":len(report),"splatRecords":manifest["splatsNotYetXYZDecoded"],
      "originalHEIC":manifest["totalHEICAtlases"],"meshDecoded":False,"splatsXYZDecoded":False},ensure_ascii=False,indent=2))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--input-dir",required=True,type=Path)
    p.add_argument("--output-root",default=Path("/opt/flyover-viewer/nativefree-regions"),type=Path)
    args=p.parse_args()
    prepare(args.input_dir,args.output_root,args.name)
if __name__=="__main__":main()
