"""Use independently acquired fixtures; no private URLs or credentials in results."""
import json
import os
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'codec'),str(ROOT/'ios/Python')]
from r3d_mobile import decode_tile, height_index, unpack_response
from nativefree_mesh import decode_mesh
from nativefree_soup import decode_soup
from nativefree_splat_material import pack_material20


class MobileDecoderChecks(unittest.TestCase):
    def test_bounded_gzip(self):
        import gzip
        self.assertEqual(unpack_response(gzip.compress(b'abc')),b'abc')
        with self.assertRaises(ValueError): unpack_response(gzip.compress(bytes(16_000_001)))

    def test_invalid_tile_and_index(self):
        for function in (decode_tile,height_index):
            with self.assertRaises(ValueError): function(bytes(300))

    @unittest.skipUnless(os.environ.get('R3D_TEST_FIXTURES'),'Set R3D_TEST_FIXTURES to acquired raw fixtures')
    def test_original_arrays_survive_mobile_packing(self):
        fixtures = Path(os.environ['R3D_TEST_FIXTURES'])
        files = list(fixtures.glob('*.r3d'))
        self.assertTrue(files)
        for file in files:
            raw = file.read_bytes()
            mobile, mesh, soup = decode_tile(raw), decode_mesh(raw), decode_soup(raw)
            vertices = list(struct.iter_unpack('<8f',mobile['vertices']))
            indices = [i[0] for i in struct.iter_unpack('<I',mobile['indices'])]
            positions = list(struct.iter_unpack('<3f',mesh['positions_f32']))
            uv = list(struct.iter_unpack('<2f',mesh['uv_f32']))
            normals = list(struct.iter_unpack('<3f',mesh['normals_f32']))
            self.assertEqual(len(indices),len(mesh['faces']))
            for i,index in enumerate(indices):
                expected = (*positions[mesh['faces'][i]],*normals[mesh['normal_indices'][i]],*uv[mesh['uv_indices'][i]])
                self.assertEqual(vertices[index],expected)
            rgba = pack_material20(soup.attributes_f32)
            original_xyz = list(struct.iter_unpack('<3f',soup.xyz_f32))
            visible = [i for i in range(soup.count) if rgba[i*20+3]]
            splats = list(struct.iter_unpack('<10f',mobile['splats']))
            self.assertEqual(len(splats),len(visible)*3)
            for i,record in enumerate(visible):
                for corner in range(3): self.assertEqual(splats[3*i+corner][:3],original_xyz[3*record+corner])
            info = json.loads(mobile['json'])
            self.assertEqual(info['meshTriangles'],mesh['faceCount'])


if __name__ == '__main__': unittest.main()
