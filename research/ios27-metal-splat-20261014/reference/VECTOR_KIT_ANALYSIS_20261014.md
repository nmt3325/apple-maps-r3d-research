# Apple Maps VectorKit ARM64e static-analysis report — 2026-10-14

## Target & verification status
- Source **macOS 27.0.1 (26A434)** dyld shared cache on denkennoMacBook-Air; **this is NOT the iOS 27.0 executable**.
- Extracted binary: `../macos-vector-dylib/VectorKit` (Mach-O 64-bit arm64e, approx. 34 MiB).
- iOS 27.0 (24A437) iPhone18,3 official IPSW: targeted extract underway as a **separate** job; never label macOS symbols as iOS addresses.
- No Apple native decoder was executed and no original R3D assets were modified. Analysis is static.

## Verified function locations (macOS VM addresses)
|Function|Address|
|---|---|
|R3dResourceDecoder::decode|`0x1c2ee760c`|
|C3mResourceDecoder::decode|`0x1c2eed210`|
|r3d_world_read_mem|`0x1c34588c4`|
|r3d_world_free|`0x1c3458810`|
|createSplats|`0x1c3465a7c`|
|huff8_decompress|`0x1c3453408`|
|huff16_decompress|`0x1c3453848`|
|huff816_decompress|`0x1c3453c78`|
|byet_decompress|`0x1c3454c88`|
|key16_decompress|`0x1c3456010`|
|bytes_decompress|`0x1c3456294`|
|trico_soup_decompress|`0x1c3452e84`|
|trico_mesh_decompress|`0x1c344e10c`|
|decodeEdgebreakerMesh|`0x1c3449e1c`|
|readMeshChunkType0|`0x1c34488e8`|
|readMeshChunkType1|`0x1c3448ea8`|
|readMeshChunkType2|`0x1c3449454`|
|readTextureData|`0x1c3448550`|

## Machine instruction callsite evidence
- `bytes_decompress` -> `huff8_decompress`: **9** BLs, at 0x1c34576e0, 0x1c3457968, 0x1c34579f8, 0x1c3457bcc, 0x1c3457c60, 0x1c3457e34, 0x1c3457fd8, 0x1c34580d0, 0x1c34584ac.
- `bytes_decompress` -> `huff16_decompress`: **3** BLs, at 0x1c34582b8, 0x1c3458540, 0x1c345869c.
- `byet_decompress` -> `bytes_decompress`: 0x1c3455b64.
- `byet_decompress` -> `key16_decompress`: 0x1c3455e48.
- `trico_mesh_decompress` -> `byet_decompress`: 10 BLs at 0x1c344e7a8, 0x1c344e8dc, 0x1c3450358, 0x1c3450508, 0x1c3450c0c, 0x1c3450d5c, 0x1c3452280, 0x1c34523b0, 0x1c3452798, 0x1c3452828.
- `r3d_world_read_mem` -> `trico_soup_decompress`: 0x1c3458fac, 0x1c3460ed8; -> `trico_mesh_decompress`: 0x1c34595a0, 0x1c34630c4; -> `byet_decompress`: 0x1c345fe14, 0x1c3460d14, 0x1c3463fe4, 0x1c3464ab8.
- Direct BL counts are from disassembled Mach-O AArch64 instruction stream; they do not establish data field semantics by themselves.

## 3DGS + mesh renderer evidence
- VectorKit contains symbols/strings `FlyoverSplatsShader`, `FlyoverSplatsClearShader`, `FlyoverSplatsIntermediateResolveShader`, `FlyoverSplatsFinalResolveColorShader`, `FlyoverSplatsFinalResolveDepthShader`, `SortSplatTilesPerFrame`, `SplatProperties`, `SplatOrders`, `SplatsMeshInstance`, `FLYOVER_V2_R3D`, `FLYOVER_C3M_MESH`, `FLYOVER_C3M_ASTC_TEXTURE`.
- Mesh path has `readMeshChunkType0/1/2`, `decodeEdgebreakerMesh`, `readTextureData`, consistent with separate polygon/texture processing.
- These observations **support** hybrid Splat+mesh architecture, but do not prove the pixel blending or exact decode output.

