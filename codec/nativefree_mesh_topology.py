"""TRICO v3 CLERS topology from bitmap tokens and boundary corner pairs.

Independent reconstruction of saved static mesh instructions at
0x1b7097500..0x1b7098970. No golden array is needed at runtime.
"""
from __future__ import annotations

import struct
from nativefree_bytes import decode_byet
from nativefree_trico_size import read_size


def read_signed(src: bytes, at: int) -> tuple[int, int]:
    if at >= len(src):
        raise ValueError("Truncated TRICO signed integer")
    first = src[at]
    at += 1
    value = first & 63
    continuation = first & 64
    shift = 6
    for _ in range(9):
        if not continuation:
            return (-value if first & 128 else value), at
        if at >= len(src):
            raise ValueError("Truncated TRICO signed integer tail")
        byte = src[at]
        at += 1
        value |= (byte & 127) << shift
        continuation = byte & 128
        shift += 7
    raise ValueError("TRICO signed integer overflow")


def read_block(src: bytes, at: int, count: int, lanes: int) -> tuple[bytes, int]:
    if not count:
        return b'', at
    size, begin = read_size(src, at)
    end = begin + size
    if end > len(src):
        raise ValueError("TRICO BYET block exceeds input")
    return decode_byet(src[begin:end], count, lanes), end


def next_corner(corner: int) -> int:
    return corner // 3 * 3 + (corner + 1) % 3


def prev_corner(corner: int) -> int:
    return corner // 3 * 3 + (corner + 2) % 3


