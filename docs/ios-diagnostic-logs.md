# iOS diagnostic logs (JSON Lines schema 1)

Open **設定 → 診断ログ → 詳細ログを書き出す**, then choose **ファイルに保存**,
AirDrop, or another share target. The file is `R3D-diagnostics-<UUID>.jsonl`, UTF-8,
one JSON object per line. Logging is always enabled in Debug and Release. Export
is a stable snapshot; app activity can continue without modifying a shared file.

Six rotating 4 MiB segments retain approximately 24 MiB of recent events across
launches in Application Support/Diagnostics. The oldest events expire first.
Exports include all retained sessions, oldest first, preceded by an
`export.snapshot` record. At most three export snapshots are kept locally.
Filesystem work and export run on a dedicated serial utility queue; export copies
in 1 MiB chunks. The event queue is bounded to 1,024 entries and individual events
to 64 KiB. Oversized/invalid events or queue overload increment `dropped_events`;
I/O errors increment `write_failures`. Both counters describe the current session
and are included in export metadata. A crash-truncated final line is repaired at
the next launch. These are diagnostic logs, not a lossless crash recorder.

Every regular record contains `schema_version`, `session_id`, `sequence`,
`unix_time` (UTC seconds), `uptime_s` (monotonic seconds), `event`, and `fields`.
Records associated with a model have `tile` (style, z, x, y, height layer).
`trace_id` links a single pipeline attempt across actors and download delegates;
a retry has the same trace and a different `attempt` (1-based). Texture work has
its own trace and links back through `source_trace`. Sequence numbers establish
file order inside a session. Duration fields ending in `_ms` use milliseconds.
Logs include geographic origins, camera coordinates and touch positions. Signed
URLs, access keys, request headers, payloads and NSError userInfo/descriptions
are excluded; errors record domain, code and cancellation status.

## Investigating slow acquisition

- `pipeline.queued` records when a tile first becomes eligible, queue position,
  LOD/height, distance and frustum visibility. `pipeline.begin` includes queue
  wait, time since first needed, CPU-cache hit and current concurrency.
- `fetch.begin/end` give total fetch time and outcome (`disk_cache_hit`,
  `negative_cache_hit`, `downloaded`, `empty`, `cancelled`, `error`).
  `cache.disk_read` separates disk/cache actor latency from networking;
  `cache.disk_write_complete.stored` distinguishes write success.
- `network.begin/response/progress/retry` include signing time, timeout limits,
  HTTP status, byte counts, attempt and retry backoff. `network.metrics` reports
  DNS, connection (including TLS), TLS, request, response-wait/TTFB and transfer
  times, connection reuse, protocol and received body bytes. A null timing means
  the platform did not provide that phase, often due to connection reuse.
  Metrics callbacks can arrive after `fetch.end`; correlate by trace, not adjacency.
- `processing.queued/begin` measure preparation-slot waiting. `decode.begin`
  measures decoder actor waiting, and `decode.end` measures codec execution and
  output sizes. The `function` distinguishes geometry decoding from early atlas
  extraction. CPU-cache hits skip fetch and codec work entirely.
- `atlas.prepare_begin/end` measure lightweight atlas preparation, overlapping
  geometry decoding. GPU preparation later reuses that same texture.
- `gpu.prepare_begin/worker_begin/end` separate background dispatch waiting from
  total preparation, with model bytes, triangles, atlas dimensions and mip count.
  `gpu.resident` measures needed-to-resident latency. Admission may instead emit
  `gpu.admission_deferred`, with memory/range evidence.
- `render.tile_first_submitted` measures resident-to-draw and needed-to-draw time.
  It means submitted to Metal, not confirmed onscreen. `render.gpu_complete`
  reports sampled command completion, GPU duration, errors and frame ID.
- `render.tile_first_presented` records the hardware drawable presentation
  callback, including needed-to-presentation milliseconds, a 100 ms deadline,
  and whether the tile belongs to the initial lightweight LOD. The callback's
  observation time is a conservative upper bound. Simulator SDKs lack that
  callback; `render.tile_first_completed` records GPU completion there instead
  and does not claim screen presentation. Both measurements include queue waits.
- `decoder.ready.compiled` confirms whether the compiled array loops loaded.
  `app.model_init.coarse_zoom` and `stream.state.coarse_zoom` identify the
  lightweight LOD even when exports contain several launches or rotated segments.
  `app.model_init.latency_origin = horizontal_plan` means model latency begins
  when its horizontal location enters the plan, including occupancy-index
  discovery. Older logs start after expansion into individual height layers.
- `pipeline.end` terminates every attempt, including cancellation/stale generation,
  with outcome, final stage and total duration. Failed network/codec/GPU work
  also emits error events. `pipeline.cancel_requested` explains plan cancellation.

## Drawing, navigation and memory

`render.interval/frame/gpu_complete` summarize roughly once per second: FPS via
`stream.state`, frame intervals, CPU encoding time, GPU time, backpressure skips,
missing drawables, selected/culled/submitted tiles, triangle/splat counts, coverage
masks and drawable size. Visibility changes log tile lists in bounded chunks.
`stream.residency` inventories resident tiles every five seconds, including LOD,
texture size, cost, distance and current need/visibility. `stream.state` includes
queue age, concurrency, failures, memory budgets and separate CPU cache, resident
GPU model, Metal allocation and process physical-footprint readings.

`input.touch_phase` captures touch count transitions and cancellation.
`navigation.begin/update/release/stop/pan/orbit/zoom` capture every accepted gesture
update, camera state and inertia; beginning a gesture also measures focus picking.
`control.*` records pause, range, quality, elevation, speed, reset, relocation,
settings, reconnect, cache clear and export. One-second camera state samples also
capture continuous inertia/elevation motion. `app.active`, `memory.warning`,
`memory.range_reduced`, `gpu.evict` and `texture.*` explain lifecycle and quality
changes. A GPU eviction records reason, age, distance, visibility, LOD and bytes.

CI's `DiagnosticsChecks.swift` verifies concurrent ordering, parseable JSONL,
immutable export, byte retention, recovery after partial writes, error redaction,
invalid record counts and surfaced export failure. The iOS workflow also compiles
simulator Debug and unsigned iPhone Release including the share sheet.

`python3 audit/summarize_ios_latency.py /path/to/log.jsonl.zip --out /tmp/latency.json`
summarizes each session separately without exporting location coordinates.
Needed-to-event timings include queue time and, for `horizontal_plan` logs,
occupancy discovery. Attempt-to-resident timings exclude
queue time and must not be used to claim the 100 ms end-to-end target.
