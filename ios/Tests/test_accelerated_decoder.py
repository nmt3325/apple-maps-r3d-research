"""Compare compiled loops with the independent Python decoder, including malformed inputs."""
import contextlib
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import random
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'codec'),str(ROOT/'ios/Python'),str(ROOT)]
import nativefree_accel
import nativefree_bytes
import nativefree_huff_aligned
import nativefree_mesh
import nativefree_mesh_topology
import nativefree_soup
import nativefree_splat_material
import nativefree_validate
import r3d_mobile
from audit.test_numeric_codec import compressed_huff, literal, word_bits

ACCEL = nativefree_accel.accelerator
MODULES = [nativefree_bytes,nativefree_huff_aligned,nativefree_mesh,nativefree_mesh_topology,
           nativefree_soup,nativefree_splat_material,nativefree_validate,r3d_mobile]


@contextlib.contextmanager
def implementation(enabled):
    previous = [m.accelerator for m in MODULES]
    for m in MODULES:
        m.accelerator = ACCEL if enabled else None
    try:
        yield
    finally:
        for m,value in zip(MODULES,previous):
            m.accelerator = value


@unittest.skipIf(ACCEL is None,'Build with ios/Scripts/build_decoder_accel.py and add the output to PYTHONPATH')
class AcceleratedDecoderChecks(unittest.TestCase):
    def compare(self, function, *args):
        with implementation(False):
            expected = function(*args)
        with implementation(True):
            self.assertEqual(function(*args),expected)

    def test_huff_symbols_and_statistics(self):
        rng = random.Random(17015)
        for width in (8,16):
            entries = [(1,0,3),(12,1<<11,10),(32,(1<<31)|(1<<30),(1<<width)-1)]
            for count in (0,1,31,32,33,511):
                values = [rng.choice(entries)[2] for _ in range(count)]
                self.compare(nativefree_huff_aligned.decode_symbols,compressed_huff(entries,values,width),width,count)
            self.compare(nativefree_huff_aligned.decode_symbols,literal(bytes(width//8*17)),width,17)
            constant = struct.pack('<I',0x61000002)+word_bits('0'*width+'00011'+f'{7:0{width}b}')
            self.compare(nativefree_huff_aligned.decode_symbols,constant,width,53)

    def test_topology_adjacency_with_duplicate_edges(self):
        rng = random.Random(18020)
        for _ in range(100):
            faces = [rng.randrange(12) for _ in range(300)]
            self.compare(nativefree_mesh.build_adjacency,faces)
        for channels in (1,2,3):
            residuals = struct.pack('<'+'i'*channels*3,*([20,4,6]*channels))
            self.compare(nativefree_mesh.reconstruct_quantized,[0,1,2],[-1]*3,residuals,channels)

    def test_quantization_rounding_and_material(self):
        rng = random.Random(1815)
        values = [rng.randrange(-100000,100000) for _ in range(900)]
        origins = struct.pack('<3i',33,-44,55)
        payload = struct.pack('<'+'i'*len(values),*values)
        from nativefree_trico_size import encode_size
        self.compare(nativefree_soup.decode_quantized,b'\x25\0'+encode_size(len(origins))+origins+payload,300,3,(.1,.2,.3))
        attributes = b''.join(struct.pack('<8f',rng.random(),rng.random(),rng.random(),rng.random(),0,1,2,3) for _ in range(1000))
        self.compare(nativefree_splat_material.pack_material20,attributes)

    def test_compiled_shape_and_bounds_rejection(self):
        cases = [lambda:ACCEL.expand_lane(b'\1\2',b'',1,5),
                 lambda:ACCEL.quantize(b'\0'*12,(2**31,0,0),(1,1,1),3),
                 lambda:ACCEL.predict_mesh([3,1,2],[-1]*3,b'\0'*12,1),
                 lambda:ACCEL.uv_indices([0,1,2],[99,-1,-1],b'\0',[0]),
                 lambda:ACCEL.normals([0,0,0],b'\0'*4,b'\2\2',1,1,.1),
                 lambda:ACCEL.topology(1,b'\0',[0,1,3,1])]
        for case in cases:
            with self.assertRaises((ValueError,OverflowError)):
                case()

    def test_parallel_loops_and_exception_gil_restoration(self):
        values = struct.pack('<3i',20,40,60)*4096
        expected = ACCEL.quantize(values,(1,2,3),(.1,.2,.3),3)

        def work(_):
            for _ in range(12):
                self.assertEqual(ACCEL.quantize(values,(1,2,3),(.1,.2,.3),3),expected)
                # Both failures occur inside loops that have released the GIL.
                with self.assertRaises(ValueError):
                    ACCEL.quantize(values,(2**31-1,0,0),(1,1,1),3)
                with self.assertRaises(ValueError):
                    ACCEL.entropy(b'',[(0,1,7)],8,4096)
            return True

        with ThreadPoolExecutor(max_workers=4) as executor:
            self.assertTrue(all(executor.map(work,range(16))))

    @unittest.skipUnless(os.environ.get('R3D_TEST_FIXTURES'),'Set R3D_TEST_FIXTURES to original raw tiles')
    def test_parallel_original_tiles(self):
        files = sorted(Path(os.environ['R3D_TEST_FIXTURES']).glob('*.r3d'))[:5]
        self.assertTrue(files)
        originals = [path.read_bytes() for path in files]
        with implementation(True):
            expected = [r3d_mobile.decode_tile(raw) for raw in originals]
            with ThreadPoolExecutor(max_workers=2) as executor:
                actual = list(executor.map(r3d_mobile.decode_tile,originals*2))
        self.assertEqual(actual,expected*2)

    @unittest.skipUnless(os.environ.get('R3D_TEST_FIXTURES'),'Set R3D_TEST_FIXTURES to original raw tiles')
    def test_original_tiles_match_python_byte_for_byte(self):
        files = sorted(Path(os.environ['R3D_TEST_FIXTURES']).glob('*.r3d'))
        self.assertTrue(files)
        for path in files:
            with self.subTest(tile=path.name):
                raw = path.read_bytes()
                self.compare(r3d_mobile.decode_tile,raw)
                if path == files[0]:
                    with implementation(False):
                        soup,mesh = nativefree_soup.decode_soup(raw),nativefree_mesh.decode_mesh(raw)
                        expected = nativefree_validate.validate_arrays(soup,mesh)
                    with implementation(True):
                        self.assertEqual(nativefree_validate.validate_arrays(soup,mesh),expected)


if __name__ == '__main__':
    unittest.main()
