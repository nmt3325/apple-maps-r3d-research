# Apple Maps iOS27 R3D v2 — Linux decoder checkpoint (2026-10-13, 22:15 JST)

Status: INCOMPLETE. No completion notification.

## Baseline and isolation
Read /opt/flyover-viewer/NATIVEFREE_HUFF_DECOMPILER_STATUS.md and /opt/flyover-viewer/www/NATIVEFREE_R3D_PROGRESS_20261013.md. CT104 linux-4ebec5ed was accessible. All new files are isolated in /opt/flyover-viewer/nativefree-research-20261013-2215/. Original viewer, captures, goldens, baseline parsers and parallel downloader were not modified.

## New findings and implementation
1. huff8_mode0_literal.py independently peels the 16-byte 0x24000000 mode0 wrapper and handles direct/nested 0xe1000002 literal Huff816. Rejects unsupported compressed modes and bad expected lengths. PASS: 15 synthetic literal roundtrips and negative cases.
2. audit_huff8.py scanned 223 Tokyo and 72 Oahu R3D files and successfully recovered 1,437 literal Huff-stage lane payloads (Tokyo 1,122; Oahu 315), zero strict-length failures. Earlier direct-only count was 301. These are intermediate Huff bytes, NOT BYET reconstructed numbers.
3. huff816_table_probe.py independently implements Huff816 compressed codebook grammar: 32-bit LE words consumed MSB-first, width8 symbol-count-minus-one, 3-bit code-width, variable code length/code and sequential/delta/absolute symbol numbering. audit_huff_table.py and audit_huff_table_oahu.py parsed 1,971 Tokyo + 688 Oahu = 2,659 real compressed 0x61000002 codebooks. All 2,659 have in-range unique symbols, unique codes, Kraft sum <=1 and zero parser errors. This verifies codebook grammar, not full decompressed bytes.
4. huff816_decode_experimental.py adds a prefix-checked Huff symbol decoder with explicit expected output count. PASS: 5 synthetic compressed two-symbol roundtrips in test_huff816_compressed.py. No real compressed Huff-stage golden comparison yet, because the BYET caller's expected Huff output length is unknown.
5. analyze_prefix.py established that all 3,094 detected Tokyo non-kind0 lane prefixes contain exactly two compact-size values before the Huff marker. In 643/645 kind6 cases the first is exactly 3 times the tile Splat count; the remaining two kind6 attribute cases equal one Splat count. Do not equate either compact-size field with expected Huff output length: 100 real-stream trials showed no 32-bit end alignment (and six first-size trials exhausted the bitstream).
6. check_wrapper_lengths.py found a new exact relationship in 1,902/1,902 compressed 0x24 mode0 envelopes: second J prefix compact-size = 16 + outer u32 field at offset4 + outer u64 field at offset8. The 123 0x24 mode1 wrappers and 1,136 literal nested wrappers do not satisfy this relation. This is framing, not an output length formula.

## Regression
Existing python3 /opt/flyover-viewer/test_nativefree_r3d.py PASS: 223 Tokyo and 72 Oahu tiles, 590 J streams, 12,980 lane descriptors, 223 Tokyo Splat count goldens and XYZ lower-bound checks, HEIC extraction and malformed-input checks.

## Missing, do not overclaim
Compressed Huff816 has not yet been matched byte-for-byte to native Huff-stage output. BYET kind0–6 lane transforms, per-Splat XYZ/color/shape floats, TRICO mesh vertices/faces/UV, Hawaii full geometry, and end-to-end arbitrary-coordinate textured polygon + Splat Linux-only display are NOT implemented. 123 multi-block 0x24 mode1 wrappers and 110 kind0 raw lanes still need decoding. Existing Tokyo viewer uses native-decoded geometry.

## Reproduction
- python3 /opt/flyover-viewer/test_nativefree_r3d.py
- cd /opt/flyover-viewer/nativefree-research-20261013-2215
- python3 huff8_mode0_literal.py
- python3 test_huff816_compressed.py
- python3 audit_huff8.py
- python3 audit_huff_table.py
- python3 audit_huff_table_oahu.py
- python3 analyze_prefix.py
- python3 check_wrapper_lengths.py

## Next tasks
1. Inspect offline iOS27 bytes_decompress and per-kind call semantics to recover exact Huff816 expected output count and 0x24 mode1 composition; avoid guessing from compact-size fields.
2. Validate compressed Huff816 bytes against a native intermediate golden; then implement strict real-stream padding/length validation.
3. Port kind0–6 BYET byte-lane predictors, signed delta and quantization; compare 32-bit integers and float bit patterns against all 223 Tokyo native goldens, then 72 Oahu.
4. Port TRICO mesh v3 topology/vertex/UV and verify against C3M golden, then integrate with separate arbitrary-area downloader and hybrid viewer only after parity.

Completion condition NOT met. Keep the recurring task enabled; continue from this checkpoint.
