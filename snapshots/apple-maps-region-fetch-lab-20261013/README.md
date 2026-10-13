# Apple Maps regional 3D acquisition lab — CT104 (2026-10-13)

This lab is completely separate from the existing Apple Flyover analysis. Do not modify /opt/flyover-viewer or the live mitmproxy capture.

## Reproduce a geographic subset

Run from this directory:

```bash
B=/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013
python3 "$B/tile_plan.py" --lat 35.7089 --lon 139.7480 --radius-m 70 --output "$B/example.plan.json"
/opt/mitmproxy-flyover/bin/python "$B/capture_extract_v2.py" "$B/example.plan.json" my-region
python3 "$B/export_height_mesh.py" "$B/exports/my-region" 2
python3 "$B/export_native_subset.py" "$B/exports/my-region"
python3 "$B/combine_layers.py" "$B/exports/my-region"
```

The native subset exporter uses existing read-only decoder outputs in /opt/flyover-viewer/decoded-native/all-223. Freshly captured data from another area needs a corresponding new iOS VectorKit decoder pass.

## Verified results

- Captured Tokyo Dome sample: 40/76 planned tiles present: 37 style98, 1 style99, 2 style100.
- Native-colored triangles: 56,550; polygonized height raster: 130,050 triangles.
- Hybrid approximation: 186,600 triangles, 5,772,508 bytes.
- Sample result: exports/capture-validation-b/hybrid_preview_approx.glb.
- Replay of an old, exact captured tile URL returns HTTP 403. Changing coordinates also yields 403. It is NOT established whether expiration, IP/client binding, or other conditions cause this.
- No independent unattended acquisition of a completely new area is established.

## Format caveats

- Style98: proprietary R3D with native triangle splat decoder output, NOT a standard portable Gaussian file.
- Style99: 512x512 uint16 raster polygonization; vertical scale/offset not calibrated. This is NOT necessarily an original textured building polygon model.
- Style100: C3MM v2 metadata. z13 and z9 are observed levels.
- Native Gaussian blending and proprietary shader have not been replicated.

Do not publish map content or credentials. Apple Maps terms place restrictions on extraction, reuse and bulk downloads.
