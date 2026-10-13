"""Independent parser for segmented 0x24 Huff816 wrappers.

Static reconstruction of Huff8/Huff16 wrapper metadata; numeric BYET decode
and caller-supplied output counts are separate unresolved stages.
"""
from dataclasses import dataclass
from struct import unpack_from

class EnvelopeError(ValueError):
    pass

@dataclass(frozen=True)
class Segment:
    offset: int
    compressed_size: int
    symbol_count: int | None

def split_envelope(data: bytes, offset: int = 0) -> tuple[Segment, ...]:
    if offset < 0 or len(data) - offset < 16:
        raise EnvelopeError("truncated envelope")
    marker, size0, count0 = unpack_from("<IIQ", data, offset)
    if marker & 0xffff00ff != 0x24000000:
        raise EnvelopeError("unexpected envelope marker")
    number = (marker >> 8) & 255
    if not number:
        if offset + 16 == len(data):
            raise EnvelopeError("empty single-stream envelope")
        return (Segment(offset + 16, len(data) - offset - 16, None),)
    segments = []
    pos = offset + 16
    for index in range(number):
        if index == 0:
            size, count = size0, count0
        else:
            if len(data) - pos < 12:
                raise EnvelopeError("truncated segment descriptor")
            size, count = unpack_from("<IQ", data, pos)
            pos += 12
        if size < 4 or size > len(data) - pos:
            raise EnvelopeError("segment exceeds envelope")
        segments.append(Segment(pos, size, count))
        pos += size
    if pos != len(data):
        raise EnvelopeError("unexpected trailing bytes")
    return tuple(segments)
