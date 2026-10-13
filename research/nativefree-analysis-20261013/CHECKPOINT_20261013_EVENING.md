# Apple R3D v2 — native-free research checkpoint (2026-10-13, evening JST)

## Read and preserved
Reviewed `/opt/flyover-viewer/NATIVEFREE_HUFF_DECOMPILER_STATUS.md` and `/opt/flyover-viewer/www/NATIVEFREE_R3D_PROGRESS_20261013.md`. Existing Tokyo viewer, downloader, source captures, native goldens and baseline decoders were not modified. New research-only workspace: `/opt/flyover-viewer/nativefree-analysis-20261013/`.

## This run: additional structural findings
- Offline Ghidra `huff8_decompress.c` dispatches the 0x24 family to a 16-byte outer envelope when header byte1 is zero; the nested stream is then passed to the shared Huff816 routine with word width 8. Nonzero byte1 selects a more complex multi-block wrapper. This is a source-level observation, not a tested implementation.
- The shared `huff816_decompress.c` reads a word-width (8 or 16) symbol-table count minus one from the top bits of the first 32-bit little-endian data word after its 4-byte header. Its symbol table uses a 3-bit prefix and variable-width code-length/code fields, plus flags for implicit, delta and absolute symbol numbering. Exact bitstream parsing, prefix validity and output parity are not yet established.
- Initial captured lane samples in `inspect_lanes.py` include 0x24 headers at offsets that vary by lane; treating every lane as a bare Huff816 stream is incorrect. The wrapper must be peeled after validating BYET kind-specific prefix sizes.

## Work files
- `inspect_lanes.py`: standalone inspection of initial captured Tokyo lane headers.
- `huff816_probe.py`: explicitly marked nonfunctional placeholder; no partially implemented decoder is exposed as working.

## Validation and blockers
The two requested status files were read successfully, and CT104 access was confirmed. Existing previous baseline remains 295 tiles / 590 J streams / 12,980 lane descriptors, but this run did NOT obtain new numerical XYZ, color, mesh or UV parity. Execution of existing decoder regression tests and a new Huff816 probe was blocked by remote tool safety checks; therefore no new test PASS is claimed. Do not mark this run complete.

## Next steps
1. Validate the 0x24 16-byte envelope and 0x61 nested stream offsets on all 295 tiles.
2. Implement Huff816 table and bitreader independently, with malformed-input rejection and literal-branch parity.
3. Reconstruct BYET/J kind0–6 lane predictors, then compare individual decoded 32-bit integers and float bit patterns against 223 Tokyo goldens.
4. Continue TRICO soup and mesh topology/UV, then verify Hawaii 72 tiles and arbitrary-coordinate fetch/display end-to-end.
