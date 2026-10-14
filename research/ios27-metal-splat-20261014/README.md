# iOS 27 Flyover triangle Splat GPU analysis and Gaussian approximation

Research checkpoint: **2026-10-14 JST**. This directory adds focused shader/kernel validation and *lossy* standard 3D Gaussian Splatting conversion experiments to the existing [R3D independent-decoder project](../../README.md).

**Scope.** The pre-existing repository already contains Linux-only raw R3D/C3MM decoding, numeric parity tests, textured meshes, tiled region acquisition and Oahu height-layer recovery. This investigation tests the **GPU rendering equation**, the native decoder's output layout and approximation to the **Graphdeco PLY** convention. These are distinct claims; nothing here retracts existing codec acceptance tests.

## Findings with measurements

| Test | Input / reference | Observed result | Scope / caveat |
| --- | --- | --- | --- |
| iOS vs macOS Metal shader comparison | Extracted iOS 27.0 / macOS 27.0.1 VectorKit Metal IR, normalized text | **6 / 8** compared shader functions identical; splat vertex and Flyover mesh fragment differ | Shader identity does not prove equal runtime constants |
| Single real native-decoded Tokyo triangle, analytic alpha vs GPU vertex | 64×64, experimental `alphaConcentration=1`, `alphaPreFactor=20` | Alpha RMSE **1.3384304e-5**, MAE **4.750113e-6**; 1,014 GPU-covered pixels, 1,015 expected, 1 boundary pixel differing | Native-decoded reference; does not validate entire production iOS scene |
| Actual packed RGBA color path, Tokyo sample #30 | Native Apple Metal multipass RGBA16F vs independent linear-light expected color | RGB MAE **0.00045952**, RMSE **0.00058529** per channel over 1,014 pixels | Test projection and selected shader configuration |
| One Gaussian from triangle barycentric moments | Same 64×64 sample alpha kernel | RMSE **0.01583927** | Assumed test uniforms and 2D raster approximation |
| One Gaussian, optimized width/amplitude | Same sample | RMSE **0.01217569** | Not lossless |
| Three optimized Gaussians per triangle | Same sample | RMSE **0.00774542** | Single-triangle synthetic raster fitting, no occlusion/PBR |

Source measurements: [shader IR comparison](metrics/ios_vs_macos_shader_ir.json), [alpha parity](metrics/ANALYTIC_BARYCENTRIC_PIXEL_PARITY.json), [four color cases](metrics/REAL_RGB_GPU_COLOR_PARITY_4CASES.json), [Gaussian fits](metrics/gaussian_fit_to_native_triangle_pixels.json), [native material-color parity](metrics/real_rgba_native_gpu_color_parity.json).

## Rendering equation

Apple's Flyover **triangle Splat** is a finite triangle rendered with 3 barycentric coordinates rather than an infinite-support ellipse. Its fragment alpha kernel is, schematically:

`alpha = min(0.99, alphaPreFactor * (sourceRGBA.a/255) * (b0*b1*b2)^alphaConcentration)`

Here `b0+b1+b2=1` inside the triangle. Per-triangle packed colors are converted from the original channel ordering into the GPU's expected packed ordering and sRGB/linear-light domain. Encoded normals and roughness/specular options affect shaded output. Apple additionally composites via tile/intermediate/final-resolve stages; its full renderer is not merely one alpha shader.

**Important**: The values 1 and 20 above are parameters **selected for tests**, not proven runtime uniforms for actual Apple Maps. Likewise Gaussian normal thickness and conversion opacity heuristics are experimental. Complete visual equality must not be claimed.

## Corrected decoded triangle buffer layout

The native `*.native-triangle-f32` array stores positions in **vertex-planar order**, not `N × 3 × XYZ` interleaved triangle order. The old `reshape(N,3,3)` interpretation invalidates previously built triangle positions and Gaussian PLY from that path. [Rebuild script](conversion/rebuild_corrected_native_triangles.py) reconstructs the proper triangle positions from native-decoded records; [material audit](conversion/audit_native_material_mapping.py) checks packed RGBA mapping.

The [converter](conversion/export_native_triangle_ply.py) accepts flattened `float32` triples for each triangle, and 4-byte RGBA per triangle; it outputs a Graphdeco-style binary PLY with XYZ, normals, SH0, opacity logit, logarithmic scales, and quaternion. The [three-Gaussian converter](conversion/expand_triangles_to_three_gaussians.py), [SH3 padding](conversion/expand_sh0_to_sh3_ply.py) and [linear-light color correction](conversion/linearize_gaussian_sh0_color.py) are separate postprocessing experiments. They are **not** compressors or native-free R3D decoders.

CT104 research data produced corrected exports for 417,650 visible triangle Splats from the Tokyo 223-tile corpus, including approximate 1-Gaussian and 3-Gaussian versions. **The large original R3D, native output buffers and generated PLY datasets are intentionally not committed**; file size and IP/provenance warrant separate distribution decisions. See the existing repository's provenance and release manifest for test fixtures.

## How to inspect and reproduce

- On macOS with Xcode command-line tools, Metal and locally available VectorKit: look at `gpu-tests/` for actual Swift M4 experiments. Some probes refer to local Metal library locations and predecoded fixtures and must be adjusted to the host. They are *experimental scripts*, not a turnkey test suite. The native library/IR is **not bundled**.
- Run pure Python synthetic conversion/fit experiments with `numpy` and `scipy`, as required by the scripts. Check `conversion/triangle_to_3dgs.py` and `gpu-tests/fit_gaussian_to_real_apple_triangle.py` for parameters.
- For CT104 conversions, inspect source paths and CLI options via `--help` where implemented. Some research scripts embed prior CT104-specific paths and need fixtures in the expected locations; they should not be treated as deployable tooling without adapting paths.
- Use `python3 -m compileall -q research/ios27-metal-splat-20261014` as a syntax check. The portable JSON reports may be validated with `python3 -m json.tool FILE`. Numerical GPU replication requires Apple Metal and actual native fixtures.

## Materials and provenance

- `gpu-tests/`: researcher-authored Swift programs and analytic Python comparisons.
- `metrics/`: measured JSON summaries (input assumptions vary by file).
- `conversion/`: experimental researcher-authored Python converters and audits, including scripts transferred from the isolated CT104 research folder.
- `reference/`: written reverse-engineering notes.

**Excluded**: official Apple firmware/VectorKit executables, `default.metallib`, raw extracted AIR/LLVM IR and ARM disassemblies, traffic captures, credentials, R3D archives and large native/PLY data.

## Still unresolved

1. Extract actual per-tile/per-draw runtime concentration/pre-factor and raster-order group configuration from an authorized iOS render capture; compare final frames.
2. Extend pixel matching to overlapping triangles, alpha compositing, depth, PBR and the hybrid polygon mesh.
3. Check approximation quality under camera moves, thin/degenerate triangles and visibility clipping; quantify if one vs three Gaussians is worthwhile.
4. Keep independent R3D numerical reproduction and the native-oracle GPU rendering experiments separately validated.
5. Compare differing iOS vs macOS vertex stages and inspect function constants before claiming iOS shader pixel parity.

_This is research documentation, not an assertion that a Gaussian is an exact triangle-Splat._
