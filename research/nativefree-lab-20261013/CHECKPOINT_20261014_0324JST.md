# Apple Maps R3D v2 Linux native-free checkpoint — 2026-10-14 03:24 JST

## Safety / scope
Read `/opt/flyover-viewer/NATIVEFREE_HUFF_DECOMPILER_STATUS.md` and `/opt/flyover-viewer/www/NATIVEFREE_R3D_PROGRESS_20261013.md` plus 23:34, 00:51, 02:40 and callsite checkpoints. Changes only in `/opt/flyover-viewer/nativefree-lab-20261013/`. Production Tokyo viewer, fetcher, source Tokyo223/Oahu72 captures and native goldens were not modified. No Apple decoder executed.

## New code and static findings
- Added `huff_x3_provenance.py`, a standalone, read-only Python audit of the existing 20,832-byte Base64 ARM64 instruction slice, and `test_huff_x3_provenance.py` (2 tests).
- Independently validated the 12 known `_bytes_decompress` Huff8/Huff16 callsites, decoding BL immediates and tracing the nearest MOV to argument register x3. Output-count argument sources: **x20 at 4 sites, x19 at 2, x28 at 4, x24 at 2**; 9 Huff8 and 3 Huff16.
- At x20/x19 sites, `ldr x20/x19,[sp,#0x30]` is visible immediately before the Huff call. At x28 sites, representative constructors include `orr x28,x9,x13` (0x1b70a0784) and `orr x28,x13,x9,lsl #8` (0x1b70a0ab0, 0x1b70a0d20, 0x1b70a119c). At x24 sites, representative constructors include `orr x24,x23,x28,lsl #8` (0x1b70a1428, 0x1b70a152c) and `orr x24,x28,x23,lsl #8` (0x1b70a16ac). These are **instruction-local bit-packing observations**, not yet a complete path-sensitive reconstruction of the count fields.
- The audit deliberately labels nearest register definitions as candidates because branches and register lifetimes require CFG-aware tracing. It does not claim recovered per-kind 0–6 output counts.

## Tests
- `python3 -m unittest test_huff816_envelope test_huff816_wrapper_decode`: **4 tests PASS**, exit 0 (synthetic wrappers and literal Huff).
- `python3 -m unittest test_huff_x3_provenance`: **2 tests PASS**, exit 0, after correcting Base64 whitespace handling and locating MOV x3 within the last five instructions (some calls have a separate MOV x28,x0 between MOV x3 and BL).
- Separate static scan of saved capture also reproduced all 12 x3 source registers; no ARM64 code was executed.
- Attempted `test_huff816_envelope_corpus.py` on Tokyo/Oahu but remote command safety gate blocked execution. **No real-corpus envelope coverage or new golden numeric parity claimed in this run.**

## Open issues / next work
1. Recover x9/x13/x23/x28 construction, stack-slot provenance and branch conditions in `_bytes_decompress` to compute exact x3 per lane kind 0–6, using a CFG-aware disassembly/decompilation. Do not substitute lane compact prefix or point count without proof.
2. Run real-corpus envelope and entropy-consumption tests when permitted; use actual output count to reconstruct Huff8/Huff16 bytes and inverse BYET predictors, then compare Tokyo223 Splat XYZ, color, scale and rotation **numerically** to native goldens.
3. Implement TRICO v3 mesh vertices, faces, normals, UV/atlas mappings; validate Oahu72 and arbitrary-coordinate Linux-only fetch → textured polygons + Splat viewer in isolated staging.

**Not complete.** Full Linux-only R3D geometry decoding, golden numeric parity and full viewer integration have not passed. Leave recurring task active and suppress completion notification.
