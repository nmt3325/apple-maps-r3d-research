# Apple R3D native-free checkpoint — 2026-10-14 02:40 JST

## Scope and preservation
Read both required status files and the 23:34, 00:51, and callsite checkpoints. Work is isolated to `/opt/flyover-viewer/nativefree-lab-20261013/`. No deployed viewer, source R3D, Tokyo golden data, Oahu capture, or separate area downloader was changed. No Apple runtime decoder was invoked.

## New code
- `huff816_envelope.py`: strict standalone parser for 0x24 Huff8/Huff16 envelopes, including the segmented `0x2400NN00` branch inferred from existing Ghidra wrapper pseudocode. First segment descriptor is (u32 compressed length at +4, u64 symbol count at +8), data begins at +16; each subsequent segment has its own 12-byte descriptor. Rejects truncated/overrunning segments and trailing bytes.
- `huff816_wrapper_decode.py`: independent Huff8/16 wrapper dispatcher using the existing lab `nativefree_huff816.decode_symbols`. Checks total symbol count, output size limits, and concatenates per-segment decoded output. In nonsegmented `0x24000000` mode it explicitly requires the caller's count and does not mistake +8 metadata for the count.
- `test_huff816_envelope.py` and `test_huff816_wrapper_decode.py`: synthetic tests for segment offsets, count provenance, literal Huff8/Huff16 and malformed wrappers.
- `test_huff816_envelope_corpus.py`: read-only Tokyo223/Oahu72 corpus audit script staged for a later run.

## Tests and evidence
`python3 -m unittest test_huff816_envelope test_huff816_wrapper_decode` on CT104: **4 tests PASS**, exit code 0. These tests exercise synthetic framing and literal Huff payloads, NOT real segmented R3D streams or compressed entropy output. An attempted run of the full corpus audit was blocked by remote tool safety checks; therefore **no new real-corpus envelope totals are claimed**. Previously established 1,462 compressed Huff tables / 962 literal streams and 590 J stream boundaries remain prior-checkpoint evidence, not newly revalidated.

## Still unresolved / next
1. Obtain a complete decompilation of `_bytes_decompress` (0x1b709f3d0) in the isolated Ghidra lab, trace x3 output count at 12 Huff8/Huff16 callsites and map BYET kinds 0–6. The new envelope dispatcher cannot resolve single-stream output counts by itself.
2. Run the staged read-only corpus audit, validate real entropy bit consumption, then reconstruct J byte lanes and BYET integer/quantized float predictors. Compare every recovered Tokyo223 Splat XYZ/color/shape number with native goldens.
3. Port TRICO mesh v3 topology, XYZ, faces, UV and atlas assignments. Extend to Oahu72 and arbitrary-coordinate fetch only after actual numeric parity. Test textured polygon + Splat viewer without touching production until validated.

**Completion gate not met.** Full Linux-only geometry decode and integrated viewer remain incomplete. Do not notify as complete; leave the recurring task active.
