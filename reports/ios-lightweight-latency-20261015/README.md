# Lightweight model latency checkpoint

Source: `d0021005586373a6e2514b2399f9211c2a6b31ad`.
Status: **the 100 ms loading-and-drawing target is not achieved**.
Horizontal-only distance clipping is implemented and tested.

## Implementation

- The independent decoder's audited array loops are compiled as a built-in
  CPython module, not replaced with an Apple private decoder. Python framing,
  variant dispatch, invariant validation, and a source-only fallback remain.
- Two decoder workers release the GIL only during C++ operations. Inputs stay
  alive while unlocked; exceptions restore the GIL before touching Python.
- Initial coverage uses original server z16 models and 256 px atlases, followed
  by the existing z18/z19/z20 detail partition. All occupied heights remain
  eligible. Child coverage uses a buffer supporting 256 rectangles.
- Lightweight atlas preparation overlaps geometry decoding. The validated
  final model reuses that texture. Processing/network limits remain two each,
  with at most four pending requests.
- Projection has no finite far plane. Mesh/Splat fragments and picking use XZ
  distance, independent of altitude. Normal camera side/near clipping remains.

## Simulator Measurement

Real Apple network acquisition, Xcode 27.0, iOS 27.0 simulator, arm64 Debug
application with the C++ loops compiled at O3. No simultaneous build or corpus
test ran during these two sessions. The cold run followed app removal and
installation; the warm run relaunched the app with its raw disk cache intact.
Neither run was a prepared CPU/GPU-cache replay.

The initial requested radius was 600 m. Both runs entered the existing
96 MiB constrained policy after a memory warning, at 327 ms and 97 ms from log
start respectively. Their effective radii subsequently fell to approximately
120 m. These are **not sustained fixed-600 m or iPhone benchmarks**. Observed
steady-state median FPS was approximately 60; that is not a 100 ms latency proof.

| Measurement | Cold Median / p95 / Max (ms) | Raw-Cache Median / p95 / Max (ms) |
|---|---:|---:|
| Needed to first submitted GPU command, 6 models | 251.7 / 300.5 / 383.6 | 169.2 / 217.3 / 250.7 |
| Needed to first GPU command completion, 6 models | 253.7 / 302.5 / 385.8 | 171.3 / 218.7 / 252.6 |
| Needed to GPU residency, 12 models | 358.2 / 550.0 / 572.6 | 232.3 / 343.4 / 354.8 |
| Geometry decoder, 12 models | 32.8 / 40.5 / 44.2 | 42.5 / 47.3 / 47.5 |
| Overlapped atlas preparation, 12 models | 21.2 / 22.6 / 36.4 | 20.4 / 48.2 / 49.0 |
| Final GPU preparation, 12 models | 0.5 / 2.2 / 20.6 | 0.6 / 4.7 / 14.5 |
| Model network response, 12 models | 71.6 / 86.5 / 107.4 | No network requests |

All six observed first GPU completions exceeded 100 ms in each run. Each run
had 57 atlas replacements across 57 different tiles and no non-cancellation
errors. The earlier texture oscillation fix remains in place.

"Needed" starts when a horizontal location enters the loading plan, before
occupancy discovery and queue waiting. It does not include process startup
before that plan or the time until the next planning tick (up to 50 ms).
Older measurements beginning after occupancy expansion are not directly
comparable. p95 uses index `int((n-1)*0.95)`, not an interpolated percentile;
six rendered models are a small sample.

The simulator does not expose the drawable presentation callback. GPU command
completion is **not confirmed screen presentation**. Hardware builds emit
`render.tile_first_presented` when the containing drawable is presented; that
callback alone does not establish pixel visibility for an occluded tile.

Attempt-to-resident excludes discovery/queue waiting and is not the target.
Its warm-run median was 79.8 ms, but reporting that as end-to-end success would
be incorrect. A cold network response alone exceeded 100 ms. Unconditional
100 ms delivery of uncached remote content cannot be guaranteed by this client.

Aggregated evidence: [simulator-latency.json](simulator-latency.json).
No raw diagnostic logs, acquired tiles, signed URLs, or credentials are included.

## Verification

- All 223 retained Tokyo originals: complete mobile output dictionaries match
  the Python implementation byte for byte, including JSON and original atlas.
  Seven accelerator tests passed in 169.264 s, including two-worker original
  tile replay, duplicate-edge adjacency, numeric parity, malformed input, and
  GIL restoration after exceptions in unlocked loops.
- z16/z17/z18 originals: seven accelerator tests and three mobile packing tests
  passed. Five original z18/z19/z20 fixtures also passed mobile packing checks.
  Early atlas extraction matches the ordinary decoder's atlas bytes.
- Numeric codec: ten pass, one unavailable release-reference-corpus test skips,
  for both compiled and source-only paths. This is not a new native-golden audit.
- World, Navigation, Pipeline, Diagnostics, and actual Metal GPU checks pass.
  Pixel readback tests cover Mesh and Splat clipping at 10/20 km altitude,
  outside-radius rejection, and the final (256th) child mask. Atlas reuse,
  original image refinement, geometry retention, and odd mip sizes also pass.
- Six latency-report tests pass, including retained previous sessions, rotated
  files, incomplete live tails, byte limits, atlas exclusion, and monotonic time.
- Simulator Debug and unsigned iPhone arm64 Release builds pass. Existing
  Sendable/orientation and deprecated diagnostic-test API warnings remain.

## Device Artifact And Next Work

Local unsigned IPA: `/tmp/r3d-fetch-device/R3DExplorer-lightweight-native-unsigned.ipa`
(18,813,588 bytes). SHA-256:
`28e086e669a53cd3cc4516d9d98c1f882170fa57e4e5ec2f210c58c51a8be098`.
The device binary contains `_PyInit__r3d_accel`; bundled adapter/accelerator-loader
sources match this checkout. The package validator passed. Device signing and
on-device execution are still required.

Keep the latency goal open. Measure signed hardware cold acquisition, disk-cache
restart, and resident-cache movement separately, including real presentation
callbacks and memory state. Remaining work includes discovery/processing queue
latency and reuse of prepared lightweight data. Clarify whether the requested
100 ms guarantee includes uncached locations, without silently narrowing it.
Do not infer a controlled speedup percentage from these different sessions.
