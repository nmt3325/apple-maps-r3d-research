"""Independent BYET/J byte-plane predictors from the inert ARM64 capture.

No native instructions or golden arrays are used by this module. Huff counts
come from compact integers in each lane, not estimated from the stream size.
"""
from __future__ import annotations

import struct
from nativefree_trico_size import read_size
from nativefree_byet_jdescriptor import split_j
from nativefree_huff_aligned import decode_symbols


def decode_huff(src: bytes, count: int, width: int) -> bytes:
    if len(src) < 4:
        raise ValueError("Truncated Huff dispatch")
    marker = struct.unpack_from('<I', src)[0]
    if marker == 0x24000000:
        if len(src) < 20:
            raise ValueError("Truncated single-stream Huff envelope")
        src = src[16:]
    elif marker & 0xffff00ff == 0x24000000:
        # A chain of compressed entropy payloads, not independent segments.
        # Intermediate stages always decode bytes, including for Huff16.
        stages = (marker >> 8) & 255
        prefixes = []
        tail_counts = []
        size, tail = struct.unpack_from('<IQ', src, 4)
        at = 16
        for _ in range(stages):
            if size < 4 or at + size + 12 > len(src):
                raise ValueError("Truncated Huff chain prefix")
            prefixes.append(src[at:at + size])
            tail_counts.append(tail)
            at += size
            size, tail = struct.unpack_from('<IQ', src, at)
            at += 12
        if size + tail != len(src) - at:
            raise ValueError("Huff chain final length mismatch")
        decoded, _ = decode_symbols(src[at:], 8, tail_counts[-1])
        for i in range(stages - 1, -1, -1):
            decoded, _ = decode_symbols(
                prefixes[i] + decoded,
                width if i == 0 else 8,
                count if i == 0 else tail_counts[i - 1],
            )
        return decoded
    result, _stats = decode_symbols(src, width, count)
    return result


