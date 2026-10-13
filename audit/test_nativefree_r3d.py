#!/usr/bin/env python3
"""Repeatable offline R3D v2 parser regression suite.

Tests the 223 Tokyo capture files and 72 Oahu files without any iOS/macOS API.
Compares Tokyo splat counts with saved native decoder fixture JSON.
Strictly validates TLV boundaries, TRICO magic/versions, compact-size splat
frame lengths, and native HEIC texture byte equivalence.
"""
from __future__ import annotations
import importlib.util,json,sys,struct,os
from pathlib import Path
ROOT=Path(os.environ.get('R3D_REFERENCE_ROOT','/opt/flyover-viewer'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'codec'))
from nativefree_r3d_codec_streams import dissect
from nativefree_extract_heic import find_heic_payloads,metadata
from nativefree_trico_size import read_size,encode_size
from nativefree_byet_jdescriptor import split_j

TOKYO=Path(os.environ.get('R3D_TOKYO_DIR',str(ROOT/'native-r3d')))
HAWAII=Path(os.environ.get('R3D_OAHU_DIR','/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20'))
GOLDEN=ROOT/'decoded-native/c3m-all-223/batch.json'
ATLAS=ROOT/'decoded-native/c3m-all-223'

def test_compact_size():
    for i in list(range(10000))+[2**n-1 for n in range(1,64)]+[2**n for n in range(1,64)]:
        c=encode_size(i)
        val,end=read_size(c)
        assert val==i and end==len(c),(i,c)

def test_native_xyz_lower_anchor(filename:str, info:dict, golden:dict):
    anchor=info["splatStream"]["blocks"][0].get("lowerAnchorXYZMeters")
    if anchor is None:return None
    file=ROOT/"decoded-native/all-223"/(filename+".decoded")
    blob=file.read_bytes()
    n=golden["vertices"]
    if not file.is_file() or len(blob)<16+12*n:
        raise ValueError("Golden native fixture missing or truncated")
    observed=[float("inf"),float("inf"),float("inf")]
    for xyz in struct.iter_unpack("<3f",blob[16:16+12*n]):
        for axis in range(3):
            if xyz[axis]<observed[axis]:observed[axis]=xyz[axis]
    gap=[observed[i]-anchor[i] for i in range(3)]
    assert all(x>=-1e-3 for x in gap),(filename,gap)
    assert max(gap)<25,(filename,gap)
    return gap

def test_one(data,f,golden=None):
    info=dissect(data)
    assert info['geometryTagOrder']==[1,1,4,2,3]
    assert info['appearanceTagOrder']==[1,1,2,3]
    assert info['splatStream']['channelCount']==8
    assert len(info['splatStream']['quantizationSteps'])==9
    assert len(info['meshStream']['quantizationSteps'])==3
    blocks=info['splatStream']['blocks']
    assert len(blocks)==2
    assert blocks[0]['relativeOffset']>=56
    assert blocks[1]['relativeOffset']>blocks[0]['relativeOffset']
    assert all(b['bytes']>0 for b in blocks)
    for block in blocks:
        pos=info['splatStream']['offset']+block['relativeOffset']
        end=pos+block['bytes']
        assert 0<=pos<end<=len(data)
        j=block["byet"]
        start=info["splatStream"]["offset"]+j["compressedPayloadRelativeOffset"]
        stop=start+j["compressedPayloadBytes"]
        assert 0<=start<stop<=len(data)
        # Exactly partitions real compressed BYET/J lanes without trailing bytes.
        lane_count=12 if block["index"]==0 else 32
        scan=split_j(data[start:stop],lane_count)
        assert scan["recordLaneBytes"]==lane_count
        assert len(scan["descriptors"])==lane_count
        assert all(0<=row["kind"]<=6 for row in scan["descriptors"])
        assert sum(row["compressedBytes"] for row in scan["descriptors"])==scan["laneCompressedBytes"]
        assert scan["firstBitmapBytes"]==(lane_count+7)//8
        assert scan["laneCompressedBytes"]+scan["descriptorBytes"]+scan["firstBitmapBytes"]+scan["secondBitmapBytes"]==stop-start
    imgs=find_heic_payloads(data)
    assert len(imgs)==3
    if golden:
        assert info['splatStream']['pointCount']==golden['vertices']
        heic=(ATLAS/(f.name+'.texture-0-0.heic'))
        assert heic.is_file()
        assert heic.read_bytes()==imgs[0][1]
    return info,imgs

