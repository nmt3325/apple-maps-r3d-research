"""Bounded in-process adapter for the audited independent R3D decoder.

No network, subprocess, numpy, or server is used by this module.
"""
import gzip
import io
import json
import struct
from array import array
import sys
from nativefree_soup import decode_soup
from nativefree_mesh import decode_mesh
from nativefree_extract_heic import find_heic_payloads, metadata
from nativefree_splat_material import pack_material20
from nativefree_validate import validate_arrays
from c3mm_v2_parser import parse

MAX_RAW = 16_000_000


def unpack_response(raw):
    if len(raw) > MAX_RAW:
        raise ValueError('Response size limit')
    if raw.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_RAW + 1)
    if len(raw) > MAX_RAW:
        raise ValueError('Expanded response size limit')
    return raw


def height_index(raw):
    sections, cells = parse(unpack_response(raw), True)
    header = next(s for s in sections if s['tag'] == 0)
    return {'json': json.dumps({'tile': header['decodedTile'],
                                'cells': sorted(cells)}).encode()}


def decode_tile(raw):
    raw = unpack_response(raw)
    if not raw.startswith(bytes.fromhex('3d96592e02000000')):
        raise ValueError('Unsupported R3D version')
    soup, mesh = decode_soup(raw), decode_mesh(raw)
    validate_arrays(soup, mesh)
    if mesh['faceCount'] > 500_000 or soup.count > 500_000:
        raise ValueError('Tile geometry budget exceeded')
    positions = list(struct.iter_unpack('<3f', mesh['positions_f32']))
    position_bytes, normal_bytes, uv_bytes = (mesh[k] for k in
        ('positions_f32', 'normals_f32', 'uv_f32'))
    vertices, indices, unique = bytearray(), array('I'), {}
    for p, t, n in zip(mesh['faces'], mesh['uv_indices'], mesh['normal_indices']):
        key = p, t, n
        index = unique.get(key)
        if index is None:
            index = len(unique)
            unique[key] = index
            # Metal uses packed float3/float3/float2, exactly 32 bytes.
            vertices.extend(position_bytes[p*12:p*12+12])
            vertices.extend(normal_bytes[n*12:n*12+12])
            vertices.extend(uv_bytes[t*8:t*8+8])
        indices.append(index)
    if sys.byteorder != 'little':
        indices.byteswap()
    colors = pack_material20(soup.attributes_f32)
    splats = bytearray()
    xyz = list(struct.iter_unpack('<3f', soup.xyz_f32))
    for i in range(soup.count):
        rgba = colors[i*20:i*20+4]
        if not rgba[3]:
            continue
        color = struct.pack('<4f', *(c/255 for c in rgba))
        for v in range(3):
            at = (3*i+v)*12
            splats.extend(soup.xyz_f32[at:at+12])
            splats.extend(color)
            splats.extend(BARYCENTRIC[v])
    all_points = positions + xyz
    # validate_arrays already checks every source position for finiteness.
    if not all_points:
        raise ValueError('Nonfinite or missing tile geometry')
    lower = [min(p[k] for p in all_points) for k in range(3)]
    upper = [max(p[k] for p in all_points) for k in range(3)]
    images = find_heic_payloads(raw)
    info = {'transform': metadata(raw), 'min': lower, 'max': upper,
            'meshTriangles': mesh['faceCount'], 'splatVertices': len(splats)//40,
            'vertexCount': len(unique), 'atlasDimensions': mesh['atlasDimensions']}
    return {'json': json.dumps(info).encode(), 'vertices': bytes(vertices),
            'indices': indices.tobytes(), 'splats': bytes(splats),
            'atlas': images[0][1] if mesh['faceCount'] else b''}


BARYCENTRIC = tuple(struct.pack('<3f', *(1.0 if k == v else 0.0 for k in range(3)))
                    for v in range(3))
