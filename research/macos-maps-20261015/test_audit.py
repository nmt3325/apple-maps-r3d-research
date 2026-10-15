#!/usr/bin/env python3
"""Regression checks for false-positive interpretations in the runtime audit."""
import json
import plistlib
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parent/'tools'))
from audit_probe import audit


class RuntimeAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        constants = bytearray(256)
        for i in range(4):
            struct.pack_into('<f',constants,(i*4+i)*4,1)
        struct.pack_into('<iff',constants,192,0,1.5,148.16207885742188)
        struct.pack_into('<3f',constants,240,1,1,1)
        (self.root/'constants.bin').write_bytes(constants)
        (self.root/'positions.bin').write_bytes(struct.pack('<24H',*([0,0,0,0]*3+[65535,65535,65535,0]*3)))
        (self.root/'properties.bin').write_bytes(bytes(24))
        (self.root/'orders.bin').write_bytes(struct.pack('<2i',1,0))
        self.rows = [dict(event='start',device='synthetic unit-test fixture'),
            dict(event='candidate_splat_constants',pipeline='Flyover::splat_vertex | Flyover::splat_fragment',
                uniform_file='constants.bin',splat_id=0,alpha_concentration=1.5,alpha_pre_factor=148.16207885742188),
            *[dict(event='splat_resource',splat_id=0,kind=kind,file=name,saved_bytes=size,complete=True) for kind,name,size in [
                ('positions-ushort4','positions.bin',48),('properties-12','properties.bin',24),('orders-int32','orders.bin',8)]],
            dict(event='summary',draw_calls=1)]

    def run_audit(self):
        (self.root/'events.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in self.rows))
        return audit(self.root)

    def test_valid_permutation_and_uniforms(self):
        result = self.run_audit()
        self.assertEqual(result['resources'][0]['records'],2)
        self.assertEqual(result['resources'][0]['first_ordered_triangle_index'],1)
        self.assertEqual(result['uniforms'][0]['fragment_half_pre_factor'],148.125)

    def test_mesh_binding_cannot_be_read_as_splat_constants(self):
        self.rows[1]['pipeline']='Flyover::flyover_bindless_vertex | Flyover::flyover_bindless_fragment'
        with self.assertRaisesRegex(ValueError,'another pipeline'):
            self.run_audit()

    def test_duplicate_order_is_rejected(self):
        (self.root/'orders.bin').write_bytes(struct.pack('<2i',0,0))
        with self.assertRaisesRegex(ValueError,'permutation'):
            self.run_audit()

    def test_different_record_counts_are_rejected(self):
        (self.root/'properties.bin').write_bytes(bytes(12))
        self.rows[3]['saved_bytes']=12
        with self.assertRaisesRegex(ValueError,'counts disagree'):
            self.run_audit()

    def test_logged_uniform_must_match_captured_bytes(self):
        self.rows[1]['alpha_pre_factor']=20
        with self.assertRaisesRegex(ValueError,'differ from snapshot'):
            self.run_audit()

    def test_empty_trace_is_not_successful_capture(self):
        trace=self.root/'mapkit.gputrace'
        trace.mkdir()
        (trace/'metadata').write_bytes(plistlib.dumps({'DYCaptureEngine.captured_frames_count':1}))
        (trace/'capture').write_bytes(bytes(8))
        self.rows.extend([dict(event='capture_start',success=True,draw_calls_at_start=1),
                          dict(event='capture_stop',draw_calls_at_stop=1)])
        self.assertFalse(self.run_audit()['capture']['has_command_data'])


if __name__ == '__main__':
    unittest.main()
