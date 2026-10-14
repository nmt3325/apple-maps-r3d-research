"""Independent TRICO v3 polygon decoder (in development)."""
from __future__ import annotations

import struct
import math
from nativefree_extract_heic import find_heic_payloads, image_dimensions
from nativefree_r3d_codec_streams import dissect
from nativefree_mesh_topology import decode_topology, read_block, read_signed, next_corner, prev_corner


def f32(value: float) -> float:
    return struct.unpack('<f', struct.pack('<f', value))[0]


def signed_half(value: int) -> int:
    return value // 2 if value >= 0 else -((-value) // 2)


def reconstruct_quantized(faces: list[int], opposite: list[int], residuals: bytes,
                          channels: int) -> bytes:
    if len(residuals) % (channels * 4):
        raise ValueError("Invalid mesh residual shape")
    count = len(residuals) // (channels * 4)
    delta = [((v[0] >> 1) ^ -(v[0] & 1)) for v in struct.iter_unpack('<i', residuals)]
    positions = [None] * count
    seen = bytearray(len(faces) // 3)
    predictor = [0] * channels

    def assign(vertex: int) -> None:
        positions[vertex] = [predictor[k] + delta[vertex * channels + k]
                             for k in range(channels)]

    for triangle in range(len(seen)):
        if seen[triangle]:
            continue
        a, b, c = faces[3 * triangle:3 * triangle + 3]
        if positions[a] is None:
            assign(a)
        if positions[b] is None:
            predictor = positions[a].copy()
            assign(b)
        if positions[c] is None:
            predictor = [signed_half(positions[a][k] + positions[b][k] + 1)
                         for k in range(channels)]
            assign(c)
        queue = [triangle]
        seen[triangle] = 1
        for current in queue:
            for corner in range(3 * current, 3 * current + 3):
                other = opposite[corner]
                if other == -1:
                    continue
                if not 0 <= other < len(faces):
                    raise ValueError("Mesh adjacency out of range")
                vertex = faces[other]
                if positions[vertex] is None:
                    a = positions[faces[next_corner(corner)]]
                    b = positions[faces[prev_corner(corner)]]
                    c = positions[faces[corner]]
                    predictor = [a[k] + b[k] - c[k] for k in range(channels)]
                    assign(vertex)
                adjacent = other // 3
                if not seen[adjacent]:
                    seen[adjacent] = 1
                    queue.append(adjacent)
    if any(p is None for p in positions):
        raise ValueError("Mesh predictor did not visit every vertex")
    return struct.pack('<' + 'i' * (count * channels),
                       *(v for position in positions for v in position))


def decode_mesh_positions(raw: bytes) -> dict:
    frame = dissect(raw)['meshStream']
    src = raw[frame['offset']:frame['offset'] + frame['bytes']]
    if struct.unpack_from('<I', src, 4)[0] != 3:
        raise ValueError("Only TRICO v3 mesh is supported")
    steps = struct.unpack_from('<3f', src, 8)
    topology = decode_topology(src)
    residuals, at = read_block(src, topology['nextOffset'], topology['vertices'], 12)
    quantized = reconstruct_quantized(topology['faces'], topology['opposite'], residuals, 3)
    vertices = b''.join(struct.pack('<f', f32(v[0]) * steps[0])
                        for v in struct.iter_unpack('<i', quantized))
    return {**topology, 'positions_f32': vertices, 'nextOffset': at,
            'steps': steps, 'src': src}


def build_adjacency(faces: list[int]) -> list[int]:
    from collections import defaultdict, deque
    pending = defaultdict(deque)
    opposite = [-1] * len(faces)
    for corner, vertex in enumerate(faces):
        other = faces[next_corner(corner)]
        matches = pending[(other, vertex)]
        if matches:
            earlier = matches.popleft()
            a, b = prev_corner(earlier), prev_corner(corner)
            opposite[a] = b
            opposite[b] = a
        else:
            pending[(vertex, other)].append(corner)
    return opposite


def rebuild_uv_indices(faces: list[int], opposite: list[int], mask: bytes,
                       patch_materials: list[int]) -> tuple[list[int], list[int], int]:
    triangles = len(faces) // 3
    if len(mask) != (triangles + 1) // 2:
        raise ValueError("UV seam mask length mismatch")
    flags = [(mask[i // 2] >> (i % 2 * 4)) & 15 for i in range(triangles)]
    seen = bytearray(triangles)
    uv_indices = [-1] * len(faces)
    face_materials = [-1] * triangles
    count = patch = 0
    adjacency = opposite.copy()
    for seed in range(triangles):
        if seen[seed]:
            continue
        if patch >= len(patch_materials):
            raise ValueError("Not enough UV patch materials")
        local = {}
        stack = [seed]
        seen[seed] = 1
        while stack:
            current = stack.pop()
            face_materials[current] = patch_materials[patch]
            for edge in range(3):
                corner = current * 3 + edge
                vertex = faces[corner]
                if vertex not in local:
                    local[vertex] = count
                    count += 1
                uv_indices[corner] = local[vertex]
                other = adjacency[corner]
                if other == -1:
                    continue
                adjacent = other // 3
                if flags[current] >> edge & 1 == 0 and not seen[adjacent]:
                    seen[adjacent] = 1
                    stack.append(adjacent)
                adjacency[corner] = adjacency[other] = -1
        patch += 1
    if patch != len(patch_materials):
        raise ValueError("Unused UV patch materials")
    return uv_indices, face_materials, count


def decode_mesh_uv(raw: bytes) -> dict:
    mesh = decode_mesh_positions(raw)
    src, at = mesh['src'], mesh['nextOffset']
    flags_bits, at = read_signed(src, at)
    if flags_bits:
        flags_raw, at = read_block(src, at, (flags_bits * mesh['vertices'] + 7) // 8, 1)
    else:
        flags_raw = b''
    has_uv, at = read_signed(src, at)
    if mesh['faceCount']==0:
        if flags_bits or has_uv:raise ValueError('Unexpected stream in empty polygon mesh')
        return {**mesh,'uv_f32':b'','uv_pixels_f32':b'','atlasDimensions':None,
                'uv_indices':[],'face_materials':[],'uvCount':0,'vertexFlagsBits':0,
                'vertexFlagsPacked':b'','nextOffset':at}
    if not has_uv:
        raise ValueError("TRICO mesh has no UV stream")
    declared_uv, at = read_signed(src, at)
    seams, at = read_block(src, at, (mesh['faceCount'] + 1) // 2, 1)
    patches, at = read_signed(src, at)
    raw_materials, at = read_block(src, at, patches, 4)
    materials = [x[0] for x in struct.iter_unpack('<i', raw_materials)]
    indices, face_materials, count = rebuild_uv_indices(mesh['faces'], mesh['opposite'], seams, materials)
    if count != declared_uv:
        raise ValueError(f"UV count mismatch {count} != {declared_uv}")
    adjacency = build_adjacency(indices)
    residuals, at = read_block(src, at, count, 8)
    quantized = reconstruct_quantized(indices, adjacency, residuals, 2)
    uv = b''.join(struct.pack('<f', f32(v[0]) * mesh['steps'][1])
                  for v in struct.iter_unpack('<i', quantized))
    images = find_heic_payloads(raw)
    if not images or any(v != 0 for v in face_materials):
        raise ValueError("Unsupported mesh material atlas assignment")
    width, height = image_dimensions(images[0][1])
    reciprocal = (f32(1 / width), f32(1 / height))
    normalized = b''.join(struct.pack('<f', v[0] * reciprocal[i % 2])
                          for i, v in enumerate(struct.iter_unpack('<f', uv)))
    return {**mesh, 'uv_f32': normalized, 'uv_pixels_f32': uv,
            'atlasDimensions': (width, height),
            'uv_indices': indices, 'face_materials': face_materials,
            'uvCount': count, 'vertexFlagsBits': flags_bits, 'vertexFlagsPacked': flags_raw,
            'nextOffset': at}


def decode_mesh(raw: bytes) -> dict:
    mesh = decode_mesh_uv(raw)
    src, at = mesh['src'], mesh['nextOffset']
    has_normals, at = read_signed(src, at)
    if mesh['faceCount']==0:
        if has_normals or at!=len(src):raise ValueError('Invalid empty mesh normal stream/trailing bytes')
        return {**mesh,'normals_f32':b'','normal_indices':[],'normalCount':0,'normalWords':b'','nextOffset':at}
    if not has_normals:
        raise ValueError("Mesh normal stream is absent")
    variant, at = read_signed(src, at)
    if variant != 0:
        raise ValueError("Unsupported mesh normal variant")
    normal_count, at = read_signed(src, at)
    selector_count, at = read_signed(src, at)
    packed, at = read_block(src, at, normal_count, 4)
    selectors, at = read_block(src, at, selector_count, 1)
    if at != len(src):
        raise ValueError("Mesh streams do not cover input")
    per_vertex = [[] for _ in range(mesh['vertices'])]
    indices = []
    cursor = count = 0
    for vertex in mesh['faces']:
        records = per_vertex[vertex]
        if not records:
            records.append(count)
            count += 1
            index = records[0]
        else:
            if cursor >= len(selectors):
                raise ValueError("Missing normal selector")
            selector = selectors[cursor]
            cursor += 1
            if selector == 0:
                index = count
                records.append(count)
                count += 1
            elif selector <= len(records):
                index = records[selector - 1]
            else:
                raise ValueError("Normal selector outside vertex instances")
        indices.append(index)
    if count != normal_count or cursor != len(selectors):
        raise ValueError("Mesh normal count/selector consumption mismatch")
    step = mesh['steps'][2]
    minus_pi = struct.unpack('<f', bytes.fromhex('db0f49c0'))[0]
    epsilon = f32(1e-6)
    normals = bytearray()
    for (word,) in struct.iter_unpack('<I', packed):
        theta = f32((word >> 16) * step)
        sin_theta = f32(math.sin(theta))
        cos_theta = f32(math.cos(theta))
        phi = f32(f32(f32((word & 65535) * step) / max(sin_theta, epsilon)) + minus_pi)
        x = f32(f32(math.cos(phi)) * sin_theta)
        y = f32(f32(math.sin(phi)) * sin_theta)
        normals.extend(struct.pack('<3f', x, y, cos_theta))
    return {**mesh, 'normals_f32': bytes(normals), 'normal_indices': indices,
            'normalCount': count, 'normalWords': packed, 'nextOffset': at}
