# Native-free R3D analysis checkpoint — 2026-10-14 00:51 JST

## Scope
Reviewed the two required status documents and the previous 2026-10-13 23:34 JST Huff816 checkpoint. Original viewer, original captured Tokyo223/Oahu72 R3D, native goldens and independent fetcher were not changed.

## Newly established from existing offline Ghidra pseudocode (static inspection)
- The Huff8 wrapper at 0x1b709c7b4 and Huff16 wrapper at 0x1b709cbf4 both distinguish direct 0x61... streams from a 0x24... outer envelope.
- For a 0x24 envelope, the byte at offset +1 (bits 8..15 of the first little-endian u32) selects a segmented path when nonzero. In that path, the first segment's metadata consists of a u32 compressed-byte length at +4 and a u64 output-symbol count at +8. The compressed segment begins at +16; subsequent segments use 12-byte (u32 compressed length, u64 output count) descriptors. These offsets and loop structure are visible in both pseudocode files. This is an offline code interpretation, not yet tested on actual segmented R3D streams.
- For the common 0x24000000 marker (byte +1 zero), the wrapper skips 16 bytes and forwards the output-symbol count supplied by its caller to Huff816. Therefore the u64 at envelope +8 must NOT be assumed to be the single-stream output count. The earlier uncertainty about Huff symbol counts is specifically a missing caller argument in _bytes_decompress, not a value that can be safely read from the 0x24 single-stream header.
- The existing nativefree_huff816.py unwrap_24() only accepts the 0x24000000 single-stream case, consistent with the 1,462 compressed streams previously tested. It does not implement the segmented wrapper branch. This does not invalidate the 1,462 prefix-free-table / 962 literal tests.

## Validation and limits
- This run: **static source-level inspection only**. No new numerical output or native-golden parity claim; no CT104 test suite was successfully executed in this run. Remote command execution and a proposed isolated helper-script write were rejected by tool safety checks; read-only access and this checkpoint write remained available. Do not treat this as an algorithmic decoder milestone.
- Previously verified: 295 original tile structures; 590 BYET/J streams and 12,980 lane directories; 1,462 Huff816 prefix trees; 962 literal payloads. These are from the earlier checkpoint, NOT new test results.
- Missing: _bytes_decompress caller's exact per-kind output counts; Huff816 bit consumption; kinds 0..6 reconstruction; actual TRICO Splat XYZ/color/shape; mesh XYZ/indices/UV; numerical Tokyo223 golden parity; Linux-only arbitrary-coordinate fetch to full viewer.

## Next reproducible action
1. In the isolated lab only, extract/decompile _bytes_decompress (0x1b709f3d0 onward) and trace the arguments passed to _huff8_decompress and _huff16_decompress. Distinguish caller-supplied output count for 0x24000000 from embedded per-segment counts for 0x2400NN00.
2. Build strict segmented-envelope unit tests and compare entropy bit consumption/padding with actual Tokyo/Oahu lanes, including malformed-stream rejection.
3. Only after verified byte-lane reconstruction implement BYET predictors and float quantization, then compare every recovered numeric field with Tokyo223 native goldens. Mesh topology and UV parity follow before any viewer integration.

**Completion gate NOT met.** Keep this task active; do not notify the user as complete.
