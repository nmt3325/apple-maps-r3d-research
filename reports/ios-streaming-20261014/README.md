# iOS native streaming validation — 2026-10-14 JST

The native SwiftUI / Metal app fetched R3D / C3MM directly from Apple's HTTPS
host, decoded in process using the existing independent codec, and rendered on
the iOS 27 simulator on an Apple Silicon Mac. No Linux terrain / decode server
was used by the app. Runtime credentials and raw map tiles are excluded.

`streaming-validation.json` records 121 samples from a 120-second scenario:
Tokyo Tower, rotation at 40 s, movement 450 m east at 65 s, memory warning at
85 s, and relocation to Waikiki at 100 s. The sampler uses measured elapsed
frame time, without capping the interval used for fps statistics.

Validated by `python3 ios/Tests/check_validation.py`:

- Dummy signature vector matches the existing Python acquisition exactly.
- At most 2 simultaneous tile tasks; no acquisition / decode failures.
- No resident-model budget violations: 192 MiB standard, 96 MiB after warning.
- Maximum resident-model estimate: 131.21 MiB. This excludes the interpreter,
  transient decoding arrays, and driver overhead; it is not process RSS.
- Observed fps median 60.00, minimum 59.02 for samples with models displayed.
- z18, z19, z20 models displayed; nonzero vertical layers acquired.
- Models displayed after camera movement and after relocation to Waikiki.

Other validation:

- `WorldChecks.swift`: quadtree partition, moved / rotated views, dateline,
  vertical gaps, shared occupancy index across LODs, rejected mismatched index,
  camera projection and ECEF origin alignment: PASS.
- `test_mobile_decoder.py`: bounded gzip, malformed-data rejection, and original
  mesh XYZ / UV / normals / indices and Splat XYZ retained by the mobile packing:
  3 tests PASS, using 5 freshly acquired R3D fixtures at z18 / z19 / z20.
- Xcode 27 Debug / arm64 iOS Simulator build: PASS.
- Xcode 27 Release / arm64 iPhone build with signing disabled: PASS.

Physical iPhone performance, installation with a developer's signing identity,
App Store distribution, exact Apple pixel parity and exact Apple LOD selection
remain unverified. The CI workflow separately checks source / simulator / device
compilation without requiring private acquisition settings.
