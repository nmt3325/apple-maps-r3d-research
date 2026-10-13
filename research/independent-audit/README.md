# Apple R3D independent audit — 2026-10-13

Scope: readonly verification of native-decoded original C3M and native-free R3D decoder. This directory is separate from the viewer and the arbitrary-area downloader. No request credentials or signed URLs are stored.

## Observed original model

- Original photo-textured C3M mesh: 223 valid tiles (z18=1, z19=21, z20=201).
- Combined triangles: 1,922,693; unique position/UV/normal combinations: 1,203,476.
- Mesh binary layout: 16-byte header, 12*N XYZ, 8*N UV, 12*N normals, 12*F face indices.
- Full independent scan of all 223 binary files: exact lengths, finite XYZ/UV/normals, bounded triangle indices, UV within [0,1.001], image files present; zero failures. Mean vertex normal lengths equal 1.
- Source R3D splat records in Tokyo: 736,915 total, 417,650 alpha-visible; source splat triangles and original polygon faces are different primitives.
- Existing viewer has native-colored soft-triangle splats plus original C3M photo-textured polygons, not a synthesized raster-only mesh. UV-regression test passed all 223 tiles.

## Native-free codec validation

- `python3 /opt/flyover-viewer/test_nativefree_r3d.py`: PASS Tokyo223 + Oahu72 R3D container/framing, 590 BYET/J streams, 12,980 lane descriptors; all Tokyo native reference splat counts match; 3 HEIC images per captured R3D; corrupt input rejection.
- `python3 /opt/flyover-viewer/test_c3m_uv_regression.py`: PASS original C3M UV orientation and GLB roundtrip.
- `python3 /opt/flyover-viewer/nativefree_huff816_raw_strict.py --test`: PASS Huff816 literal-only synthetic roundtrip/rejection tests.
- `huffman-families.json`: independent first-signature survey of Tokyo223: 2,370 0x24 header candidates; 725 0x61; kind-0 unmarked candidates 77. Header classification is not entropy decoding.
- R3D TRICO soup has splat count, XYZ scales and eight attribute lanes. TRICO mesh v3 still needs decompression.
- Per-splat XYZ, UV indices, face indices, material channels cannot yet be recovered in a Linux-only way from newly captured compressed R3D.


## C3MM v2 pure-Python section grammar breakthrough (same day)

- New Linux-independent implementation: `c3mm_v2_parser.py`. Reads already-captured style100 C3MM v2. No Apple API or network calls, does not touch deployed viewer/downloader.
- **Exact** outer header: ASCII C3MM, uint16 version 2, uint16 observed subtype 3, uint32 number of sections (6 or 7 in captures).
- Sections are `uint8 tag; uint32 LE encoded-record-bytes (including tag); ...`. Six compressed sections have tag sequence **[0,8,9,1,5,6]**; some z9 samples also prepend 15-byte inline section tag4. Record sizes cover the file without padding or gaps.
- Compressed sections: after tag and total-size, 1-byte codec flag1, 4-byte declared uncompressed length, then header `5d00001000ffffffffffffffff` and raw LZMA1. Decode with standard Python `lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(..., max_length=declared)` because the block need not include an EOS marker.
- Earlier scan-based decoder appeared to exceed the file by 1 byte because it omitted the tag from the length calculation. **This was not a truncated stream**. Corrected parser reaches exact EOF for every sample.
- All six captured C3MM files decompressed, **36/36 LZMA sections** passing exact uncompressed-size verification. New sequential record report `c3mm-v2-sequential-report.json`. Canonical parser verified directly on Tokyo z9, Tokyo z13, Oahu z13.
- Four sections have matching per-file shared record count **N** determined from uint16 LE at start of tag8/9: size(tag0) = 12 + 4*N; size(tag8) = 2 + 8*N; size(tag9) = 2 + 4*N; size(tag5) = 9 + 4*N. Test values: Tokyo z13 N=257; Tokyo z9 N=253; Oahu N=215; Tokyo Tower N=259. These are structural relations, not yet confirmed geographic octree interpretations.
- Tag1 begins uint32 LE count **M** followed by exactly `2*M` bytes, strongly consistent with a uint16 array; e.g. Tokyo z13 M=31321 and Oahu M=18888.
- Tag5 begins two plausible float32 lower/upper values. Whether they represent elevation bounds requires semantic proof. Its ninth byte is 8 in sampled sources and the N per-cell fields can be interpreted as two uint16 quantized values up to 255. Most but not all pairs are ordered (Tokyo Dome 255/257, Oahu 204/215), so numerical elevation semantics are a **hypothesis only**.
- **NOT YET**: geographic root-index / octree semantic decoding, arbitrary-coordinate availability prediction, TRICO R3D float/face decompression or native-free full 3D export.


## Validated geographic subdivision fields

The native-free parser is now able to provide exact z/x/y from C3MM bytes; e.g. `python3 c3mm_v2_parser.py /path/to/s100_z13_x504_y3600.c3mm` displays `decodedTile` and recovered spatial index statistics.

