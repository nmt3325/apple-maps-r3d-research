# Apple Maps Flyover R3D v2 — Linux native-free decoder progress

Updated: 2026-10-13 19:50–20:xx JST. Host CT104, in a separate `/opt/flyover-viewer/nativefree-*` workspace.

## Objective
Receive an R3D network tile captured by `fetch_area_98.py` at arbitrary coordinates, decode native C3M textured polygon XYZ/UV/faces/normals + Splat XYZ/material without calling Apple's iOS27 VectorKit or any Apple decoding APIs, then load the existing viewer. **Full Linux geometry decode is still in progress.**

## Verified discoveries and operational code
1. Apple style98 R3D v2 starts with `3d 96 59 2e`, followed by uint32 LE version2, bytes `01 02 00`.
2. Outer TLV at absolute byte11 uses pairs of unsigned LEB128 varints `tag,length`; entire file splits without remainder into tags `[1,2,3]`.
3. Outer tag1 = splat group: one version byte then TLVs `[1,1,4,2,3]`. Tag3 contains **TRICO triangle soup v1** compressed payload starting `d1 22 c9 07 01 00 00 00`.
4. Outer tag2 = C3M mesh/material group: one version byte then TLVs `[1,1,2,3]`. Tag2 contains **TRICO polygon mesh v3** compressed payload starting `e1 21 66 24 03 00 00 00`. Tag3 is texture container with TLVs `[1,3,5,6,8]`.
5. Each soup frame has uint64 LE Splat record count at offset8, 8 channels u32 at offset16, 9 float32 quantization scales starting offset20. Tokyo **736,915 Splat record counts match iOS golden for all 223 tiles**. Newly captured Hawaii has **304,527 Splat records** according to original compressed headers (no golden comparison yet).
6. Mesh v3 includes three float32 quantization values at offsets8,12,16. Both types validated 295/295.
7. Apple `_read_size.64545` uses a distinct compact integer encoding where a unary prefix of low-order set bits specifies 1–8 LE bytes and the value is right-shifted by the byte width. `0xff` is an extended 8-byte LE integer. Independently implemented `nativefree_trico_size.py` with roundtrip tests.
8. TRICO soup at byte56 contains exactly **two separately compact-size-length-framed BYET quantized float blocks**. The first is fed to the XYZ coordinate decoder, the second to the attribute decoder as observed in native `_trico_soup_decompress`; both blocks begin `25 00` (BYET header). The frames cover 100% of compressed soup bytes for all 295 tiles with zero padding or mismatch. The numerical arrays are **still compressed**.
9. `_bufrw_read_byet_quantf` contains two calls to `_byet_decompress`; numerical quantizer delta decoding needs a standalone port.
10. Each source tile contains exactly three standalone HEIC images. Extracted directly without Apple API using `nativefree_extract_heic.py`. Tokyo **223/223 primary HEIC atlases SHA-256 identical** to native decoder output, plus 446 auxiliary atlases. Hawaii **216 HEIC streams** across 72 tiles. HEIC #0 is color, two smaller auxiliary grayscale images (roles not yet verified).
11. Per-tile R3D local rotation matrix and ECEF translation are read directly without iOS, validated determinant near1 and center near Earth radius.
12. Legacy pure-Go `retroplasma/flyover-reverse-engineering` handles **C3M v3**, not the new TRICO payloads. It cannot be used as drop-in parser; could adapt only export/coordinate code.
13. Native codec functions and callgraph investigated in Mac iOS27 ARM64 VectorKit for interoperability:
`_r3d_world_read_mem`, `_trico_soup_decompress`, `_trico_mesh_decompress`, `_bufrw_read_byet_quantf`, `_byet_decompress`, `_bufrw_field_next`, `_read_size.64545`, `_huff8_decompress`, `_huff16_decompress`, `_huff816_decompress`.