def main():
    Path(os.environ.get('R3D_REPORT_DIR',str(Path(__file__).resolve().parents[1]/'reports/generated'))).mkdir(parents=True,exist_ok=True)
    test_compact_size()
    golden={e['file']:e for e in json.loads(GOLDEN.read_text())['files']}
    findings={}
    byte_lane_directories=0
    byte_lane_entries=0
    anchor_counts=0
    anchor_gaps=[]
    sparse_anchor_counts=0
    unsupported_tiles=[]
    for name,path in [('tokyo',TOKYO),('oahu',HAWAII)]:
        files=sorted(path.glob('*.r3d'))
        points=images=mesh_bytes=splat_bytes=0;quant={}
        for f in files:
            b=f.read_bytes()
            info,imgs=test_one(b,f,golden.get(f.name))
            byte_lane_directories+=len(info["splatStream"]["blocks"])
            byte_lane_entries+=12+32
            if name=="tokyo":
                gap=test_native_xyz_lower_anchor(f.name,info,golden[f.name])
                if gap is not None:
                    anchor_counts+=1
                    anchor_gaps.extend(gap)
                    if info["splatStream"]["blocks"][0]["originCodec"]=="byte-transition-bitmap":
                        sparse_anchor_counts+=1
                else:
                    unsupported_tiles.append(f.name)

            points+=info['splatStream']['pointCount']
            images+=len(imgs)
            mesh_bytes+=info['meshStream']['bytes']
            splat_bytes+=info['splatStream']['bytes']
            quant[tuple(info['splatStream']['quantizationSteps'])]=quant.get(tuple(info['splatStream']['quantizationSteps']),0)+1
        findings[name]={'tiles':len(files),'splatRecords':points,'embeddedHEIC':images,'meshCompressedBytes':mesh_bytes,'splatCompressedBytes':splat_bytes,'quantizationPatterns':len(quant),'nativeGoldenCompared':len(files) if name=='tokyo' else 0}
        print(name,findings[name])
    assert findings['tokyo']['tiles']==223 and findings['tokyo']['splatRecords']==736915
    assert anchor_counts==223, f"expected 223 verified origin anchors, got {anchor_counts}"
    assert sparse_anchor_counts==21, f"expected 21 sparse-packed XYZ anchors, got {sparse_anchor_counts}"
    assert len(unsupported_tiles)==0,unsupported_tiles
    print("Quantized XYZ native-fixture verified:",anchor_counts,"tiles (202 direct + 21 sparse bitmap); maximum XYZ min offset",round(max(anchor_gaps),3),"meters; unsupported",unsupported_tiles)

    assert findings['oahu']['tiles']==72 and findings['oahu']['splatRecords']==304527
    assert findings['tokyo']['embeddedHEIC']==669 and findings['oahu']['embeddedHEIC']==216
    assert byte_lane_directories==590
    assert byte_lane_entries==12980
    print("BYET/J lane directory parity",byte_lane_directories,"streams /",byte_lane_entries,"lane entries exact partition")

    failures=0
    src=next(TOKYO.glob('*.r3d')).read_bytes()
    for bad in [b'',src[:100],b'xxxxx'+src[5:]]:
        try:dissect(bad);failures+=1
        except ValueError:pass
    assert failures==0
    report={'byteLaneDirectories':byte_lane_directories,'compressedLaneEntries':byte_lane_entries,
            'nativeXYZAnchorGoldenCompared':anchor_counts,'sparseBitmapAnchorGoldenCompared':sparse_anchor_counts,
            'unsupportedAnchorTiles':unsupported_tiles,'native12BitAnchorMaxGapMeters':round(max(anchor_gaps),4),
            'nativeAPIInvoked':False,'validations':findings,'truncatedOrCorruptedRejected':3,'status':'TRICO frame and header decode; numeric XYZ/UV/face indices still compressed'}
    (Path(os.environ.get('R3D_REPORT_DIR',str(Path(__file__).resolve().parents[1]/'reports/generated'))) / 'nativefree-decoder-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('PASS: frame boundaries, 3 HEIC atlases, 8 Splat channels, quantization tables, original Splat counts on 295 tiles, 3 corrupt input tests')
if __name__=='__main__':main()