def rebuild_topology(face_count: int, tokens: bytes, integers: list[int]
                     ) -> tuple[list[int], list[int], int]:
    if len(integers) < 4 or integers[0] != 0x5a4c0000:
        raise ValueError("Unknown TRICO topology header")
    if integers[1] != face_count or (len(integers) - 4) % 2:
        raise ValueError("Topology face count/pair length mismatch")
    vertices, boundaries = integers[-2:]
    if not 0 < vertices <= face_count * 3 or not 0 <= boundaries <= face_count:
        raise ValueError("Invalid topology vertex/boundary count")
    corners = 3 * face_count
    opposite = [-1] * corners
    faces = [-1] * corners
    for a, b in zip(integers[2:-2:2], integers[3:-2:2]):
        if a >= corners or b >= corners:
            raise ValueError("Boundary corner pair out of range")
        if a >= 0:
            opposite[a] = b
        if b >= 0:
            opposite[b] = a
    bitmap_bytes = (face_count + 7) // 8
    if len(tokens) < bitmap_bytes:
        raise ValueError("Truncated CLERS bitmap")
    bitmap = tokens[:bitmap_bytes]
    extra = tokens[bitmap_bytes:]
    codes = []
    starts = [0] * (face_count + 1)
    depth = component = extra_at = bit_at = 0
    if boundaries == 0:
        codes.append(8)
    while len(codes) < face_count:
        at = len(codes)
        if bitmap[bit_at // 8] >> (bit_at % 8) & 1:
            if extra_at // 4 >= len(extra):
                raise ValueError("Truncated CLERS two-bit tokens")
            code = 4 | ((extra[extra_at // 4] >> (extra_at % 4 * 2)) & 3)
            extra_at += 1
        else:
            code = 0
        bit_at += 1
        codes.append(code)
        if code == 7:
            if depth:
                depth -= 1
            else:
                component += 1
                if len(codes) < face_count:
                    if component < boundaries:
                        starts[component] = len(codes)
                    else:
                        codes.append(8)
        elif code == 4 and opposite[3 * at + 2] == -1:
            depth += 1
    if depth or len(codes) != face_count:
        raise ValueError("CLERS component structure incomplete")
    counter = vertices - 1
    saved = []
    triangle = face_count - 1

    def link(a: int, b: int) -> None:
        if a >= 0:
            if a >= corners:
                raise ValueError("Topology link out of range")
            opposite[a] = b
        if b >= 0:
            if b >= corners:
                raise ValueError("Topology link out of range")
            opposite[b] = a

    def close_star(corner: int, vertex: int) -> None:
        current = corner
        for _ in range(corners + 1):
            terminal = prev_corner(current)
            faces[next_corner(current)] = vertex
            adjacent = opposite[terminal]
            if adjacent < 0 or adjacent == corner:
                link(terminal, corner)
                return
            current = adjacent
        raise ValueError("Nonterminating topology star")

    def read_boundary(corner: int) -> None:
        nonlocal counter
        current = next_corner(corner)
        for _ in range(corners + 1):
            terminal = next_corner(current)
            adjacent = opposite[terminal]
            if adjacent < 0:
                current = terminal
                break
            current = adjacent
        else:
            raise ValueError("Nonterminating boundary entry")
        for _ in range(corners + 1):
            faces[next_corner(current)] = counter
            current = prev_corner(current)
            for _ in range(corners + 1):
                adjacent = opposite[current]
                if adjacent < 0:
                    break
                current = adjacent
                faces[next_corner(current)] = counter
                current = prev_corner(current)
            else:
                raise ValueError("Nonterminating boundary star")
            counter -= 1
            if faces[next_corner(current)] != -1:
                return
        raise ValueError("Nonterminating boundary ring")

    if not component:
        raise ValueError("CLERS has no completed component")
    while component > 0:
        component -= 1
        previous = -1
        while component >= boundaries or (component >= 0 and triangle >= starts[component]):
            if triangle < 0:
                raise ValueError("CLERS component underflow")
            corner = 3 * triangle
            code = codes[triangle]
            if code in (0, 4, 6):
                link(previous, corner + 1)
            elif code == 5:
                link(previous, corner + 2)
            elif code == 7:
                if previous > 0:
                    saved.append(previous)
            elif code == 8:
                link(previous, corner)
            else:
                raise ValueError("Unknown CLERS code")
            if code == 0:
                close_star(corner + 2, counter)
                counter -= 1
            elif code == 4:
                other = opposite[corner + 2]
                if other == -1:
                    if not saved:
                        raise ValueError("CLERS split stack underflow")
                    link(corner + 2, saved.pop())
                elif other <= -2:
                    link(corner + 2, -other)
                    current = corner + 2
                    for _ in range(corners + 1):
                        terminal = next_corner(current)
                        current = opposite[terminal]
                        if current < 0:
                            read_boundary(terminal)
                            break
                    else:
                        raise ValueError("Nonterminating split boundary")
            elif code == 8:
                close_star(corner + 1, counter - 2)
                close_star(corner + 2, counter - 1)
                close_star(corner, counter)
                counter -= 3
                component -= 1
            previous = corner
            triangle -= 1
        if boundaries:
            read_boundary(3 * starts[component] + 1)
            boundaries -= 1
    if counter != -1 or any(v < 0 or v >= vertices for v in faces):
        raise ValueError("Topology reconstruction did not assign all vertices")
    return faces, opposite, vertices


def decode_topology(src: bytes, at: int = 20) -> dict:
    face_count, at = read_signed(src, at)
    token_bytes, at = read_signed(src, at)
    integer_count, at = read_signed(src, at)
    if not 0 < face_count <= 10_000_000 or token_bytes < (face_count + 7) // 8:
        raise ValueError("Invalid TRICO topology sizes")
    first_count = (face_count + 7) // 8
    bitmap, at = read_block(src, at, first_count, 1)
    extra, at = read_block(src, at, token_bytes - first_count, 1)
    header, at = read_block(src, at, integer_count, 4)
    integers = [x[0] for x in struct.iter_unpack('<i', header)]
    faces, opposite, vertices = rebuild_topology(face_count, bitmap + extra, integers)
    return {'faces': faces, 'opposite': opposite, 'vertices': vertices,
            'faceCount': face_count, 'nextOffset': at,
            'tokenBytes': token_bytes, 'integerCount': integer_count}
