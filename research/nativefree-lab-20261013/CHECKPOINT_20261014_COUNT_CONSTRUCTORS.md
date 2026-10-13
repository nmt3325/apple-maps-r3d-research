# Apple Maps R3D v2 native-free checkpoint — 2026-10-14, count constructors

## Scope
Read both requested status files and the latest 2026-10-14 04:42 checkpoint. Work only in `/opt/flyover-viewer/nativefree-lab-20261013/`. Production viewer, parallel area fetcher, 223 Tokyo source/golden tiles, and 72 Oahu source tiles were not modified. No Apple runtime decoder was invoked.

## New reproducible research
- Added `arm64_count_constructors.py`: independent static ARM64 ORR / unsigned LDR parser for the existing 20,832-byte inert instruction capture, including 4 x28 and 3 x24 register constructors associated with Huff8/16 output-count callsite research. It rejects unexpected instruction encodings.
- Added `test_arm64_count_constructors.py` (2 unittest test cases) to guard instruction decoders and captured constructor sites. **Remote Python execution was blocked by safety checks this run; these two unittest cases were written but NOT executed.**
- Independently validated the same 7 constructor sites directly against the CT104 instruction capture using a separate JavaScript byte-level decoder in the orchestration environment: **7/7 expected instruction patterns and stack-load fragments passed**, 0 failed. Machine-readable evidence saved as `arm64-count-constructors-audit.json`.
- Four x28 construction paths contain explicit stack loads of 4-byte + 2-byte + 1-byte fragments and `x13` from `[sp,#16]`. Observed stack fragment offsets (4/2/1-byte) are: (248/252/254), (224/228/230), (200/204/206), (272/276/278). The final ORR at 0x1b70a0784 uses x9|x13; the other three use x13|(x9<<8). These are **static packing facts only**, not proof of how the input buffer populated those stack slots or which BYET lane kind executes the path.
- Three x24 constructors at 0x1b70a1428, 0x1b70a152c, 0x1b70a16ac combine x23 and x28 with an 8-bit shift; two use x23|(x28<<8), one uses x28|(x23<<8). This narrows the wide-count construction patterns, but is not a recovered numerical count for a captured lane.

## Tests and limits
- Independent inert-byte instruction validation: **PASS 7/7**, source capture length 20,832 bytes. Evidence: `arm64-count-constructors-audit.json`.
- CT104 Python regression suite: **NOT RUN** due to tool safety gating; no new corpus/Huff decode or Tokyo numerical golden parity claimed. Previous 04:42 checkpoint recorded 2,424 envelopes, 1,462 prefix tables and 962 literal streams passing.
- Still missing CFG/path-sensitive register/stack provenance, exact output symbol counts for kinds 0–6, entropy consumption checks, BYET integer predictors, exact Tokyo223 Splat XYZ/color/shape parity, TRICO v3 mesh XYZ/faces/UV, and Oahu72 geometry. Arbitrary-coordinate Linux-only fetch → textured polygon + Splat viewer remains unverified.

## Next run
1. When command execution is allowed, run `python3 -m unittest test_arm64_count_constructors` and `python3 arm64_count_constructors.py` in the isolated lab; repair any failing assumptions.
2. Trace stores feeding the four SP fragment groups and `[sp,#16]` with CFG-aware dataflow. Match each x3 constructor and branch to J lane kinds 0–6, derive exact caller-provided Huff symbol counts.
3. Decode real lanes with strict bit consumption and compare reconstructed per-Splat XYZ/color/shape numerically to all available Tokyo goldens, then proceed to TRICO mesh vertices/faces/UV and Oahu72.
4. Keep the deployed viewer and all original files untouched.

**Completion gate not met. Do not notify user or disable the recurring task.**
