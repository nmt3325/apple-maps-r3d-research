# Apple Maps Flyover triangle-Splat / Metal GPU analysis

Analysis date: 2026-10-14. Performed on `denkennoMacBook-Air.local`, macOS 27.0.1 (26A434), Apple M4 (10 GPU cores, Metal 4). **Static shader analysis + actual Metal GPU load/specialized-pipeline compilation**. We did NOT frame-capture a Flyover render or reverse the exact iOS Metal shader, and DID NOT run the proprietary R3D decoder on source tiles in this study.

## Grounded source binaries and provenance
- macOS `VectorKit.framework`, from local system dyld shared cache, version `2043.20.6`: `macos-vector-dylib/VectorKit`, Mach-O arm64e SHA-256 `bf432e44cd40bd1330f9e63db5ea71044461047321ea2ec6feb25d648290153c`.
- macOS Metal program: `/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/default.metallib`, MetalLib (macOS), SHA-256 `7cb9244f82b6c273c1e0d9d5dba6c21c8ae5ff18b5d20a88e5b785f4f2601b67`.
- Actual iOS 27.0 iPhone18,3 build 24A437 Apple Maps executable: `extracted/24A437__iPhone18,3/private/var/staged_system_apps/Maps.app/Maps`; VectorKit version `2043.30.6`, differs from macOS build.
- Actual iOS 27 `VectorKit`: `ios-vector-dylib/VectorKit` (from official iOS shared cache), arm64e SHA-256 `92c3f65718915d705edb7ca71f8f63aa03d7c1eb3ab7c205b4fe888f2afeb3b6`. The iOS R3D/TRICO/Huff call sites were separately verified in the preceding analysis.
- This document's **GPU IR and layouts are from macOS**, not assumed byte-identical to the iOS shader.

## Method and runtime GPU check
- `xcrun metal-objdump --metallib --reflection default.metallib` generated `gpu-analysis/vector-metal-reflection.txt` (~2.3 MB).
- `xcrun metal-objdump --metallib --disassemble-symbols=Flyover::splat_vertex default.metallib` emitted the full Metal AIR/LLVM-IR (340 modules); selected entry points saved as `gpu-analysis/Flyover_*.ll`.
- `gpu-analysis/gpu_splat_pipeline_structs.json`: authoritative extracted Metal function argument offsets/types (not conjectured source declarations).
- `gpu-analysis/probe_metal.swift`: successfully instantiated the actual 340-function MetalLib on the M4 GPU, obtained all seven desired functions, and verified raster order groups are supported.
- `gpu-analysis/compile_pipeline.swift`: specialized the required four vertex / one fragment Metal function constants and **successfully compiled a native `Flyover::splat_vertex` + `Flyover::splat_fragment` render pipeline** on M4. This validates a loadable pipeline, not an actual rendered frame or a matching iOS shader.

## GPU Splat representation — directly established by Metal reflection and AIR IR
`Flyover::splat_vertex` uses `vertex_id / 3` to choose one Splat from an `SplatOrders.splatIndex` array and `vertex_id % 3` for a vertex. **Three vertices form each Splat triangle.**

| GPU representation | Layout / interpretation |
|---|---|
| `CommonMesh::BufferPos4w` | `ushort4` per vertex; XYZ from components 0..2, every Splat reads three vertices |
| `FlyoverCommon::SplatProperties` | offset 0 `int albedoSrgbHex`, offset 4 `ushort2 normal`, offset 8 `ushort roughnessSpecularWeight`; struct may have padding and actual GPU buffer stride must be checked before raw memory decoding |
| `FlyoverCommon::SplatOrders` | offset 0 `int splatIndex`; depth/splat ordering indirection |
| Position dequantization | `pos = posBoundsMin + (uint16_xyz/65535) * posBoundsScale`, per tile/instance bounds |
| Color | `unpack.unorm4x8(albedoSrgbHex)` reordered to RGBA; source alpha carried with RGB |
| Encoded normal | 2x16-bit octahedral normal; decoded only when PBR is enabled; see `Flyover_splat_vertex.ll` |
| Roughness/specular | low byte roughness normalized by 255, high byte specular weight normalized by 255, plus uniform scale/offset |
| Per-tile constants | `modelView`, six clip planes, specularLight, lightDir, splatID, alphaConcentration, alphaPreFactor, specularWeightScale, specularWeightOffset, posBoundsMin and posBoundsScale |

