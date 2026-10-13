"""Portable Huff8/16 envelope dispatcher (no BYET predictor)."""
from huff816_envelope import split_envelope, EnvelopeError
from nativefree_huff816 import decode_symbols

def decode_envelope(data: bytes, width: int, *, count: int | None = None,
                    offset: int = 0, max_bytes: int = 100_000_000):
    if width not in (8, 16):
        raise EnvelopeError("invalid Huff width")
    segments = split_envelope(data, offset)
    segmented = segments[0].symbol_count is not None
    if not segmented and count is None:
        raise EnvelopeError("single-stream requires caller-supplied symbol count")
    total = sum(s.symbol_count for s in segments) if segmented else count
    if count is not None and total != count:
        raise EnvelopeError("Huff output count mismatch")
    if total < 0 or total * (width // 8) > max_bytes:
        raise EnvelopeError("Huff output exceeds limit")
    parts = []
    for segment in segments:
        expected = segment.symbol_count if segmented else count
        payload = data[segment.offset:segment.offset + segment.compressed_size]
        block, _ = decode_symbols(payload, width, expected)
        parts.append(block)
    result = b"".join(parts)
    if len(result) != total * (width // 8):
        raise EnvelopeError("Huff output byte count mismatch")
    return result
