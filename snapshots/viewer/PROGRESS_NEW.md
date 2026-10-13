
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