`Flyover::SplatsArgumentBuffer` contains three bindless arrays of 16,384 **buffer descriptor slots** each (vertex, properties, order). This is *not* a demonstrated fixed 16,384 splat-per-tile limit.

### Splat fragment alpha, directly transcribed from AIR IR
For barycentric weights `b0,b1,b2`, color alpha `a`, uniforms `p = alphaPreFactor`, `c = alphaConcentration`:

`alpha = min(0.99, p * a * pow(b0*b1*b2, c))`.

The fragment shader optionally uses native Metal barycentric coordinates or manually interpolated barycentrics. As any weight tends toward zero at a triangle edge, alpha tends to zero (for `c>0`). This is a **triangle-supported, barycentric-power kernel**, not the unbounded anisotropic 3D Gaussian kernel of reference 3DGS.

### Blending and depth
- `Flyover::clear_tile` initializes tile imageblock accumulators to `[0,0,0,1,0]` (five 32-bit floats, some carrying packed half colors).
- `Flyover::splat_fragment` accumulates `color += T*alpha*rgb`, `weightedDepth += T*alpha*z`, `T *= (1-alpha)`, `totalWeight += T_old*alpha`. The shader caps alpha at 0.99. `Raster Order Groups` keep raster-order-group 0 imageblock data coherent.
- `intermediate_resolve_tile` normalizes weighted colors/depth, applies transfer functions and packs color in unorm; `final_resolve_color` composites with background color; `final_resolve_depth` yields weighted depth (discards if zero).
- `usePbrRendering`, `colorAdjustmentEnabled`, `useClipPlanes`, and `useMetalBarycentricCoordinate` are shader function constants. PBR uses oct normal, roughness/specular weight, lightDir and specularLight. Lighting/color correction and different compositing paths must be considered for view-accurate output.
- Metal code was genuinely obtained from binary `default.metallib` as AIR/LLVM IR. No native Metal source or screenshot-specific runtime trace is claimed.

## Can it be converted to reference / standard Graphdeco 3DGS PLY?
**Yes, as an approximate geometric and appearance conversion once native triangles, per-splat colors and per-tile uniforms have been decoded. No, not as a bit-exact or mathematically lossless conversion.** The primitive families differ and Apple's source has tile/scene transforms, triangle support, special alpha power, optional PBR lighting, and compositing; a standard Gaussian has center, 3D covariance, sigmoid opacity and SH colors.

One triangle vertices `V0,V1,V2`, barycentric coordinates `b0,b1,b2`, `c>0`:
- Gaussian center `mu = (V0+V1+V2)/3` (the Apple kernel is symmetric about triangle centroid).
- Let `E = [V1-V0, V2-V0]`, a `3x2` matrix mapping `(b1,b2)` to 3D tangent-plane displacements.
- Normalize the unclipped kernel `(b0*b1*b2)^c` over the triangle. Its barycentric distribution is Dirichlet `(c+1,c+1,c+1)`, with **exact second-moment covariance** `Cov(b1,b2) = [[2,-1],[-1,2]]/[9(3c+4)]`.
- Approximate 3D covariance `Sigma = E * Cov * E^T + thickness^2*(normal*normal^T)`. Eigen-decompose to `scale_0..2 = ln(sigma_i)` and `rot_0..3` a normalized `(w,x,y,z)` quaternion. Thickness is arbitrary regularization, not an encoded original Gaussian thickness.
- Peak opacity `alpha_peak = min(0.99, p * (individualAlpha/255) * 27^(-c))`; `opacity = logit(alpha_peak)` (non-clipped case peak matching). SH degree 0: `f_dc_rgb = (rgb - 0.5) / 0.28209479177387814`; `f_rest_*` can be omitted when importing with configured SH degree 0. RGB's sRGB/linear transfer and source PBR shading must be tuned to the target viewer; the demo keeps unmodified normalized source RGB.
- The triangle kernel goes *strictly to zero* on its boundary; a finite Gaussian doesn't. With clipping, varying alpha/color corrections, and specular, peak+moment matching is not a complete representation. Multiple Gaussians per triangle and viewpoint-fitted optimization may improve fidelity at the cost of more data.
- A scene containing Apple C3M polygon/texture meshes cannot be represented *losslessly* by a Gaussian-only PLY. Use hybrid mesh+Gaussian GLB/PLY or approximate each mesh surface with further Gaussian primitives.