def decode_lane(src: bytes, kind: int, count: int) -> tuple[bytes, int]:
    """Return packed 8/16-bit lane values and the number of byte planes."""
    if not 0 < count <= 20_000_000:
        raise ValueError("Invalid byte-plane record count")
    if kind == 0:
        if len(src) != count:
            raise ValueError("Raw byte-plane length mismatch")
        return src, 1
    if kind not in range(1, 7):
        raise ValueError("Unknown byte-plane predictor")
    width = 16 if kind >= 4 else 8
    stride = width // 8
    if len(src) < stride:
        if src:
            raise ValueError("Truncated constant lane")
        values = [0]
        bitmap = b''
    elif len(src) == stride:
        values = [int.from_bytes(src, 'little')]
        bitmap = b''
    else:
        symbols, at = read_size(src)
        if not 1 <= symbols <= count:
            raise ValueError("Lane symbol count exceeds output count")
        bitmap = b''
        if symbols > 1:
            bitmap_bytes, at = read_size(src, at)
            end = at + bitmap_bytes
            if end > len(src):
                raise ValueError("Lane bitmap Huff block exceeds input")
            bitmap = decode_huff(src[at:end], (count + 6) // 8, 8)
            at = end
        value_bytes, at = read_size(src, at)
        end = at + value_bytes
        if end != len(src):
            raise ValueError("Lane values do not cover input")
        raw = decode_huff(src[at:end], symbols, width)
        values = list(raw) if width == 8 else list(struct.unpack('<' + 'H' * symbols, raw))
    mask = (1 << width) - 1
    value = values[0]
    out = bytearray(value.to_bytes(stride, 'little'))
    if len(values) == 1:
        fill = 0 if kind in (2, 5) else value
        out.extend(fill.to_bytes(stride, 'little') * (count - 1))
        return bytes(out), stride
    table = [0] * (1 << width) if kind in (2, 5) else None
    cursor = 1
    sign_state = 0
    for i in range(count - 1):
        bit = (bitmap[i // 8] >> (i % 8)) & 1
        if kind in (3, 6):
            if cursor >= len(values):
                raise ValueError("Not enough delta symbols")
            delta = values[cursor]
            cursor += 1
            if sign_state != bit:
                delta = -delta
            sign_state ^= bit
            value = (value + delta) & mask
        elif kind in (1, 4):
            if bit:
                if cursor >= len(values):
                    raise ValueError("Not enough transition symbols")
                value = values[cursor]
                cursor += 1
        else:
            if bit:
                if cursor >= len(values):
                    raise ValueError("Not enough predictor symbols")
                successor = values[cursor]
                cursor += 1
                table[value] = successor
            else:
                successor = table[value]
            value = successor
        out.extend(value.to_bytes(stride, 'little'))
    if cursor != len(values):
        raise ValueError("Unused lane symbols")
    return bytes(out), stride


def decode_j(src: bytes, count: int, lanes: int) -> bytes:
    layout = split_j(src, lanes)
    out = bytearray(count * lanes)
    pending = False
    for d in layout['descriptors']:
        lane = d['lane']
        kind = d['kind']
        size = d['compressedBytes']
        at = d['compressedOffset']
        if kind in (4, 5, 6):
            if lane % 2 == 0:
                if size:
                    raise ValueError("Paired lane has unexpected first payload")
                pending = True
                continue
            if not pending and kind != 5:
                raise ValueError("Missing paired first lane")
            pending = False
            decoded, width = decode_lane(src[at:at + size], kind, count)
            out[lane-1::lanes] = decoded[0::2]
            out[lane::lanes] = decoded[1::2]
        else:
            if pending:
                raise ValueError("Incomplete paired lane")
            if not size:
                if kind != 1:
                    raise ValueError("Unexpected empty active byte lane")
                continue
            decoded, width = decode_lane(src[at:at + size], kind, count)
            out[lane::lanes] = decoded
    if pending:
        raise ValueError("Unterminated paired lane")
    return bytes(out)


def decode_byet(src: bytes, count: int, lanes: int) -> bytes:
    """Decode a BYET byte block, including transformed origin blocks."""
    if count < 0 or lanes not in (1, 4, 8, 12, 32):
        raise ValueError("Invalid BYET shape")
    total = count * lanes
    if total > 128 * 1024 * 1024:
        raise ValueError("BYET output exceeds 128 MiB limit")
    if len(src) == total:
        return src
    if not src:
        raise ValueError("Empty BYET block")
    mode = src[0]
    data = src[1:]
    for flag in (8, 4):
        if not mode & flag:
            continue
        if mode == flag:
            n = total
            at = 0
        else:
            n, at = read_size(data)
        if not 0 < n <= max(total, 1_000_000):
            raise ValueError("BYET intermediate length exceeds limit")
        end = at + (n + 7) // 8
        if end > len(data):
            raise ValueError("Truncated BYET transition bitmap")
        bitmap = data[at:end]
        if n > 64:
            literal_count, end = read_size(data, end)
            if literal_count != sum(byte.bit_count() for byte in bitmap):
                raise ValueError("BYET transition literal count mismatch")
        payload = data[end:]
        if len(payload) != sum(byte.bit_count() for byte in bitmap):
            raise ValueError("BYET transition payload length mismatch")
        table = bytearray(256)
        previous = cursor = 0
        unpacked = bytearray()
        for i in range(n):
            if bitmap[i // 8] >> (i % 8) & 1:
                if cursor >= len(payload):
                    raise ValueError("Truncated BYET transition payload")
                value = payload[cursor]
                cursor += 1
                if flag == 4 and i:
                    table[previous] = value
            else:
                value = previous if flag == 8 else table[previous]
            unpacked.append(value)
            previous = value
        # Native popcount includes unused high bits of the final bitmap byte.
        # Their literal bytes are framed but do not produce output values.
        padding_literals = (bitmap[-1] >> (n % 8)).bit_count() if n % 8 else 0
        if cursor + padding_literals != len(payload):
            raise ValueError("Unused BYET transition bytes")
        data = bytes(unpacked)
        mode &= ~flag
    if mode & 2:
        at = 0
        if mode == 2:
            n = total
        else:
            n, at = read_size(data)
        value, at = read_size(data, at)
        if at != len(data) or not 0 < n <= max(total, 1_000_000):
            raise ValueError("Invalid BYET constant bytes")
        data = value.to_bytes(8, 'little')[:n].ljust(n, b'\0')
        mode &= ~2
    if mode == 0x80:
        if data[:2] != b'J\x00':
            raise ValueError("Unknown nested BYET compressor")
        return decode_j(data[2:], count, lanes)
    if mode:
        raise ValueError(f"Unsupported BYET flags {mode:#x}")
    if len(data) != total:
        raise ValueError("BYET output length mismatch")
    return data
