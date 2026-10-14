# iOS surrounding streaming and memory policy

The default loading radius is 600 m. Loading covers 360 degrees and does not
change when the camera rotates. z20 enters at 85 m and remains through 120 m;
z19 enters at 200 m and remains through 240 m. The rest uses z18. Requests
prioritize coarse coverage, facing direction and a two-second motion prediction.
The renderer separately applies the camera frustum, including the far plane.
Models outside the loading region remain for 60 / 40 / 20 seconds according to
distance; needed offscreen models do not expire. Memory pressure may evict sooner.

First display uploads a 1024 px atlas (512 under pressure). A single background
job replaces only the atlas; geometry and the previous atlas remain renderable
until the replacement is ready. z20 targets the original image, subject to an
8192 px hardware-safe ceiling and available memory; z19 targets 2048 and z18 1024.
All textures retain mipmaps and trilinear, derivative-selected sampling. Under
pressure z20 uses 512–1024 and other LODs use up to 512. Resident mips are copied
to smaller atlases without requiring the original CPU cache entry.

Resolution selection excludes the atlas being replaced from resident usage;
upload admission still reserves space for both the old and replacement atlas.
Distant atlases can only shrink during active texture pressure. After a successful
reduction, upgrades wait ten seconds, including when camera movement brings the
tile closer. Further emergency reductions remain available immediately. Once
pressure and the upgrade delay end, the ordinary refinement policy can restore
detail. Stored texture resolution reflects the actual mip dimensions (for example,
an 896 px atlas reduced to a 512 px cap becomes 448 px), rather than the requested cap.

The resident model budget is 192 MiB standard / 96 MiB constrained. Texture
replacement memory is reserved against other uploads. At 80% usage or allocation
failure, distant textures are reduced first; geometry eviction ranks distance,
LOD, last access, bytes, current need and visibility, favoring coarse coverage.
If geometry eviction is still required, the automatic range shrinks, and severe
constrained mode limits refinement to z19. The user's range setting is kept
separate from the automatic effective range. OS memory warnings allow immediate
budget enforcement. Less than 128 MiB OS-reported process headroom also enters
constrained mode for 60 seconds.

A separate CPU LRU retains packed decoded geometry and the original compressed
atlas for up to 60 seconds, bounded to 96 / 24 MiB. Cache hits bypass acquisition
and codec decoding. If an atlas refinement needs an expired entry, the ordinary
bounded request pipeline restores it from the disk cache or network.

The overlay and debug validation report track resident model bytes, CPU cache
bytes, Metal allocated bytes and process physical footprint independently.
Model bytes include allocated atlas storage and geometry buffers, but do not
represent the entire process. Background preparation and previously submitted
Metal frames can temporarily retain additional allocations.

WorldChecks covers 360-degree rotation invariance, four-quadrant acquisition,
partitioning with hysteresis, pressure LOD limits, texture policy, eviction order,
and CPU LRU byte/lifetime bounds, plus stable texture targets, upgrade delays and
restoration after pressure. GPUChecks verifies actual non-power-of-two mip sizes.
GitHub's iOS workflow compiles both simulator
Debug and unsigned iPhone Release, and packages an unsigned IPA. Hardware visual
quality, memory-warning behavior and frame rate still require device validation.