- Tag0 uncompressed payload begins `u8 subZoom; u32 LE flippedYOrigin; u32 LE xOrigin; u8 leafZoom; u16 LE N`, then N packed uint32 indexes. For captures, `subZoom=style100_z+4`, `leafZoom=style100_z+7`, `xOrigin=16*style100_x`, `flippedYOrigin=2^subZoom-16*(style100_y+1)`.
- Inverting those equations recovers exact original style100 XYZ geographic tile coordinates for Tokyo Dome (13/7276/3225), Tokyo Tower (13/7275/3226), Hilton Oahu (13/504/3600), Tokyo z9 (9/454/201). Recovered from binary only, not from names.
- Tag0 packed indexes use local 16x16 XY bits `((value>>8)&15, (value>>20)&15)` with a low-bit marker 0/1; first entries traverse Morton/Z-order blocks. Tokyo example N257 has 256 unique XY and an extra low-bit entry, Hawaii N215 has 215 unique XY. Mapping of low-bit marker to style98 high-zoom h must NOT be assumed one-to-one.
- Actual R3D coverage cross-check: Oahu 72 of 72 high-resolution style98 h0 captures match the C3MM XY index. Tokyo matched 147 ordinary h0 tiles; 34 captured h1 records are not directly represented by the same z17 marker (unknown hierarchy semantics).
- Additional cross-section sizes validated: tag1 has `4+2*M` bytes; tag6 has `1+2*(M-N)` bytes, where M=uint32 first field in tag1. This strongly suggests a parent/child node table, but link semantics remain unknown.
- Check tools: `c3mm_v2_parser.py`, `check_tiles_oahu.py`, `check_tiles.py`. The existing downloader and viewer are unchanged.

## Browser verification

`node /opt/flyover-viewer/test_wasd_flight.cjs` PASS: W forward52.5m, E rise52.5m, Q descent43.05m, D strafe52.5m, mouse look, return to orbit; original model loaded.

## Next milestones

1. Continue mapping the decoded Huff816 byte arrays back through BYET/J predictor lane kinds 0..6, using saved reference arrays as an exact test oracle.
2. Recover 3 XYZ and eight material floats per Splat from the R3D soup.
3. Decode TRICO mesh v3 topology and quantized XYZ/UV/normals for full byte/geometry parity.
4. Test Oahu Hilton R3D72 using Linux-only decoder, then connect arbitrary-area fetcher to the original hybrid viewer.
5. Match native soft-triangle shader constants and tile accumulation/compositing to device screenshots.

Current status: original Tokyo asset extraction and original hybrid viewer work with Apple's offline decoder; full arbitrary-location Linux-native-free reconstruction is not complete.

## Native-free Huff816 byte decoder (continuation, 2026-10-13)

New independent implementation in `huff816_nativefree.py` parses the captured 0x61 Huff816 codebook format and decodes its MSB-first bitstream over little-endian 32-bit words. It also handles the 16-byte 0x24 wrapper and its explicit 0xe1000002 literal branch. It does not load or call Apple's decoder. The codebook grammar was first cross-checked against 1,971 observed tables in the separate read-only research folder; the independent decoder then passed its own two-symbol synthetic frame, wrapper, literal and malformed-input checks.

Corpus verification using `audit_huff816_nativefree.py` and the saved Tokyo + Hilton Oahu captures:

- Tokyo: 223 tiles; 1,471 wrapped frames decoded to the exact wrapper-requested byte count (234,572 bytes) plus 500 direct 0x61 frames decoded to the size in the preceding compact field (336,779 bytes). Also handled 899 literal wrapper frames and 224 direct literal dispatches.
- Oahu: 72 tiles; 554 wrapped frames decoded to the exact wrapper-requested byte count (104,160 bytes) plus 134 direct 0x61 frames decoded to the preceding compact size (64,191 bytes). Also handled 237 literal wrapper frames and 77 direct literal dispatches.
- Combined: 2,659 compressed Huff816 frames and 739,702 output bytes decoded, with zero Huff816 decode rejections. One Tokyo header candidate had no valid compact prefix and remains unclassified; 77 Tokyo + 33 Oahu lanes had no header candidate. These details are in `huff816-nativefree-report.json`.

This advances the Huffman byte stage only. The decoded arrays have not been proven byte-for-byte against Apple's private intermediate arrays, and BYET/J lane reconstruction, point ordering, quantized XYZ, eight appearance channels, TRICO mesh topology/UVs and splat compositing remain unfinished. The native-free decoder has not yet produced complete 3D output.

## BYET/J kind-0 XYZ byte observation

Across the 223 Tokyo native-golden fixtures, 21 active kind-0 XYZ lanes each contain exactly 3*N bytes. The first N bytes match the low byte of the corresponding native-decoded quantized coordinate on 20 lanes (3,732/4,029 point-byte comparisons). The remaining Z lane differs by +1 for all 297 points and uses sparse origin header `0877065cfeff5afefff5ff`; its origin interpretation remains unresolved. This is a narrow observed correspondence only: it does not decode the trailing 2*N bytes or any other BYET/J kind. Reproduce with `python3 audit_byet_kind0.py /opt/flyover-viewer/native-r3d /opt/flyover-viewer/decoded-native/all-223 --report byet-kind0-native-golden-report.json`.
