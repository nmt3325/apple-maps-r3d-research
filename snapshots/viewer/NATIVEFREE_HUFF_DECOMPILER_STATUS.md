# Apple Maps iOS27 R3D — native-free Huffman reverse-engineering checkpoint
Date: 2026-10-13

Scope: Independent Linux codec replacement for R3D/TRICO/BYET; no Apple iOS/macOS decoder in the final Linux pipeline. All data is from already captured tiles. Do not alter the parallel area downloader or deployed Tokyo viewer.

## Working code
- /opt/flyover-viewer/nativefree_r3d_codec_streams.py
- /opt/flyover-viewer/nativefree_byet_origin.py — all 223 Tokyo tile-local XYZ lower-bound anchors verified against native golden minima. Sparse bitmap cases 21/21 incl special 0x0577/byte-repeat pattern.
- /opt/flyover-viewer/nativefree_byet_jdescriptor.py — correctly partitions 12 XYZ +32 attribute byte lanes per tile.
- /opt/flyover-viewer/nativefree_huff_raw.py — can extract literal payload from 0xe1000002 Huff816 high-bit uncompressed variant (224 Tokyo and 77 Oahu lane payloads). This is an intermediate Huff stage, not reconstructed floats.
- /opt/flyover-viewer/nativefree_huffman_header.py — probabilistic Huff8/Huff16 family marker detector for 0x24, 0x61 headers; offsets 2..5; do not equate marker detection with decompression.
- /opt/flyover-viewer/test_nativefree_r3d.py — passes all Tokyo 223 and Hawaii72 fixtures, 590 J streams /12980 lane descriptors exactly partitioned.
- Original source tiles and native decoded goldens remain at /opt/flyover-viewer/native-r3d and /opt/flyover-viewer/decoded-native/all-223.

## Ghidra offline reverse engineering
Mac extracted native instruction slice from iOS27 VectorKit:
- /opt/flyover-viewer/ghidra-lab/huffman-arm64.bin (5912 bytes; specific Huff functions only).
- /opt/flyover-viewer/ghidra-lab/DecompileHuff.java (GhidraScript)
- /opt/flyover-viewer/ghidra-lab/output/huff8_decompress.c (decompiled pseudocode)
- /opt/flyover-viewer/ghidra-lab/output/huff16_decompress.c
- /opt/flyover-viewer/ghidra-lab/output/huff816_decompress.c (shared 975-line routine)
Ghidra 12.1.4 + OpenJDK21 installed on CT104 in isolated /opt/flyover-viewer/ghidra-lab; headless project saved. CPU affinity/reduced priority used. Ghidra C pseudocode is a research aid, not compilable C.

Apple _huff816_decompress input appears to be destination pointer(s), output count, encoded pointer, encoded size and word width8/16. Inspect the Ghidra C around 0x1b709d0a8 (magic), 0x1b709d138 (literal high-bit memcpy), 0x1b709d170 (symbol table), and 0x1b709d444+ (Huffman symbol/codelength sort). Main payload bitreader after that. Calls malloc/calloc/memcpy/free, can port as clean-room C/Python.
The code 0xe1000002 from captured data matches high-bit literal Huff816 branch. Actual per-Splat XYZ/attribute numerical arrays have NOT yet been decoded.

## Next engineering priorities
1. Extract structured Huff816 table grammar and bit reader from 975-line pseudocode; implement in new /opt/flyover-viewer/nativefree_huff816.py and compare literal cases against 301 saved 0xe1000002 payloads.
2. Implement J lane codec transformations for kinds 0..6 plus bitplane interpretation and BYET integer interpolation; require exact float/bit parity against the previously decoded 223 Tokyo splats. Do not guess values or rely solely on bounds.
3. Port TRICO mesh v3 topology, XYZ normals, texture UV and faces using Apple codec field boundaries and older open-source export conventions. Match native C3M binary.
4. Integrate Linux-only parser with arbitrary-coordinate fetcher and browser. Preserve existing viewer and parallel projects.

## Verified aggregate
Tokyo 223 R3D, 736,915 splat records from headers. Oahu 72 R3D, 304,527. 295/295 R3D TLV streams and 885 original HEIC images extracted. Every HEIC primary atlas Tokyo 223 matches native golden byte-identically. All 223 Tokyo local XYZ lower-bound anchors pass golden coordinate bounds. Complete per-Splat position/color, polygon faces and UV not yet done.

## 2026-10-13 23:34 JST — Huff816 grammar checkpoint
Independent research-only implementation: `/opt/flyover-viewer/nativefree-lab-20261013/nativefree_huff816.py`. Verified 1,462/1,462 prefix-free Huff816 compressed tables (including exact 0x24 wrapper table-size cross-check) and 962/962 literal streams across Tokyo223+Oahu72; existing 295-tile R3D/J tests still pass. **Full Huff output count, BYET kinds0–6 transforms, Splat numeric parity, mesh faces/UV and viewer integration remain unresolved.** Details/tests/next steps: `/opt/flyover-viewer/nativefree-lab-20261013/CHECKPOINT_20261013_2334JST.md`. Production viewer/fetcher untouched.
