"""Focused regressions for predictor semantics, float sentinels and corruption."""
import struct
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'codec'))
from nativefree_bytes import decode_byet, decode_lane
from nativefree_byet_origin import read_origin_int32
from nativefree_mesh import reconstruct_quantized
from nativefree_mesh import decode_mesh
from nativefree_soup import decode_quantized, decode_soup
from nativefree_validate import validate_arrays
from nativefree_splat_material import pack_material20
from nativefree_trico_size import encode_size
from nativefree_huff_aligned import WordBits, decode_symbols, Huff816Error


def literal(payload):
    return struct.pack('<I', 0xe1000002) + payload


def lane(kind, values, bitmap, output_count):
    width = 2 if kind >= 4 else 1
    encoded = b''.join(v.to_bytes(width, 'little') for v in values)
    bitstream = literal(bytes((bitmap,)))
    value_stream = literal(encoded)
    return encode_size(len(values)) + encode_size(len(bitstream)) + bitstream + encode_size(len(value_stream)) + value_stream


def word_bits(bits):
    bits += '0' * (-len(bits) % 32)
    return b''.join(struct.pack('<I', int(bits[i:i+32], 2)) for i in range(0, len(bits), 32))


def compressed_huff(entries, values, width):
    table = f'{len(entries)-1:0{width}b}' + '101'
    for length, code, symbol in entries:
        table += f'{length-1:05b}{code:0{length}b}11{symbol:0{width}b}'
    codes = {symbol: f'{code:0{length}b}' for length, code, symbol in entries}
    return struct.pack('<I', 0x61000002) + word_bits(table) + word_bits(''.join(codes[v] for v in values))