## CT104 code + tests
- `/opt/flyover-viewer/nativefree_r3d_codec_streams.py` strict R3D/TLV/TRICO parser, exports compressed mesh/soup + 2 soup blocks.
- `/opt/flyover-viewer/nativefree_trico_size.py` compact integer codec (decode + encode).
- `/opt/flyover-viewer/nativefree_extract_heic.py` original embedded HEIC/geo extraction.
- `/opt/flyover-viewer/nativefree_r3d_field_tree.py` exploratory recursive TLV visualizer.
- `/opt/flyover-viewer/nativefree_prepare_region.py` packages an independently downloaded arbitrary area into private folder, HEIC + compressed TRICO + per-tile metadata, with **explicit flags that mesh and Splat XYZ not yet decoded**.
- `/opt/flyover-viewer/test_nativefree_r3d.py` 295 original files tested incl 223 exact source Splat counts & first HEIC golden, quantization scales, 3 embedded textures/tile, strict boundaries & corrupt input rejection: **PASS**.
- Test report `/opt/flyover-viewer/nativefree-decoder-tests.json`.
- Tokyo source 223 tiles under `/opt/flyover-viewer/native-r3d`, native goldens in `/opt/flyover-viewer/decoded-native/`.
- New Oahu source72 tiles under `/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20`.
- Staged Hawaii **separately without overwriting original viewer** at `/opt/flyover-viewer/nativefree-regions/oahu-hilton-capture-20261013/` with HEIC and original compressed TRICO frames, 72 tiles, 304,527 Splat count header, 216 HEICs.

## NOT achieved yet
The native-free TRICO bitstream decoder has **not** produced Splat XYZ, materials numerical arrays or genuine C3M polygon face indices / positions / UVs. The existing Tokyo viewer at http://100.104.153.80:8891/ uses *earlier* native-decoded geometry, and thus Hawaii is **not yet flyable in full 3D using Linux-only code**. Do not falsely label independently prepared Hawaii region a decoded 3D scene.

## Exact immediate next reverse-engineering work
1. Port `_byet_decompress` into a stand-alone Linux module (native function 0x1b709decc, about 4.7KB) and `_bufrw_read_byet_quantf` (0x1b70afc4c), including delta prediction and quantization. Each TRICO soup's 2 BYET blocks should output pointCount x (3 XYZ + 8 attributes).
2. Compare output floats **within bounds or bitwise** against the 223 saved native fixture `*.decoded`.
3. Port `_trico_mesh_decompress` (0x1b7097500), 19.7KB ARM64, which uses BYET + topology/huffman; verify original XYZ / UV and face indexes against `*.c3m-*.bin`.
4. Once float/mesh numerical parity proven, make `nativefree_prepare_region.py` produce actual scene geometry and combine with viewer, optionally a `lat/lon` form invoking preexisting fetch tool. No need for Apple iOS simulator then.

## Run native-free reader
```bash
python3 /opt/flyover-viewer/test_nativefree_r3d.py
python3 /opt/flyover-viewer/nativefree_r3d_codec_streams.py /opt/flyover-viewer/native-r3d --expected-native-manifest /opt/flyover-viewer/decoded-native/c3m-all-223/batch.json
python3 /opt/flyover-viewer/nativefree_prepare_region.py --name my-new-region --input-dir /path/to/extracted/r3d
```

No OAuth or accessKey values are written into the exported parser reports. Existing Tokyo viewer and other thread downloader workspace not modified.


## New: Quantized local XYZ anchor and independent georeferenced Hawaii samples

Using the `_bufrw_read_byet_quantf` fixed 0x0025 frame header, two compressed Soup blocks begin with `25 00` in 295/295 tested R3D files. Immediately after the compact per-frame header value12 in first/coordinate stream, three signed little-endian int32 encode a local XYZ lower-bound anchor. Multiplying each integer by soup quantization step0 yields local metric XYZ. First stream header values10/11 use a different packing, **and are not read as int32**.

Tested *all 202* Tokyo tiles with coordinate stream header12 against earlier known native-decoded real Splat vertices in 202 `*.decoded` golden fixtures: each XYZ coordinate minimum is >= its compressed native-free anchor (tolerance 0.001m); maximum gap 22.48m. This recovers a lower-bound reference, **not the actual positions of each Splat**.

For new Oahu 72 tile corpus: 71 have header12 and native-free XYZ anchors, 1 unsupported header variation is skipped rather than fabricated. Transformed anchors through original R3D 3x3 ECEF matrix and translation then WGS84 geodetic: lon -157.83818…-157.83577, lat 21.28136…21.28395, ellipsoid height ~32–76 meters, the intended Hilton Hawaiian Village Oahu vicinity.

Usable GeoJSON of 71 one-per-tile *lower-bound anchors*, not decoded individual Splat vertices:
`/opt/flyover-viewer/www/nativefree/oahu-nativefree-anchors.geojson`.
Native-free script: `/opt/flyover-viewer/nativefree_georef_anchors.py`.
Regression suite passes all original tests + 202 XYZ golden parity constraints: `python3 /opt/flyover-viewer/test_nativefree_r3d.py`.

