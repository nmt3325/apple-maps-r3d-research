"""Geographic edge cases and real-R3D rejection through the public entry point."""
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'pipeline'))
from acquisition import plan_area,tile_name

class PipelineTests(unittest.TestCase):
    def test_dateline_and_invalid_requests(self):
        plan=plan_area(0,180,10,max_tiles=4)
        self.assertEqual({t['x'] for t in plan['tiles']},{0,(1<<20)-1})
        for lat,lon,r in [(float('nan'),0,1),(86,0,1),(0,181,1),(0,0,0),(0,0,100001)]:
            with self.assertRaises(ValueError):plan_area(lat,lon,r)
        with self.assertRaises(ValueError):plan_area(0,0,1000,max_tiles=1)

    def test_original_r3d_corruption_and_wrong_location(self):
        root=Path(os.environ.get('R3D_OAHU_DIR','/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20'))
        files=sorted(root.glob('s98_z20_x*_y*_h0.r3d'))
        if not files:self.skipTest('Original Oahu R3D corpus is not installed')
        fixture=files[0];match=re.fullmatch(r's98_z20_x(\d+)_y(\d+)_h0.r3d',fixture.name)
        x,y=map(int,match.groups());raw=fixture.read_bytes()
        for case,payload,target_x in [('truncated',raw[:128],x),('wrong-location',raw,x+100)]:
            with self.subTest(case=case),tempfile.TemporaryDirectory() as temporary:
                path=Path(temporary);source=path/'input';source.mkdir()
                coord={'x':target_x,'y':y,'z':20,'h':0};(source/tile_name(coord)).write_bytes(payload)
                n=1<<20;lat=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y+.5)/n))));lon=(target_x+.5)/n*360-180
                output=path/'output'
                command=[sys.executable,str(REPO/'pipeline/r3d_explorer.py'),'--lat',str(lat),'--lon',str(lon),'--radius-m','.001',
                         '--source-dir',str(source),'--out-dir',str(output),'--workers','1']
                result=subprocess.run(command,capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                report=json.loads((output/'run.json').read_text());self.assertFalse(report['pass'])
                self.assertFalse((output/'viewer/scene.json').exists())
                self.assertEqual(report['nativeGoldenInput'],False)
                if case=='truncated':self.assertEqual(report['steps'][-1]['exitCode'],1)
                else:self.assertIn('georeference does not match',report['error']['message'])

if __name__=='__main__':unittest.main()