### Executed demonstration and limits
`conversion-lab/triangle_to_3dgs.py` is a **standard-library-only proof-of-concept**, accepting already decoded triangle positions, alpha constants and `0xRRGGBBAA` and writing a Graphdeco-style binary little-endian 17-float/point PLY with XYZ, normal, f_dc_0..2, logit opacity, log scales, quaternion. It does **not** decode R3D/BYET files; exact input data still has to be recovered and validated.

`conversion-lab/synthetic_fixture.json` -> `conversion-lab/synthetic_approx_gaussians.ply` with two *synthetic*, not Apple, triangles. Read-back validation verified header size, record counts, centroids, scales, normalized quaternions and opacity.

For **synthetic triangle-domain** sample points (121-grid, equal weighting, kernel scaled to peak=1, no alpha clipping), the RMS difference between Apple's normalized barycentric-power kernel and the moment-matched Gaussian is:

| alphaConcentration `c` | RMS/peak | Gaussian value at triangle edge midpoint, true Apple kernel = 0 |
|---|---:|---:|
| 0.5 | 0.275 | 0.253 |
| 1.0 | 0.172 | 0.174 |
| 2.0 | 0.095 | 0.082 |
| 4.0 | 0.047 | 0.018 |

**These are analytical/synthetic tests only.** They do not measure visual or pixel error on real Apple Maps tiles, and `c=0.5,1,2,4` are *test values*, not observed defaults from a real Apple map tile.

## What remains before a full real-world converter is proven
1. Recover R3D native source triangle XYZ (3 vertices per primitive), per-splat albedo/normal/roughness, tile bounding scales, `alphaPreFactor`, `alphaConcentration`, and world georeference in the independent Linux/nativefree reader. Exact XYZ/color numeric parity with the 223 Tokyo / 72 Oahu golden samples had **not been established** in the earlier CT104 research.
2. Confirm whether the macOS AIR shader and the iOS 27 Metal shader have exactly matching constants/layouts. Our static macOS metal binary is a different VectorKit build.
3. Capture live Apple Maps GPU buffers/frames with Xcode GPU Frame Capture (or controlled instrumentation) and compare color/depth with the numerical model on a known tile; make sure app/OS debug policies permit capturing. No live frame capture was performed in this work.
4. Export decoded, **real** triangles through `triangle_to_3dgs.py`, compare same-camera rendered colors, positions and silhouettes against native Maps, and optimize gaussian counts/covariance/color if necessary.

## Related primary reference
- Graphdeco INRIA GaussianModel PLY and transforms: `https://github.com/graphdeco-inria/gaussian-splatting/blob/main/scene/gaussian_model.py`
- Graphdeco INRIA SH functions: `https://github.com/graphdeco-inria/gaussian-splatting/blob/main/utils/sh_utils.py`

All extracted files and reports remain under the isolated `~/ios27-maps-binary-lab/` directory. No Wi-Fi, Tailscale, system daemon, production viewer, or existing CT104 project was changed.