## Update: full BYET/J per-byte-lane directory recovery

Native-only runtime not used in the Linux tools. Architecture-specific iOS binary was inspected *offline solely to understand interoperability*; the following parsers run in independent Python on CT104.

### Signed XYZ origin in compressed 10/11-byte cases
- For signed TRICO origin block with raw size12, original 3x int32 LE anchor is direct.
- In size10/11 blocks, decoder markers 0x04 or 0x08 followed by a uint16 LE sparse presence bitmap and packed signed bytes. A mode-aware sign-extension of omitted bytes reconstructs 20/21 exceptional Tokyo anchor triples without native Apple APIs. Rare 0x08+0x0577 format remained ambiguous; rejected rather than inventing a coordinate.
- All recovered 222/223 Tokyo XYZ *lower-bound anchors* verified by comparison against native-decoded real Splat coordinate minima. The largest coordinate-minimum gap was 22.48m. These reference minima are not any individual Splat coordinates.
- All Hawaii 72/72 tile lower XYZ anchors now independently extracted and georeferenced, updated GeoJSON: `/opt/flyover-viewer/www/nativefree/oahu-nativefree-anchors.geojson`.

### J entropy stream parsing discovery
- Both separate TRICO soup quantized blocks (XYZ, eight extra attributes) contain BYET flag 0x80, nested 16-bit marker 0x004a. Every one of **590** streams across 295 tiles agrees.
- REVISED EARLIER BITMAP INTERPRETATION: `_bytes_decompress` encodes **byte lanes**, not point indices, in its two leading bitmaps. Each XYZ record is 3 signed int32 => 12 byte lanes; each eight-attribute record is 8 signed int32 => 32 byte lanes. Bitmask A is `ceil(lanes/8)` bytes. Let `active=popcount(A)`. Bitmask B is `ceil(2*(active-1)/8)` bytes. The two control bits for each additional active lane signal explicit vs inherited lane kind and packed size.
- Lane kinds are integers **0 through 6**. If missing in bitmap A, default lane code1 with zero compressed size. Active lanes may inherit kind/length from preceding active lane. Kind4 or kind6 also marks the previous lane as part of a multi-byte group.
- Independent `/opt/flyover-viewer/nativefree_byet_jdescriptor.py` decodes every per-lane offset, length, and kind. **590/590** XYZ/attribute streams and **12,980** lane directory entries were parsed. Sum of every lane's compressed byte length exactly equals all remaining J stream bytes for *all 590 captures* (no trailing padding and zero mismatches). Full numerical lane codecs remain unimplemented.
- Earlier exploratory `nativefree_byet_jbitmap.py` was replaced by a note pointing to the corrected byte-lane code (former per-point assumption was incorrect).
- Mac iOS27 offline disassembly shows per-kind reconstruction calls to `_huff8_decompress` and `_huff16_decompress` from `_bytes_decompress`. Next implementation target: portable versions of these codecs and their BYET lane kind0..6 predictors, then compare 223 native fixtures byte-by-byte.

### New code and reusable data
```text
/opt/flyover-viewer/nativefree_byet_origin.py
/opt/flyover-viewer/nativefree_byet_jdescriptor.py
/opt/flyover-viewer/nativefree_r3d_codec_streams.py
/opt/flyover-viewer/nativefree_prepare_region.py
/opt/flyover-viewer/nativefree_georef_anchors.py
/opt/flyover-viewer/test_nativefree_r3d.py
/opt/flyover-viewer/nativefree-jdescriptor-tokyo.json
/opt/flyover-viewer/nativefree-jdescriptor-oahu.json
/opt/flyover-viewer/nativefree-regions/oahu-hilton-nativefree-jdir-v3/
/opt/flyover-viewer/www/nativefree/oahu-nativefree-anchors.geojson
```
Use `python3 /opt/flyover-viewer/test_nativefree_r3d.py` to reproduce: 223 Tokyo +72 Oahu tiles, 223 exact Splat record counts matching native, 222 geometric lower-bound checks, 590 J lane directories exactly cover all bytes, 295*3 HEIC and sample corrupt-input rejection. The original Tokyo WebGL hybrid viewer is still running and uses previously decoded geometry, not yet the independent numerical BYET stage. Hawaii independent **actual Splat XYZ and C3M vertex/index/UV** are still NOT decoded.
