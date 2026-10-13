# Apple Maps iOS 27: Flyover R3D native splat reconstruction

Updated: 2026-10-13 (JST)
Host: CT104 (Tailscale only)
Status: **223 / 223 original R3D tiles successfully decoded, reassembled and rendered.**

## Original data / provenance
- Captured on an authorized, non-jailbroken iPhone running iOS 27 via mitmproxy on CT104.
- Captured request style=98 payload signature: 0x2e59963d (little-endian 3D 96 59 2E), R3D v2.
- Source flows: `/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm`.
- 223 R3D tiles exported to `/opt/flyover-viewer/native-r3d/`, without URL, signed token or access key.
- Native decoder: `r3d_world_read_mem`, located in Apple's iOS27 VectorKit on an isolated iOS 27 simulator running on connected Mac.
- Native splat constructor: `geo::r3d::createSplats`, reverse-engineered to a simulator function beginning with the verified sequence `sub sp,#0xf0; stp d9,d8; ...; ldrsw x22,[x0,#8]`.
- App source on Mac: `/Users/denken/.desktop-mcp/mac-6dd4602a/work/ios27-vectorkit-analysis/decoder-harness/main.mm`.
- Actual decoded outputs on CT104: `/opt/flyover-viewer/decoded-native/all-223/`.

## Recovered true source geometry and material
- Full 223/223 decoded with native status=0.
- Exactly **736,915 original splat records**.
- `createSplats` produces **3 native XYZ float32 vertices per splat**, total **2,210,745 native triangle vertices**.
- Native triangle vertex buffers: one `*.native-triangle-f32` file per tile, exactly 36 bytes per record.
- Native material buffers: one `*.native-material20` file per tile, exactly 20 bytes per record.
- Native material layout: first 4 bytes are packed uint8 red, green, blue, alpha; next 16 bytes are 4 float32 material channels.
- Nontransparent original records: **417,650 triangles**, **1,252,950 visible triangle vertices**.
- Shader `Flyover::splat_vertex` uses a triangle per record (vertex ID / 3 and modulo 3).
- Shader `Flyover::splat_fragment` computes smoothed alpha from a barycentric-coordinate product raised to an exponent; this is a **soft triangular splat**, not proven to be conventional elliptical 3D Gaussian Splatting.
- Native octahedral normals are decoded from 2 packed material floats (type 6), geo-transformed to east/up/south; optional diagnostic lighting is available in viewer.

## Reconstructed scene
- Native triangle geometry / packed RGB and alpha: original iOS27 VectorKit output, preserved and geo-referenced via per-tile R3D ECEF matrix.
- Browser uses Three.js BufferGeometry triangles, vertex RGBA, barycentric fade.
- Native opacity exponent, compositing mode, depth sorting and Apple's intermediate resolve are NOT pixel-exact; browser provides approximate soft triangle opacity and adjustable strength.
- The independent green polygon layer is a visualization of captured 16-bit style99 height rasters; it is **not a direct export of Apple's full original textured polygon meshes**.
- Viewer has *R3D only*, *Hybrid (R3D+heightfield)*, prior point-sprite comparison, native normal lighting, blend controls and orbit/camera controls.
- Viewer: http://100.104.153.80:8891/ (Tailscale network).

## Usable outputs
- Accurate native triangular splat geometry with vertex RGBA: `/opt/flyover-viewer/www/Apple-Flyover-iOS27-native-417650-triangles.glb` (25,060,048 bytes). Successfully reimported and checked: 417,650 triangles, 1,252,950 vertices.
- All 736,915 R3D points with native RGB/alpha (including alpha 0): `/opt/flyover-viewer/www/Apple-R3D-native-all-223-colored-points.ply`.
- Native normals PLY: `/opt/flyover-viewer/www/Apple-R3D-native-all-223-with-normals.ply`.
- Native visible points GLB: `/opt/flyover-viewer/www/Apple-R3D-native-visible-417650.glb`.
- Derived green 16bit raster polygons GLB: `/opt/flyover-viewer/www/Flyover-captured-heightfield.glb`.
- WebGL source: `/opt/flyover-viewer/www/index.html`; native geometry processor: `/opt/flyover-viewer/build_native_triangle_splats.py`; decoded normals and point cloud processor: `/opt/flyover-viewer/build_full_native.py`.
- Model delivery HTTP confirmed from a separate Tailscale host, and actual native triangle scene tested headlessly in Chromium.

## Remaining research for exact Apple Maps rendering
1. Reproduce the exact uniform exponent/opacity and multistage order-independent composite pipeline from Apple `Flyover::splat_fragment` and `FlyoverTileMemory` intermediate resolve stages.
2. Recover remaining native *polygon* geometry and texture layers, not just PNG height rasters.
3. Verify Apple Maps final display quality, occlusion, texture/PBR lighting and LOD compared with a real device screenshot.

