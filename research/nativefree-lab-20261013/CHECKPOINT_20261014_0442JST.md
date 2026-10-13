# Apple R3D v2 Linux native-free checkpoint — 2026-10-14 04:42 JST

## Scope
Reviewed the requested status files and latest 03:24 checkpoint. All work stayed in the isolated lab. Production viewer, fetcher, source captures and native goldens were untouched.

## Reproducible results
- `python3 test_huff816_envelope_corpus.py`: exit 0. Scanned Tokyo 223 and Oahu 72 R3D files. **2,424 single-stream 0x24 envelopes, 0 segmented, 0 errors**. This does not imply full lane decoding.
- `python3 test_huff816_tables.py --limit 295`: exit 0. **1,462 compressed prefix tables, 962 literal streams, 0 errors**. Their sum matches all 2,424 envelopes independently.
- `python3 -m unittest test_huff_x3_provenance`: exit 0, **2 tests passed**.

- Added isolated `test_huff816_corpus_regression.py`: `python3 -m unittest test_huff816_corpus_regression` **1 test PASS**, exit 0; enforces corpus tile counts and wrapper invariants on future runs.

## Unresolved
The single-stream envelope does not carry a proven output symbol count; this must come from the BYET caller. The per-kind 0–6 reconstruction, entropy bit consumption, exact Splat XYZ/color/shape parity, mesh vertex/face/UV parity, and arbitrary-coordinate Linux-only textured polygon + Splat viewer are not implemented or validated.

## Next
Trace the twelve Huff callsite output-count registers through ARM64 control flow and stack slots. Use the recovered counts to decode byte lanes and test against Tokyo native golden arrays. Then address mesh topology/UV and Oahu geometry. No full-completion claim; leave recurring task active.
