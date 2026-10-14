"""Regression for missing upper R3D layers, using real Oahu index and h1 originals."""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'pipeline'))
from acquisition import discover_height_tiles,fetch_area,plan_area


class HeightLayerTests(unittest.TestCase):
    def setUp(self):
        root=Path(os.environ.get('R3D_HEIGHT_FIXTURES',REPO/'reports/generated/vertical-investigation'))
        self.root=root
        indexes=list(root.rglob('s100_z13_x504_y3600_h0.c3mm'))
        uppers=list(root.rglob('s98_z20_x64556_y460816_h1.r3d'))
        if not indexes or not uppers:self.skipTest('Install original Oahu height-index/h1 fixtures')
        self.index=indexes[0].read_bytes();self.upper=uppers[0].read_bytes()
        x,y=64556,460816;n=1<<20
        self.lat=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y+.5)/n))))
        self.lon=(x+.5)/n*360-180
        self.plan=plan_area(self.lat,self.lon,.001)

    def test_real_index_discovers_upper_layers_and_enforces_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch('acquisition.response_body',return_value=self.index):
                plan=discover_height_tiles(self.plan,{},Path(temporary))
                self.assertIn({'z':20,'x':64556,'y':460816,'h':1},plan['tiles'])
                self.assertEqual(len(plan['tiles']),8)
                with self.assertRaises(ValueError):
                    discover_height_tiles(self.plan,{},Path(temporary),max_candidates=7)
        with tempfile.TemporaryDirectory() as temporary:
            with patch('acquisition.response_body',return_value=self.index[:64]):
                with self.assertRaises(RuntimeError):discover_height_tiles(self.plan,{},Path(temporary))

    def test_empty_lower_layer_does_not_hide_upper_geometry(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            with patch('acquisition.response_body',return_value=self.index):
                plan=discover_height_tiles(self.plan,{},output/'index')
            with patch('acquisition.response_body',side_effect=lambda config,tile:self.upper if tile['h']==1 else b''):
                result=fetch_area(plan,{},output/'raw',delay=0)
            self.assertEqual([f['tile']['h'] for f in result['files']],[1])
            self.assertEqual(len(result['emptyTiles']),7)
            self.assertEqual(result['errors'],[])
            # Repeat uses recorded empty responses only for the same original index.
            with patch('acquisition.response_body',side_effect=AssertionError('unexpected network request')):
                cached=fetch_area(plan,{},output/'raw',delay=0)
            self.assertEqual(cached['cached'],1);self.assertEqual(cached['cachedEmpty'],7)

    def test_offline_entry_preserves_original_upper_mesh_and_splats(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir()
            (source/'s98_z20_x64556_y460816_h1.r3d').write_bytes(self.upper)
            result=subprocess.run([sys.executable,str(REPO/'pipeline/r3d_explorer.py'),
                '--lat',str(self.lat),'--lon',str(self.lon),'--radius-m','.001',
                '--source-dir',str(source),'--out-dir',str(root/'output'),'--workers','1'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            run=json.loads((root/'output/run.json').read_text())
            scene=json.loads((root/'output/viewer/scene.json').read_text())
            self.assertTrue(run['pass']);self.assertFalse(run['nativeGoldenInput'])
            self.assertGreater(scene['bounds']['max'][1],110)
            self.assertGreater(scene['totals']['meshTriangles'],0)
            self.assertGreater(scene['totals']['visibleSplatRecords'],0)
            self.assertIn('_h1.r3d',scene['tiles'][0]['source'])

    def test_original_splat_only_upper_tile_and_corrupted_empty_mesh(self):
        from nativefree_mesh import decode_mesh
        from nativefree_r3d_codec_streams import dissect
        fixtures=list(self.root.rglob('s98_z20_x64555_y460821_h3.r3d'))
        if not fixtures:self.skipTest('Install original Oahu splat-only h3 fixture')
        raw=fixtures[0].read_bytes();mesh=decode_mesh(raw)
        self.assertEqual(mesh['faceCount'],0);self.assertEqual(mesh['positions_f32'],b'')
        corrupt=bytearray(raw);offset=dissect(raw)['meshStream']['offset'];corrupt[offset+32]=1
        with self.assertRaises(ValueError):decode_mesh(bytes(corrupt))
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir();(source/fixtures[0].name).write_bytes(raw)
            n=1<<20;x,y=64555,460821
            lat=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y+.5)/n))));lon=(x+.5)/n*360-180
            result=subprocess.run([sys.executable,str(REPO/'pipeline/r3d_explorer.py'),
                '--lat',str(lat),'--lon',str(lon),'--radius-m','.001','--source-dir',str(source),
                '--out-dir',str(root/'output'),'--workers','1','--export'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            scene=json.loads((root/'output/viewer/scene.json').read_text())
            self.assertEqual(scene['totals']['meshTriangles'],0)
            self.assertEqual(scene['totals']['splatRecords'],536)
            self.assertIsNone(scene['tiles'][0]['texture'])
            self.assertTrue((root/'output/export/scene.glb').is_file())


if __name__=='__main__':unittest.main()