class NumericCodecTests(unittest.TestCase):
    def test_word_reader_across_boundaries(self):
        text = ''.join(f'{v:032b}' for v in (0x12345678, 0xdeadbeef, 0x98765432))
        data = word_bits(text)
        for start in range(64):
            for width in range(33):
                reader = WordBits(data, start)
                self.assertEqual(reader.read(width), int(text[start:start+width] or '0', 2))
                self.assertEqual(reader.pos, start+width)
        with self.assertRaises(Huff816Error): WordBits(data[:-1], 64).read(1)

    def test_huff_prefix_lookup_long_codes_and_tail(self):
        for width in (8, 16):
            entries = [(1, 0, 3), (12, 1<<11, 10), (32, (1<<31)|(1<<30), (1<<width)-1)]
            for values in ([3], [10], [entries[-1][2]], [3, 10, entries[-1][2], 3]*37):
                data = compressed_huff(entries, values, width)
                decoded, stats = decode_symbols(data, width, len(values))
                expected = b''.join(v.to_bytes(width//8, 'little') for v in values)
                self.assertEqual(decoded, expected)
                self.assertEqual(stats['entropyBitsConsumed'], sum(next(n for n, _, s in entries if s==v) for v in values))
            data = compressed_huff(entries, [3], width)
            for bad in (data[:-1], data+b'\0'*4, data[:-4]+struct.pack('<I', 1),
                        data[:-4]+struct.pack('<I', 0xe0000000)):
                with self.assertRaises(Huff816Error): decode_symbols(bad, width, 1)
            conflict = compressed_huff([(1,0,1),(2,0,2)], [1], width)
            with self.assertRaises(Huff816Error): decode_symbols(conflict, width, 1)

    def test_huff_constant_and_literal(self):
        for width in (8, 16):
            constant = struct.pack('<I', 0x61000002) + word_bits('0'*width+'00011'+f'{7:0{width}b}')
            self.assertEqual(decode_symbols(constant, width, 5)[0], (7).to_bytes(width//8,'little')*5)
            self.assertEqual(decode_symbols(literal(b'\0'*(width//8)), width, 1)[0], b'\0'*(width//8))

    def test_byte_predictors(self):
        self.assertEqual(decode_lane(lane(1, [10, 20, 10], 0b1010, 5), 1, 5)[0], bytes([10, 10, 20, 20, 10]))
        self.assertEqual(decode_lane(lane(2, [10, 20, 10], 0b0011, 5), 2, 5)[0], bytes([10, 20, 10, 20, 10]))
        self.assertEqual(decode_lane(lane(3, [10, 2, 3, 4, 5], 0b0110, 5), 3, 5)[0], bytes([10, 12, 9, 13, 18]))

    def test_paired_predictors(self):
        for kind, values, bitmap, expected in [
            (4, [1000, 2000, 1000], 0b1010, [1000, 1000, 2000, 2000, 1000]),
            (5, [1000, 2000, 1000], 0b0011, [1000, 2000, 1000, 2000, 1000]),
            (6, [1000, 200, 300, 400, 500], 0b0110, [1000, 1200, 900, 1300, 1800])]:
            decoded, width = decode_lane(lane(kind, values, bitmap, 5), kind, 5)
            self.assertEqual(width, 2)
            self.assertEqual(list(struct.unpack('<5H', decoded)), expected)

    def test_origin_crosses_channel_boundary(self):
        self.assertEqual(read_origin_int32(bytes.fromhex('0877065cfeff5afefff5ff')), (-420, -422, -2561))
        packed = struct.pack('<3i', -420, -422, -2561)
        self.assertEqual(decode_byet(bytes.fromhex('0877065cfeff5afefff5ff'), 3, 4), packed)

    def test_long_transition_block(self):
        bitmap = b'\x01' + b'\0' * 8
        source = b'\x08' + bitmap + encode_size(1) + b'\x7f'
        self.assertEqual(decode_byet(source, 72, 1), b'\x7f' * 72)
        with self.assertRaises(ValueError):
            decode_byet(source[:-1], 72, 1)

    def test_special_floats_precede_origin(self):
        origins = struct.pack('<3i', 5, 9, 17)
        deltas = struct.pack('<3i', -1, -2, -3)
        source = b'\x25\0' + encode_size(len(origins)) + origins + deltas
        out, _ = decode_quantized(source, 1, 3, (0.1, 0.2, 0.3))
        self.assertEqual(struct.unpack('<3I', out), (0x7fc00000, 0xff800000, 0x7f800000))

    def test_closed_triangle_predictor(self):
        # Zigzag deltas seed q0=10, q1=12, q2=14; rounded mean is 11.
        residual = struct.pack('<3i', 20, 4, 6)
        self.assertEqual(struct.unpack('<3i', reconstruct_quantized([0, 1, 2], [-1]*3, residual, 1)), (10, 12, 14))

    def test_truncated_and_inconsistent_lanes(self):
        good = lane(1, [10, 20, 10], 0b1010, 5)
        for bad in (b'\xff\xff', good[:-1], good + b'\0'):
            with self.assertRaises(ValueError):
                decode_lane(bad, 1, 5)
        with self.assertRaises(ValueError):
            decode_byet(b'\x80J\0\x10', 3, 4)

    def test_original_numeric_fixture_and_corruption(self):
        root = Path(os.environ.get('R3D_REFERENCE_ROOT', '/opt/flyover-viewer'))
        name = 'r3d_z20_x931330_y412807_h0.r3d'
        source = root / 'native-r3d' / name
        if not source.is_file():
            self.skipTest('Release reference corpus is not installed; run the full array audits separately')
        raw = source.read_bytes()
        soup = decode_soup(raw)
        mesh = decode_mesh(raw)
        self.assertTrue(validate_arrays(soup, mesh)['finiteGeometry'])
        golden = root / 'decoded-native'
        self.assertEqual(soup.xyz_f32, (golden/'all-223'/(name+'.native-triangle-f32')).read_bytes())
        self.assertEqual(pack_material20(soup.attributes_f32), (golden/'all-223'/(name+'.native-material20')).read_bytes())
        for key, suffix in [('positions_f32', '2b0'), ('uv_f32', '2c8'), ('normals_f32', '2e0')]:
            self.assertEqual(mesh[key], (golden/'c3m-all-223'/(name+'.c3m-'+suffix+'.bin')).read_bytes())
        for bad in (raw[:-1], raw[:128], b'\0' + raw[1:]):
            with self.assertRaises(ValueError):
                decode_soup(bad)
        poisoned = dict(mesh)
        poisoned['faces'] = mesh['faces'].copy()
        poisoned['faces'][0] = mesh['vertices']
        with self.assertRaises(ValueError):
            validate_arrays(soup, poisoned)


if __name__ == '__main__':
    unittest.main()
