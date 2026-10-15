#!/usr/bin/env python3
"""Inventory a local macOS Maps/VectorKit build without distributing Apple binaries."""
import argparse
import bisect
import hashlib
import json
import re
import struct
import subprocess
import uuid
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def macho(data):
    """Read 64-bit little-endian slices, with offsets relative to each slice."""
    if data[:4] == b'\xca\xfe\xba\xbe':
        count, = struct.unpack_from('>I', data, 4)
        offsets = [struct.unpack_from('>5I', data, 8 + 20*i)[2:4] for i in range(count)]
    else:
        offsets = [(0, len(data))]
    slices = []
    for start, size in offsets:
        blob = memoryview(data)[start:start+size]
        magic, cpu, subtype, kind, count, commands_size, flags, _ = struct.unpack_from('<8I', blob)
        if magic != 0xfeedfacf:
            raise ValueError('expected a 64-bit little-endian Mach-O')
        row = dict(cpu=hex(cpu), subtype=hex(subtype), filetype=kind,
                   file_offset=start, size=size, segments=[], sections=[])
        cursor = 32
        for _ in range(count):
            command, length = struct.unpack_from('<II', blob, cursor)
            if length < 8 or cursor + length > 32 + commands_size:
                raise ValueError('invalid load command')
            if command == 0x1b:
                row['uuid'] = str(uuid.UUID(bytes=bytes(blob[cursor+8:cursor+24]))).upper()
            elif command == 0x32:
                platform, minimum, sdk, _ = struct.unpack_from('<4I', blob, cursor+8)
                version = lambda v: f'{v >> 16}.{(v >> 8) & 255}.{v & 255}'
                row['build'] = dict(platform=platform, minimum=version(minimum), sdk=version(sdk))
            elif command == 0x19:
                name, address, vm_size, offset, file_size, _, _, nsections, _ = struct.unpack_from('<16s4Q4I', blob, cursor+8)
                name = name.split(b'\0')[0].decode()
                row['segments'].append(dict(name=name, address=address, vm_size=vm_size,
                                             offset=offset, file_size=file_size))
                for j in range(nsections):
                    sname, segname, addr, slen, off = struct.unpack_from('<16s16sQQI', blob, cursor+72+j*80)
                    row['sections'].append(dict(name=sname.split(b'\0')[0].decode(),
                        segment=segname.split(b'\0')[0].decode(), address=addr, size=slen, offset=off))
            cursor += length
        slices.append(row)
    return slices


def symbols(path):
    raw = subprocess.run(['nm', '-nm', str(path)], capture_output=True, text=True, check=True).stdout
    text = subprocess.run(['c++filt'], input=raw, capture_output=True, text=True, check=True).stdout
    result = []
    for line in text.splitlines():
        match = re.match(r'([0-9a-fA-F]+) \(__TEXT,__text\) (?:non-external|external) (.*)', line)
        if match:
            result.append((int(match[1], 16), match[2]))
    return sorted(result)