## Paths to generated assembly
- `macos_bytes_decompress_arm64e.asm` — 2500 instructions
- `macos_byet_decompress_full.asm` — 1240 instructions
- `macos_r3d_world_read_mem_full.asm` — 12500 instructions
- `macos_trico_mesh_full.asm` — 4900 instructions

## Next steps
1. Complete official iOS 27 filesystem extraction and/or dyld_shared_cache extraction; confirm binary provenance and Mach-O UUID.
2. Repeat same function+BL inventory on the actual iOS VectorKit, compare to CT104 native slices / codec goldens.
3. Follow x3 provenance for each Huff8/16 callsite; map branch predicates to lane kinds 0..6.
4. Prove per-record XYZ/color/shape and polygon face/UV/texture exact parity with test corpus before integration.

## Confirmed Metal shader entry names (macOS VectorKit default.metallib)
Path: `/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/default.metallib`. This is a macOS 27 MetalLib, *not* an iOS 27 MetalLib.
- `Flyover::splat_vertex`
- `Flyover::splat_fragment`
- `Flyover::clear_tile`
- `Flyover::intermediate_resolve_tile`
- `Flyover::final_resolve_color`
- `Flyover::final_resolve_depth`
- `Flyover::flyover_vertex`, `Flyover::flyover_fragment`
- Function constants: `Flyover::usePbrRendering`, `Flyover::useClipPlanes`, `Flyover::useMetalBarycentricCoordinate`.
These names are extracted from actual MetalLib bytes; no GPU execution, per-pixel math or exact depth/alpha blend behavior has been established.

## Verified genuine iOS 27.0 Maps application binary (new)
- Official source: iPhone18,3 27.0 24A437 Restore IPSW, original root filesystem `/private/var/staged_system_apps/Maps.app/Maps`.
- Extracted at `../extracted/24A437__iPhone18,3/private/var/staged_system_apps/Maps.app/Maps`.
- Mach-O arm64e executable; `LC_BUILD_VERSION` platform=2 (iOS), minos=27.0, sdk=27.0; `LC_UUID=54544936-E8DB-31EA-8105-A282A2327955`.
- SHA-256 `8cd562b04a6e31ef2f8844a5f728a5dfeb6539f067b194d7f8e7b5dcfcce3451`.
- Imports VectorKit version **2043.30.6**, GeoServices **2075.30.6**, MapKit, ARKit, Metal; the **macOS** VectorKit analyzed above is version **2043.20.6** (different). Do not confuse them.
- Actual Maps app imports Look Around APIs and VectorKit debugging/configuration symbols; decoder/renderer is implemented primarily in dependent VectorKit.
- `ipsw extract --files` returned exit code 0; extracted actual iOS Maps file was verified using `file`, `otool -l`, `otool -L`, and SHA-256. The direct symbol-level iOS VectorKit reverse-engineering still awaits extraction of that dependent dylib from the iOS dyld cache.

## Confirmed: actual iOS 27 VectorKit binary (not macOS approximation)
- Extracted from the official iPhone18,3 iOS 27.0 24A437 ARM64e dyld_shared_cache under `../ios-dyld/24A437__iPhone18,3/` via `ipsw extract --dyld --dyld-arch arm64e --remote` then `ipsw dyld extract`.
- Extracted Mach-O path: `../ios-vector-dylib/VectorKit` (approximately 34MB).
- VectorKit Mach-O LC_UUID `20B9BC81-464C-3C31-9E97-129B46F7A9F8`.
- SHA-256 `92c3f65718915d705edb7ca71f8f63aa03d7c1eb3ab7c205b4fe888f2afeb3b6`.
- iOS-specific symbols found by `nm` (these addresses **are iOS**, unlike earlier macOS addresses):