## Security and operations
- CT104 `flyover-capture-viewer.service`: persisted; localhost 127.0.0.1:8891 forwarded via Tailscale Serve TCP 8891.
- Original mitmproxy `mitmproxy-flyover.service`: persisted; localhost port 8890 forwarded via Tailscale Serve TCP 8890, with R3D requests containing credentials in private capture. Do not expose raw capture publicly.
- Temporary upload service/port 8894 stopped and Tailscale forwarding removed.
- iOS 27 Simulator test code calls nonpublic VectorKit functions; keep testing isolated.

## Continued reconstruction (2026-10-13, later session)
- Confirmed `R3dResourceDecoder::decode` calls both native `createC3mModel` and `createSplats` constructors, so the binary supports a mesh plus soft-triangle-splat construction path. **Do not claim native C3M polygon extraction is completed**; the current green proxy remains derived from style99 PNG.
- Examined exact iOS27 `Flyover::splat_fragment` Metal AIR:
  `alpha = min(0.99, alphaPreFactor * sourceAlpha * pow(barycentric.x * barycentric.y * barycentric.z, alphaConcentration))`.
  Fragment writes to the five-float `FlyoverTileMemory::SplatAccumView` using front-to-back transmittance, color weighting and weighted depth.
- `intermediate_resolve_tile` normalizes accumulated RGB by accumulated alpha, performs transfer functions and composites into a packed output; `final_resolve_color` blends this against background with further color-space transfer.
- Web viewer updated to use the **exact source alpha equation**, keeping `alphaPreFactor` (default test value 81) and `alphaConcentration` (test value 1.0) as **user-controlled estimates** since the official runtime uniform values have not been recovered.
- 417,650 triangles are camera depth-sorted back-to-front after orbit end, approx 129ms per sort on headless Chromium CT104; intended to reproduce standard source-over compositing more closely than unordered drawing (still not pixel-exact Apple raster-order-group / deferred tile resolve).
- Calibrated style99 height proxy by sampling captured R3D geodetic positions: pixel-sample corr approx 0.71; 2,383 raster cells with >2 native points each gave least-squares top-height relation `h [m] ≈ 51.68 + 0.788 * rawPNG`. This is a statistical approximation, not proof of the Apple raster encoding or native polygon meshes.
- Enabled opt-out PNG clipping to the actually decoded R3D geographic bounds, reducing large unrelated heightfield artifacts.
- Exported `Apple-Flyover-hybrid-native-splats-calibrated-proxy.glb` (27,611,336 bytes): separate named meshes for ORIGINAL 417,650 Apple native Splat triangles and 15,846 faces of ESTIMATED PNG height proxy, confirmed by trimesh reimport.
- Tested live viewer native R3D-only and hybrid scenes with Playwright/Chromium; shader compiles without errors after alpha formula update.
- Captured all Apple request style counts: 360 style98 requests, 10 style100 R3D index requests, 7 style99 height PNG requests; 2D vector maps also present. No direct classic style15 native C3M tile requests in this capture.
- Native iOS27 R3D struct candidate at world+0x350 was inspected; no sufficient proof that it contains mesh objects. Further mapping required to export native `geo::c3m::Model` geometry/textures.

## Latest browser verification
- Default viewer now starts close to dense original R3D triangle geometry (no misleading green proxy).
- Browser test confirms 417650 native soft triangles visible and distance sort is refreshed in approximately 151ms.
- Hybrid toggle remains available for calibrated estimated polygon proxy comparison.
- The iOS27 original C3mModel polygon textures/geometry are not yet exported, despite confirmed dual decoder paths.


## Original native HEIC-textured polygon mesh reconstruction (new, 2026-10-13)

**SUCCESS:** This supersedes the earlier note that the original C3M polygons were unavailable.

The isolated iOS27 Simulator R3D decoder revealed the following genuine C3M arrays for every one of the 223 captured R3D tiles:
* r3d_world_t +0x2b0: float32 XYZ position array
* +0x2c8: float32 UV atlas coordinates [0..1]
* +0x2e0: float32 surface normals
* +0x2f8: uint32 per-triangle position index array
* +0x310: uint32 per-triangle UV index array
* +0x328: uint32 per-triangle normal index array
* +0x338/0x340: texture records count and pointers
* native texture record +0x608 pointer to image bytes, +0x808 image byte length (texture slot 0)
* the texture atlas is **HEIC**, recognized by ftypheic, decoded to 832x832 PNG in sample. Every one of 223 tiles has one valid HEIC atlas.

