"""Integration checks for the stream cache, HTTP API, and original tile packing."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'pipeline'))
from web_streaming import StreamCache,coordinates,expand_heights,prepare_request,fetch_response

CONFIG={'endpoint':'https://example.invalid/tile','queryParameters':[['style','98'],['x','0'],['y','0'],['z','20'],['h','0']],
        'signingParts':['public-dummy-part-a','public-dummy-part-b']}
TILE={'style':98,'z':20,'x':931325,'y':412987,'h':0}


def fake_worker(config,tile,destination):
    path=Path(destination);path.mkdir(parents=True,exist_ok=True);(path/'public').mkdir(exist_ok=True)
    (path/'public/mesh.bin').write_bytes(b'mesh')
    result={'sourceSHA256':'f'*64,'textureSize':None,'tile':tile}
    record={'status':'ready','result':result,'finished':time.time()}
    (path/'result.json').write_text(json.dumps(record));return record


class StreamTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name);self.config=self.root/'config.json';self.config.write_text(json.dumps(CONFIG))

    def cache(self,**kwargs):
        cache=StreamCache(self.config,self.root/'cache',worker=fake_worker,executor=ThreadPoolExecutor(max_workers=2),**kwargs)
        self.addCleanup(cache.close);return cache

    def wait(self,cache,job_id):
        limit=time.monotonic()+5
        while time.monotonic()<limit:
            state=cache.state(job_id)
            if state['status']!='queued':return state
            time.sleep(.005)
        self.fail('Worker did not finish')

    def test_coordinates_and_multilod_all_heights(self):
        for value in [{**TILE,'x':True},{**TILE,'h':-.1},{**TILE,'z':17},{**TILE,'x':2**20},{**TILE,'y':-1},{**TILE,'style':99},{}]:
            with self.assertRaises(ValueError):coordinates(value)
        for z in (18,19,20):
            factor=1<<(z-17);tile={'style':98,'z':z,'x':7*(1<<(z-13))+2*factor,'y':8*(1<<(z-13))+2*factor,'h':0}
            index={'tile':{'z':13,'x':7,'y':8},'cells':[[2,13,0],[2,13,3]]}
            result=expand_heights(index,tile)
            self.assertEqual([t['h'] for t in result],list(range(factor))+list(range(3*factor,4*factor)))
            with self.assertRaises(ValueError):expand_heights({**index,'tile':{'z':13,'x':8,'y':8}},tile)

    def test_singleflight_queue_limit_and_restart_cache(self):
        started=threading.Event();release=threading.Event();calls=[]
        def blocked(config,tile,destination):
            calls.append(tile);started.set();release.wait(5);return fake_worker(config,tile,destination)
        cache=self.cache(max_pending=2);cache.worker=blocked
        first=cache.request(TILE);self.assertTrue(started.wait(2));second=cache.request(TILE)
        self.assertEqual(first['id'],second['id']);self.assertEqual(len(cache.futures),1)
        cache.request({**TILE,'h':1})
        with self.assertRaises(BlockingIOError):cache.request({**TILE,'h':2})
        release.set();self.assertEqual(self.wait(cache,first['id'])['status'],'ready');cache.close()
        self.assertEqual(sum(t['h']==0 for t in calls),1)
        restarted=self.cache();state=restarted.request(TILE)
        self.assertTrue(state['cached']);self.assertEqual(state['id'],first['id']);self.assertEqual(len(restarted.futures),0)
        self.assertNotIn('accessKey',json.dumps(state));self.assertNotIn('signingParts',json.dumps(state))
        self.assertIsNone(restarted.asset(restarted.namespace,state['id'],'raw.r3d'))
        self.assertIsNone(restarted.asset('wrong',state['id'],'mesh.bin'))
        with restarted.asset(restarted.namespace,state['id'],'mesh.bin') as source:self.assertEqual(source.read(),b'mesh')

    def test_empty_and_authentication_are_distinct(self):
        with patch('web_streaming.response_body',return_value=b''):
            self.assertEqual(fetch_response(CONFIG,TILE),b'')
            with self.assertRaises(ValueError):fetch_response(CONFIG,{'style':100,'z':13,'x':7275,'y':3226,'h':0})
        with patch('web_streaming.response_body',side_effect=HTTPError('redacted',403,'Forbidden',{},None)):
            with self.assertRaises(PermissionError):fetch_response(CONFIG,TILE)
        cache=self.cache()
        def denied(*args):raise PermissionError('redacted')
        cache.worker=denied;state=self.wait(cache,cache.request(TILE)['id'])
        self.assertTrue(state['authenticationFailed']);self.assertEqual(state['status'],'failed')
        with self.assertRaises(PermissionError):cache.request({**TILE,'h':1})

    def test_disk_budget_evicts_old_entries(self):
        cache=self.cache(budget=900)
        first=None
        for h in range(8):
            state=self.wait(cache,cache.request({**TILE,'h':h})['id'])
            if first is None:first=state['id']
        self.assertLessEqual(sum(cache.sizes.values()),900);self.assertNotIn(first,cache.sizes)

    def test_http_origin_assets_and_existing_scene(self):
        import map_web_server as server
        root=self.root/'web';root.mkdir();(root/'index.html').write_text('test');(root/'scene.json').write_text(json.dumps({'origin':[0,0,0]}))
        cache=self.cache()
        with patch.multiple(server,CONFIG=self.config,WEB_ROOT=root,STREAM=cache):
            http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{http.server_port}'
            try:
                with patch.object(server,'PUBLIC_ORIGIN',base):
                    with self.assertRaises(HTTPError) as failure:
                        urlopen(Request(base+'/api/stream/request',data=json.dumps(TILE).encode(),headers={'Origin':'https://other.invalid'}))
                    self.assertEqual(failure.exception.code,403)
                    request=Request(base+'/api/stream/request',data=json.dumps(TILE).encode(),headers={'Origin':base,'Content-Type':'application/json'})
                    state=json.loads(urlopen(request).read());state=self.wait(cache,state['id'])
                    self.assertEqual(json.loads(urlopen(base+'/api/stream/jobs/'+state['id']).read())['status'],'ready')
                    self.assertEqual(urlopen(base+state['result']['mesh']).read(),b'mesh')
                    with self.assertRaises(HTTPError):urlopen(base+state['result']['mesh'].split('mesh.bin')[0]+'raw.r3d')
                    self.assertTrue(json.loads(urlopen(base+'/scene.json').read())['webStreaming'])
                    self.assertIn(b'stream-enabled',urlopen(base+'/').read())
            finally:http.shutdown();http.server_close();thread.join()

    def test_original_upper_tile_packing_and_wrong_location_rejection(self):
        fixtures=list((REPO/'reports/generated/height-repairs').glob('*/raw/s98_z20_x931325_y412987_h1.r3d'))
        if not fixtures:self.skipTest('Original Tokyo upper tile is not installed')
        raw=fixtures[0].read_bytes();tile={**TILE,'h':1}
        with patch('web_streaming.fetch_response',return_value=raw):
            destination=self.root/'original';record=prepare_request(self.config,tile,destination)
            self.assertEqual(record['status'],'ready');result=record['result']
            self.assertEqual(result['sourceSHA256'],hashlib.sha256(raw).hexdigest());self.assertLessEqual(result['georeferenceErrorMeters'],.5)
            self.assertGreater(result['triangles'],0);self.assertGreater(result['visibleSplatRecords'],0)
            # Reconstruct original triangles from the display buffer's split vertices.
            from nativefree_mesh import decode_mesh
            import numpy as np
            mesh=decode_mesh(raw);data=(destination/'public/mesh.bin').read_bytes();_,_,count,faces=struct.unpack_from('<4I',data)
            xyz=np.frombuffer(data,dtype='<f4',offset=16,count=count*3).reshape(-1,3)
            indices=np.frombuffer(data,dtype='<u4',offset=16+count*32,count=faces*3)
            expected=np.frombuffer(mesh['positions_f32'],dtype='<f4').reshape(-1,3)[mesh['faces']]
            self.assertTrue(np.array_equal(xyz[indices],expected));self.assertFalse((destination/'decoded').exists())
            with self.assertRaisesRegex(ValueError,'coordinates do not match'):
                prepare_request(self.config,{**tile,'x':tile['x']+100},self.root/'wrong-location')
            self.assertFalse((self.root/'wrong-location').exists())


if __name__=='__main__':unittest.main()