| iOS 27 function | iOS 27 address |
|---|---|
| `md::R3dResourceDecoder::decode` | `0x1b6cf3334` |
| `md::C3mResourceDecoder::decode` | `0x1b6cf8ef0` |
| `_huff8_decompress` | `0x1b709c7b4` |
| `_huff16_decompress` | `0x1b709cbf4` |
| `_huff816_decompress` | `0x1b709d024` |
| `_byet_decompress` | `0x1b709decc` |
| `_key16_decompress` | `0x1b709f14c` |
| `_bytes_decompress` | `0x1b709f3d0` |
| `_trico_mesh_decompress` | `0x1b7097500` |
| `_trico_soup_decompress` | `0x1b709c238` |
| `_r3d_world_read_mem` | `0x1b70a1914` |
| `decodeEdgebreakerMesh` | `0x1b7092bf4` |
| `readMeshChunkType0` | `0x1b70916c0` |
| `readMeshChunkType1` | `0x1b7091c80` |
| `readMeshChunkType2` | `0x1b709222c` |
| `readTextureData` | `0x1b7091328` |
| `createSplats` | `0x1b70ae89c` |

### iOS 27 confirmed AArch64 direct BL edges
- `_bytes_decompress` -> `_huff8_decompress` (9 calls): `0x1b70a06e8`, `0x1b70a0980`, `0x1b70a0a14`, `0x1b70a0bf0`, `0x1b70a0c84`, `0x1b70a0e60`, `0x1b70a1008`, `0x1b70a1100`, `0x1b70a14e4`.
- `_bytes_decompress` -> `_huff16_decompress` (3 calls): `0x1b70a12f0`, `0x1b70a1578`, `0x1b70a16e0`.
- `_byet_decompress` -> `_bytes_decompress` at `0x1b709eca4`; -> `_key16_decompress` at `0x1b709ef84`.
- `_trico_mesh_decompress` -> `_byet_decompress` (10 calls): `0x1b7097b80`, `0x1b7097ccc`, `0x1b7099740`, `0x1b70998f0`, `0x1b7099ff4`, `0x1b709a144`, `0x1b709b634`, `0x1b709b764`, `0x1b709bb4c`, `0x1b709bbdc`.
- `_r3d_world_read_mem` -> `_trico_soup_decompress` (2 calls): `0x1b70a1ff4`, `0x1b70aa4b0`; -> `_trico_mesh_decompress` (2 calls): `0x1b70a23f4`, `0x1b70ac1b8`; -> `_byet_decompress` (4 calls): `0x1b70a8c60`, `0x1b70a99b4`, `0x1b70ad260`, `0x1b70adbc0`.
- iOS-specific disassembly saved under `ios27_bytes_decompress.asm`, `ios27_byet_decompress.asm`, `ios27_trico_mesh_decompress.asm`, `ios27_r3d_world_read_mem.asm`.
- **Independent consistency:** all 12 Huff call addresses are identical to those previously reported in CT104's `CHECKPOINT_20261014_CALLSITES.md`; this grounds the previously captured CT104 instruction slice to the native code positions of the official iOS 27.0 VectorKit binary. Addresses alone do not establish full build identity without a second binary hash.

### Still unsolved
The ARM64 call graph is verified, but *native-independent* Huff816 symbol-count provenance, BYET inverse transforms for all lane kinds, splat XYZ/rotation/color/opacity reconstruction, and TRICO faces/UV/texture exact parity remain unverified. Static BL counts must not be mistaken for an end-to-end decoder. The iOS MetalLib's exact shader bodies have not been extracted (only same-generation macOS MetalLib shader entry points were inspected above).

### Huffman output count x3 register provenance (iOS 27)
- All 12 Huff8/Huff16 callsites pass expected symbol count via `x3` then compare the return value `x0` against the same expected count.
- Closest `x3` assignments are from registers **x20 (4 calls), x28 (4 calls), x19 (2 calls), x24 (2 calls)**. The exact upstream formulas for these registers and mapping to BYET lane kinds still need dataflow/control-flow analysis; do not equate any prefix length with an output count without validating it.
- Per-callsite mapping saved as `ios27_huffman_callsite_audit.json`.