Extracted **1,922,693 native C3M polygon triangles** across 223/223 tiles (223 atlases) with indexed UVs and normals. No PNG-generated proxy geometry is used for the C3M viewer.
The source atlas bytes are in `/opt/flyover-viewer/decoded-native/c3m-all-223/*.texture-0-0.heic`. Browser-compatible JPEG transcodes in `/opt/flyover-viewer/www/c3m-textures/` (223 images, 17.4 MB total). Native source vertex/UV/normal/index arrays in `/opt/flyover-viewer/decoded-native/c3m-all-223/` (1338 arrays). Coordinate transforms from original R3D ECEF matrix georeference each mesh into exact same east/up/south world coordinates as previous native splats. Builder: `/opt/flyover-viewer/build_native_c3m_geometry.py`. Manifest `/opt/flyover-viewer/www/data/native-c3m.json`, UV-indexed geometry: `/opt/flyover-viewer/www/c3m-geometry/` (~61 MB).
**Actual web hybrid:** `http://100.104.153.80:8891/` loads true original C3M UV/HEIC textures + 417,650 original native triangle splats. z19 LOD = 21 original C3M tiles / 247,750 polygon triangles / 21 original image atlases, web-rendered and browser-tested. z20 nearby 50 original tiles = 380,972 polygon triangles, tested. All z20 = 201 source tiles / 1,660,801 triangles (high resource).
**Exported verified GLBs (all original geometry and textures):**
* `Apple-Flyover-iOS27-original-HEIC-textured-C3M-19.glb` -- 21 native photo-textured meshes, 247,750 faces, 21 original images.
* `Apple-Flyover-iOS27-original-HEIC-textured-C3M-20.glb` -- 201 native photo-textured meshes, 1,660,801 faces, 201 original images, ~152.8 MB.
* `Apple-Flyover-iOS27-original-textured-C3M-plus-R3D-splats-19.glb` -- true 21 textured meshes plus 417,650 genuine native splat triangles, 22 nodes.
* `Apple-Flyover-iOS27-original-textured-C3M-plus-R3D-splats-20.glb` -- true 201 textured meshes plus 417,650 genuine native splat triangles, 202 nodes, 2,078,451 faces total, ~177.8 MB.
Reimports validated face counts and texture material counts using trimesh.

**Remaining visual differences**: soft splat fragment shader and Apple-specific tile memory/deferred accumulation/sorting/occlusion not pixel-exact; native realtime Apple camera/LOD selection not exactly recovered. GLB cannot embed Apple custom Splat shader.

**Mobile:** Sidebar transformed to a collapsible settings drawer, 3D canvas full iPhone width, horizontal scroll toolbar. Test with Playwright simulated 390 x 844. Existing user captures and mitmproxy data remain private. Temporary authenticated upload port 8894 shut down after using encrypted Tailscale Taildrop file transfer.


## Corrected HEIC atlas mapping (2026-10-13, 18:50 JST)

User detected incorrectly mapped polygon photographic texture. Root cause: the native C3M UV convention is OpenGL/OBJ V (bottom-left origin) as shown by the legacy retroplasma/flyover-reverse-engineering OBJ writer (`vt U V` with unmodified source data), whereas the new Three.js TextureLoader layer had wrongly forced `texture.flipY=false` as if raw Apple UV was glTF top-left.

We A/B-rendered exactly the same native C3M z19 mesh tile using both settings. With `flipY=false`, facade windows were smeared and projected onto roof areas; `flipY=true` maps windows, facades and roofs much more coherently to the reconstructed geometry. Fixed both `/opt/flyover-viewer/native_c3m_layer.js` and the embedded code in live `/opt/flyover-viewer/www/index.html` to `texture.flipY=true`. Screenshot comparison: `c3m-texture-uv-before-after.jpg` in the viewer web root.

Existing GLB exports do **not** require regeneration: `trimesh.exchange.gltf` exporter already reverses the V coordinate during writing of glTF TEXCOORD_0, and its importer reverses it on reading. We briefly tested a separately suffixed double-flipped sample, verified it was incorrect, removed it and restored the original exporter. Previous z19/z20 original photo-textured GLBs preserve the correct glTF orientation.

Regression test added: `/opt/flyover-viewer/test_c3m_uv_regression.py`. PASS: 223 native UV buffers, legacy OBJ UV convention, fixed WebGL source, original sample GLB export/import UV roundtrip. Chromium rendered 21 original z19 C3M meshes with 247,750 faces and 21 decoded atlases plus 417,650 native splat primitives without JS errors after the fix. This fixes the primary UV error; Apple-specific Splat compositing remains approximate.
