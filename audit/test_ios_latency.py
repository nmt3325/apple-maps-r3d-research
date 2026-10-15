"""Keep latency reports session-specific and distinguish discovery from codec work."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from audit.summarize_ios_latency import distribution, read_logs, summarize


def row(session, sequence, event, fields=None, tile=None, trace=None):
    result = dict(session_id=session,sequence=sequence,event=event,fields=fields or {},
                  unix_time=1700000000+sequence/1000)
    if tile:
        result['tile'] = tile
    if trace:
        result['trace_id'] = trace
    return result


class IOSLatencyChecks(unittest.TestCase):
    def test_sessions_lod_discovery_and_atlas_are_separate(self):
        tile = 's98_z16_x1_y2_h0'
        rows = [row('new',0,'session.start'),
                row('new',1,'app.model_init',{'coarse_zoom':16,'latency_origin':'horizontal_plan'}),
                row('new',2,'decoder.ready',{'compiled':True}),
                row('new',3,'decode.end',{'duration_ms':.2,'function':'atlas_payload'},tile),
                row('new',4,'decode.end',{'duration_ms':25,'function':'decode_tile'},tile),
                row('new',5,'pipeline.begin',{'queue_wait_ms':20},tile,'a'),
                row('new',6,'gpu.resident',{'needed_to_resident_ms':180},tile,'a'),
                row('old',7,'decode.end',{'duration_ms':600},'s98_z18_x1_y2_h0')]
        sessions = {s['session']:s for s in summarize(list(reversed(rows)))['sessions']}
        self.assertEqual(sessions['new']['coarseMetrics']['decode.end']['count'],1)
        self.assertEqual(sessions['new']['coarseMetrics']['decode.end']['medianMs'],25)
        self.assertEqual(sessions['new']['coarseMetrics']['gpu.resident']['atMost100Ms'],0)
        self.assertLess(sessions['new']['coarseAttemptToResident']['medianMs'],100)
        self.assertEqual(sessions['new']['latencyOrigin'],'horizontal_plan')
        self.assertEqual(sessions['old']['latencyOrigin'],'expanded_tile_plan')
        self.assertEqual(sessions['old']['coarseZoom'],18)
        self.assertIsNone(sessions['new']['coarseMetrics']['render.tile_first_presented'])

    def test_archive_reads_all_sessions_and_rotated_parts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'logs.zip'
            with zipfile.ZipFile(path,'w') as archive:
                for index,session in enumerate(('previous','latest','previous')):
                    archive.writestr(f'logs/stream-{index}.jsonl',json.dumps(row(session,index,'session.start'))+'\n')
                archive.writestr('__MACOSX/ignored.jsonl','invalid')
            sessions = summarize(read_logs(path))['sessions']
            self.assertEqual([s['records'] for s in sessions],[2,1])

    def test_attempt_duration_prefers_monotonic_measurements(self):
        tile = 's98_z18_x1_y2_h0'
        begin = row('a',0,'pipeline.begin',{'needed_wait_ms':80},tile,'trace')
        resident = row('a',1,'gpu.resident',{'needed_to_resident_ms':140},tile,'trace')
        resident['unix_time'] += 100
        result = summarize([begin,resident])['sessions'][0]
        self.assertEqual(result['coarseAttemptToResident']['medianMs'],60)

    def test_only_incomplete_last_live_line_is_tolerated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'stream-0.jsonl'
            valid = json.dumps(row('a',0,'session.start'))+'\n'
            path.write_text(valid+'{"partial":')
            self.assertEqual(len(read_logs(path)),1)
            path.write_text(valid+'{"partial":\n')
            with self.assertRaises(json.JSONDecodeError):
                read_logs(path)

    def test_distribution_ignores_nonfinite_and_boolean_values(self):
        self.assertEqual(distribution([None,True,float('nan'),float('inf')]),None)
        stats = distribution([200,100,20,50])
        self.assertEqual(stats,dict(count=4,medianMs=75,p95Ms=100,maxMs=200,atMost100Ms=3))

    def test_read_limit_applies_before_loading_whole_files(self):
        with tempfile.TemporaryDirectory() as directory, patch('audit.summarize_ios_latency.MAX_LOG_BYTES',16):
            path = Path(directory)/'stream-0.jsonl'
            path.write_bytes(b' '*17)
            for source in (path,Path(directory)):
                with self.assertRaisesRegex(ValueError,'read limit'):
                    read_logs(source)


if __name__ == '__main__':
    unittest.main()
