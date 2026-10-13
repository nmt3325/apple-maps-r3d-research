"""Pack original Splat attributes into native-compatible RGBA/material records."""
import math
import struct


def pack_material20(attributes_f32: bytes) -> bytes:
    if len(attributes_f32) % 32:
        raise ValueError("Splat attributes must have eight float32 channels")
    out = bytearray()
    for at in range(0, len(attributes_f32), 32):
        values = struct.unpack_from('<4f', attributes_f32, at)
        for index in (1, 2, 3, 0):
            value = values[index]
            scaled = struct.unpack('<f', struct.pack('<f', value * 255))[0]
            # Native float->integer truncation maps missing color to zero.
            integer = int(scaled) if math.isfinite(scaled) else 0
            out.append(integer & 255)
        out.extend(attributes_f32[at + 16:at + 32])
    return bytes(out)