def inventory(vector, sample, raw_dir):
    result = {'scope': 'macOS binaries; static VM addresses are build-specific', 'binaries': {}}
    maps = Path('/System/Applications/Maps.app/Contents/MacOS/Maps')
    metal = Path('/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/default.metallib')
    for name, path in [('Maps', maps), ('VectorKit', vector), ('default.metallib', metal)]:
        data = path.read_bytes()
        result['binaries'][name] = dict(bytes=len(data), sha256=sha256(data))
        if name != 'default.metallib':
            result['binaries'][name]['slices'] = macho(data)
    vk = result['binaries']['VectorKit']['slices'][0]
    if len(result['binaries']['VectorKit']['slices']) != 1 or vk['file_offset'] != 0:
        raise ValueError('--vector-kit must be an extracted thin Mach-O')
    if sample:
        data = sample.read_bytes()
        text = data.decode()
        match = re.search(r'(0x[0-9a-f]+)\s+-\s+0x[0-9a-f]+\s+com\.apple\.VectorKit\s+\(([^)]+)\)\s+<([^>]+)>', text)
        if not match:
            raise ValueError('no loaded VectorKit identity in sample')
        load = int(match[1], 16)
        base = next(s['address'] for s in vk['segments'] if s['name'] == '__TEXT')
        footprint = re.search(r'^Physical footprint:\s+(.*)$', text, re.MULTILINE)
        peak = re.search(r'^Physical footprint \(peak\):\s+(.*)$', text, re.MULTILINE)
        result['native_sample'] = dict(sha256=sha256(data), vector_kit_uuid=match[3].upper(),
            vector_kit_version=match[2], vector_kit_live_base=hex(load), extracted_segment_base_delta=hex(load-base),
            extracted_uuid_matches=match[3].upper() == vk['uuid'],
            physical_footprint=footprint[1] if footprint else None,
            peak_footprint=peak[1] if peak else None,
            caveat='Short idle sample. Footprint is the whole app. Extracted segment base delta is not a verified dyld slide: extractors can rewrite segment headers.')
    syms = symbols(vector)
    needles = ['R3dResourceDecoder::decode(', 'C3mResourceDecoder::decode(', 'createSplats(',
        '_r3d_world_read_mem', '_r3d_world_free', '_huff8_decompress', '_huff16_decompress',
        '_huff816_decompress', '_byet_decompress', '_bytes_decompress', '_key16_decompress',
        '_trico_mesh_decompress', '_trico_soup_decompress', 'decodeEdgebreakerMesh(',
        'readMeshChunkType', 'readTextureData(', 'ggl::FlyoverSplatsShader::']
    selected = [(a,n) for a,n in syms if any(needle in n for needle in needles)]
    result['functions'] = [dict(address=hex(a), name=n) for a,n in selected]
    data = vector.read_bytes()
    text = next(s for s in vk['sections'] if s['name'] == '__text')
    result['extracted_text_prefix4096_sha256'] = sha256(data[text['offset']:text['offset']+min(4096,text['size'])])
    starts = sorted(set(a for a,_ in syms))
    names = {a:n for a,n in syms}
    edges = []
    for address, name in selected:
        stop = starts[bisect.bisect_right(starts,address)] if address < starts[-1] else text['address']+text['size']
        offset = text['offset'] + address - text['address']
        for delta in range(0, stop-address, 4):
            instruction, = struct.unpack_from('<I', data, offset+delta)
            if instruction & 0xfc000000 != 0x94000000:
                continue
            immediate = instruction & 0x3ffffff
            if immediate & 0x2000000:
                immediate -= 0x4000000
            target = address + delta + immediate*4
            if target in names and any(k in names[target] for k in needles):
                edges.append(dict(caller=name, callsite=hex(address+delta), target=hex(target), callee=names[target]))
    result['direct_bl_edges'] = edges
    # Raw AIR and reflection stay local. Commit hashes and selected field metadata only.
    if raw_dir:
        raw_dir.mkdir(parents=True, exist_ok=True)
        for filename, options in [('reflection.txt',['--reflection']), ('metal-ir.txt',['--disassemble-symbols=Flyover::splat_vertex'])]:
            path = raw_dir / filename
            with path.open('w') as stream:
                subprocess.run(['xcrun','metal-objdump','--metallib',*options,str(metal)],stdout=stream,check=True)
        reflection = (raw_dir/'reflection.txt').read_text()
        decoder = json.JSONDecoder()
        selected_reflections = {}
        for match in re.finditer(r'Reflection No\. (\d+):\s*',reflection):
            module,_ = decoder.raw_decode(reflection,match.end())
            nodes = module.get('nodes',[])
            function = next((n['node']['name'] for n in nodes if n['node_type'] in ['VertexFunction','FragmentFunction']), None)
            if function not in ['Flyover::splat_vertex','Flyover::splat_fragment']:
                continue
            structures = [n for n in nodes if n['node'].get('type_name') in [
                'FlyoverCommon::SplatConstants','FlyoverCommon::SplatProperties','Flyover::SharedSplatsArgumentBuffer','Flyover::SplatsArgumentBuffer']]
            selected_reflections[function] = dict(reflection_index=int(match[1]), structures=structures)
        result['shader_reflection'] = selected_reflections
        ir = (raw_dir/'metal-ir.txt').read_text()
        modules = re.split(r'(?m)^(0x[0-9a-f]+) -- (.+):\n',ir)
        result['shader_ir'] = {}
        for i in range(1,len(modules),3):
            _,name,body = modules[i:i+3]
            if name.startswith('Flyover::'):
                triple = re.search(r'target triple = "([^"]+)"', body)
                result['shader_ir'][name] = dict(sha256=sha256(body.encode()), bytes=len(body.encode()),
                    target_triple=triple[1] if triple else None,
                    function_constants=[dict(name=n,index=int(index)) for n,index in re.findall(
                        r'!"bool", !"(Flyover::[^"]+)", i32 (\d+), i1 (?:true|false)',body)])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vector-kit', type=Path, required=True, help='Extracted thin macOS VectorKit Mach-O, not an iOS dylib')
    parser.add_argument('--native-sample', type=Path)
    parser.add_argument('--raw-dir', type=Path, help='Local-only output directory for Apple AIR/reflection')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.vector_kit,args.native_sample,args.raw_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(dict(output=str(args.output),functions=len(report['functions']),direct_bl_edges=len(report['direct_bl_edges']),
        uuid_matches=report.get('native_sample',{}).get('extracted_uuid_matches')),indent=2))


if __name__ == '__main__':
    main()
