"""Clean-room partial decoder for Apple's 0x61 Huff816 stream family.

The table grammar and 32-bit word bit order were reconstructed from the saved
ARM64 disassembly and checked against 1,971 captured tables. This module is an
independent implementation; it does not load or call Apple's decoder.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass


class HuffError(ValueError):
    pass


class WordBits:
    """MSB-first bit view over little-endian 32-bit words."""
    def __init__(self, data: bytes, at: int = 0):
        self.data = data
        self.at = at

    def take(self, count: int) -> int:
        if count < 0 or self.at + count > len(self.data) * 8:
            raise HuffError("truncated Huff816 bitstream")
        result = 0
        for _ in range(count):
            word_base = (self.at // 32) * 4
            byte_index = word_base + (3 - (self.at % 32) // 8)
            bit_index = 7 - self.at % 8
            result = (result << 1) | ((self.data[byte_index] >> bit_index) & 1)
            self.at += 1
        return result


@dataclass(frozen=True)
class HuffTable:
    width: int
    count: int
    entries: tuple[tuple[int, int, int], ...]  # code length, code, symbol
    bit_offset: int


@dataclass(frozen=True)
class Huff8Result:
    wrapper_tag: int
    decoded_bytes: bytes
    inner_kind: str


def parse_table(stream: bytes, width: int = 8) -> HuffTable:
    if width not in (8, 16):
        raise HuffError("symbol width must be 8 or 16")
    if len(stream) < 8:
        raise HuffError("truncated Huff816 header")
    marker = struct.unpack_from("<I", stream)[0]
    if marker & 0x7F000000 != 0x61000000:
        raise HuffError(f"unsupported Huff816 marker {marker:#010x}")
    # The first 32-bit word is dispatch metadata. The second word is consumed
    # by the same word-oriented bit reader used for the rest of the table.
    bits = WordBits(stream[4:])
    count = bits.take(width) + 1
    if count > (1 << width):
        raise HuffError("invalid Huff816 symbol count")
    length_field_width = bits.take(3)
    symbol = 0
    entries: list[tuple[int, int, int]] = []
    for _ in range(count):
        if length_field_width == 0:
            code_length = 1 if count == 2 else 0
            code = bits.take(1) if count == 2 else 0
        else:
            code_length = bits.take(length_field_width) + 1
            code = bits.take(code_length)
        if bits.take(1):
            if bits.take(1):
                symbol = bits.take(width)
            else:
                symbol += bits.take(width // 2)
        if not 0 <= symbol < (1 << width):
            raise HuffError("decoded table symbol out of range")
        entries.append((code_length, code, symbol))
        symbol += 1
    if any(n < 1 or n > 32 or code >= (1 << n) for n, code, _ in entries):
        raise HuffError("invalid Huff816 codeword")
    if len({(n, code) for n, code, _ in entries}) != count:
        raise HuffError("duplicate Huff816 codeword")
    kraft = sum(1 / (1 << n) for n, _, _ in entries)
    if kraft > 1.000001:
        raise HuffError("oversubscribed Huff816 table")
    return HuffTable(width, count, tuple(entries), bits.at)


def decode(stream: bytes, output_symbols: int, width: int = 8) -> bytes:
    """Decode one Huff816 frame to exactly output_symbols symbols.

    Symbol codes are explicit in the encoded table (not canonicalized). The
    32-bit-word bit reader continues directly from the code table into payload.
    """
    if not 0 <= output_symbols <= 1 << 26:
        raise HuffError("unreasonable output symbol count")
    table = parse_table(stream, width)
    bits = WordBits(stream[4:], table.bit_offset)
    by_length: dict[int, dict[int, int]] = {}
    for n, code, symbol in table.entries:
        by_length.setdefault(n, {})[code] = symbol
    max_length = max(by_length)
    out = bytearray()
    for _ in range(output_symbols):
        code = 0
        for n in range(1, max_length + 1):
            code = (code << 1) | bits.take(1)
            symbol = by_length.get(n, {}).get(code)
            if symbol is not None:
                out.extend(symbol.to_bytes(width // 8, "little"))
                break
        else:
            raise HuffError("payload contains no matching Huff816 codeword")
    return bytes(out)


def decode_huff8_wrapper(stream: bytes) -> Huff8Result:
    """Decode the captured 0x24 Huff8 envelope and its inner Huff816 frame.

    Captured byte lanes carry a 16-byte 0x24 envelope. Its uint64 field at
    +8 is the requested Huff816 output size in bytes; the inner stream begins
    at +16. The literal 0xe1000002 dispatch is handled explicitly.
    """
    if len(stream) < 20:
        raise HuffError("truncated Huff8 0x24 envelope")
    marker, _record_count = struct.unpack_from("<II", stream)
    if marker & 0x7F000000 != 0x24000000 or marker & 0xFF != 0:
        raise HuffError(f"unsupported Huff8 wrapper {marker:#010x}")
    wrapper_tag = (marker >> 8) & 0xFF
    if wrapper_tag not in (0, 1):
        raise HuffError(f"unsupported Huff8 wrapper tag {wrapper_tag}")
    requested_bytes = struct.unpack_from("<Q", stream, 8)[0]
    inner = stream[16:]
    inner_marker = struct.unpack_from("<I", inner)[0]
    if inner_marker == 0xE1000002:
        decoded = inner[4:]
        if requested_bytes and len(decoded) != requested_bytes:
            raise HuffError(
                f"literal length mismatch: {len(decoded)} != {requested_bytes}"
            )
        return Huff8Result(wrapper_tag, decoded, "literal")
    if inner_marker & 0x7F000000 != 0x61000000 or inner_marker & 0x80000000:
        raise HuffError(f"unsupported inner Huff816 marker {inner_marker:#010x}")
    decoded = decode(inner, requested_bytes, width=8)
    if len(decoded) != requested_bytes:
        raise HuffError("Huff816 wrapper output size mismatch")
    return Huff8Result(wrapper_tag, decoded, "huffman")


def self_test() -> None:
    # Two-symbol table: 0 -> 0, 1 -> 1, then payload 0,1,1,0.
    # Bits are count-1(8), length-field-width(3), then (code, delta-flag)
    # for each table entry, followed immediately by payload bits.
    bit_text = "00000001" + "000" + "00" + "10" + "0110"
    bit_text += "0" * ((32 - len(bit_text) % 32) % 32)
    first_word = int(bit_text[:32], 2)
    raw = struct.pack("<I", 0x61000002) + struct.pack("<I", first_word)
    assert decode(raw, 4) == bytes((0, 1, 1, 0))
    assert parse_table(raw).count == 2
    wrapped = struct.pack("<IIQ", 0x24000000, 1, 4) + raw
    result = decode_huff8_wrapper(wrapped)
    assert (result.wrapper_tag, result.inner_kind, result.decoded_bytes) == (
        0, "huffman", bytes((0, 1, 1, 0))
    )
    literal = struct.pack("<IIQ", 0x24000000, 1, 3) + struct.pack(
        "<I", 0xE1000002
    ) + b"abc"
    assert decode_huff8_wrapper(literal).decoded_bytes == b"abc"
    # Reject malformed/truncated tables.
    for bad in (b"", b"\x02\x00\x00\x61", raw[:5]):
        try:
            parse_table(bad)
        except HuffError:
            continue
        raise AssertionError("malformed Huff816 input accepted")
    print("PASS Huff816 parser bounds and malformed-input checks")


if __name__ == "__main__":
    self_test()
