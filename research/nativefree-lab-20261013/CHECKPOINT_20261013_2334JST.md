# Native-free Apple R3D Huff816 / BYET checkpoint — 2026-10-13 (CT104)

## Scope and isolation
All new scripts and reports are confined to `/opt/flyover-viewer/nativefree-lab-20261013/`. The deployed WebGL viewer, original Tokyo/Oahu R3D files, original goldens, and parallel arbitrary-area fetcher were not modified. Only previously captured tiles were read. No Apple decoder was invoked by the Linux tests.

## Verified this run
1. Implemented independent `nativefree_huff816.py` with an MSB-first-in-little-endian-u32 bitreader, symbol table grammar, prefix-code conflict validation, literal high-bit mode, and experimental symbol decoding for a supplied output count. It reads the `0x24` outer Huff envelope and the `0x61000002` or `0xe1000002` Huff816 markers.
2. Reverse-engineered the table header: first `width` bits encode symbol count minus one; next 3 bits specify fixed code-length width; each symbol stores a code length, explicit codeword, and increment/absolute symbol value. The table is padded to a 32-bit boundary. This grammar produces valid prefix-free trees for **1,462 / 1,462** captured compressed 8-bit Huff816 streams.
3. An independent exact cross-check: the `0x24` envelope's 32-bit field at offset +4 equals **4 + the Huff816 table's word-aligned byte length** for **all 1,462 / 1,462** streams. This verifies byte-level table framing, not full decompressed numerical arrays.
4. For the high-bit literal mode, **962 / 962** captured Huff816 streams are extracted and the new decoder returns the original literal bytes exactly. Tokyo: **1,087** valid compressed tables + **800** literal streams; Oahu: **375** valid compressed tables + **162** literal streams.
5. Re-ran the existing `test_nativefree_r3d.py`: **PASS**, Tokyo223 and Oahu72, 590 BYET/J streams and 12,980 lane descriptors partitioned without remainder, 223 Tokyo native splat counts and local lower-bound XYZ anchors still valid.
6. Mac offline ARM64 callsite mapping identified the BYET byte-lane function starting at `0x1b709f3d0` and callsites to Huff8 `0x1b709c7b4` and Huff16 `0x1b709cbf4`. Further per-kind transformation analysis is required.

## Important limitation discovered
A Huff816 code tree being correct does **not** imply that the requested per-lane output count or the downstream BYET predictor is known. In the Tokyo z18 sample with 9,559 splats, asking for 9,559 Huff symbols succeeds for some lanes but overruns compressed data on others (e.g. a 573-byte kind4 lane). Reading the first BYET compact-size token as the Huff output count also leaves large amounts of entropy bytes unused. These are **exploratory hypotheses, not decoded values**. The `0x24` envelope has additional metadata and the lane kinds 0–6 use further reconstruction logic. Do not feed these experimental bytes to the viewer or compare them as final Splat attributes.

## Tests and reproducibility
```sh
python3 /opt/flyover-viewer/test_nativefree_r3d.py
python3 /opt/flyover-viewer/nativefree-lab-20261013/test_huff816_tables.py --limit 295 --output /opt/flyover-viewer/nativefree-lab-20261013/huff816-tables-report.json
python3 /opt/flyover-viewer/nativefree-lab-20261013/test_huff816_decode.py
python3 /opt/flyover-viewer/nativefree-lab-20261013/analyze_huff_count.py
```
`test_huff816_tables.py` completed successfully after strict prefix-tree validation, Huff table byte-size checks and literal exact-byte verification: `parsed_tree=1462`, `literal=962`, no errors. The last smoke test intentionally shows the output-count ambiguity; it is not a parity test. Earlier test report saved to `huff816-tables-report.json` has the same aggregate counts; rerun the command above to refresh the stricter report.

## Next work
1. Recover/decompile the isolated `_bytes_decompress` function at `0x1b709f3d0` (through `0x1b70a1914`) from the authorized Mac analysis environment into the private CT104 lab, preserving the existing Ghidra project and viewer. Determine exact Huff8/16 output counts, how the `0x24` envelope fields are used, and per-kind 0..6 transforms.
2. Validate entropy bit consumption to within the native decoder's final padding tolerance, **not** merely a valid prefix tree. Check decoded byte lanes against native intermediates if available; do not mistake direct Huff symbols for reconstructed byte planes.
3. Implement BYET predictor/delta reconstruction, produce exact XYZ/color/shape per Splat and compare per-number with Tokyo223 golden. Extend same path to Oahu72 (no native golden there).
4. Reverse-engineer TRICO mesh v3 topology, vertex XYZ, face indices, UV and atlas mapping, compare Tokyo native C3M; integrate arbitrary-coordinate fetcher + textured polygon/Splat viewer only after verified parity.

**Completion gate NOT met:** no Linux-only full Splat numeric XYZ/color/shape; no polygon XYZ/faces/UV; no integrated arbitrary-coordinate textured scene. Do not notify as complete or disable the recurring task.
