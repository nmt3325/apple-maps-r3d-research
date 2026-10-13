# Apple Maps R3D v2: native-free decoder status (CT104)

2026-10-13. This work is independent from the old iOS 27 simulator decoder and does not modify the other extraction thread's workspace.

## Confirmed facts
- Old [retroplasma/flyover-reverse-engineering](https://github.com/retroplasma/flyover-reverse-engineering) is a **pure Go, no-iOS** Flyover decoder for **C3M v3**. Its `pkg/fly/c3m/c3m.go` requires a C3M header and explicitly declines C3M v1/v2, while `pkg/fly/c3m/internal` contains Huffman and edgebreaker decoder routines.
- Current `style=98` captures start with **3d 96 59 2e 02 00 00 00** (Apple R3D v2), not legacy C3M. No working direct R3D mesh/splat parser was found in the inspected projects.
- New `/opt/flyover-viewer/nativefree_extract_heic.py` extracts embedded HEIC ISOBMFF streams (ftyp/meta/mdat) **straight from captured R3D network bytes**, with Python 3 standard library only. It validates and reports the local rotation matrix and ECEF translation as well.
- Tokyo Dome R3D corpus: 223/223 validated with valid R3D position transforms, 669 HEIC images found (3 per R3D). The **first HEIC** of all 223 tiles was verified byte-for-byte (SHA-256) against the 223 HEIC files previously extracted by the iOS 27 native decoder: 223 pass, 0 mismatch.
- Hawaii Hilton capture: 72/72 network R3Ds valid, **216 HEIC streams recovered** (3 per tile), 4,149,602 bytes of total HEIC data. No iOS code used. Output: `/opt/flyover-viewer/nativefree-oahu-textures/`; summary: `/opt/flyover-viewer/nativefree-oahu-report.json`.
- Sample of Hawaii tile `s98_z20_x64551_y460816_h0` has three HEIC images: 896x832 color aerial atlas, 448x416 high-contrast monochrome, 448x416 low-contrast monochrome. Roles of latter two (e.g. masks/auxiliary materials) are **not yet proven**.
- Native-free Tokyo comparison report: `/opt/flyover-viewer/nativefree-verified-tokyo.json`.

## Run
Inspect a captured R3D without writing:
```bash
python3 /opt/flyover-viewer/nativefree_extract_heic.py /path/to/tile.r3d
```
Extract every HEIC from a directory:
```bash
python3 /opt/flyover-viewer/nativefree_extract_heic.py /path/to/r3d_directory --out-dir /path/to/private/output --report /path/to/result.json
```
Verify against outputs from older native decoder (for migration testing only):
```bash
python3 /opt/flyover-viewer/nativefree_extract_heic.py /opt/flyover-viewer/native-r3d --verify-native-dir /opt/flyover-viewer/decoded-native/c3m-all-223
```

## Still missing to eliminate the iOS dependency
1. Independent parsing of R3D v2 geometry and compressed triangle mesh / UV / indices / normals. Do not confuse with C3M v3 or C3M v2.
2. R3D per-splat point/attribute and exact triangle generation (formerly Apple `createSplats`).
3. Prove/port block compression and topology against the **already saved 223 native-decoded fixtures**, comparing exact vertex counts, array contents and mesh checksums. Reusing legacy Huffman and edgebreaker code is a hypothesis to test, **not yet established as compatible**.
4. Integrate an independent parser into `fetch_area_98.py` to transform the newly fetched Hawaii region straight into native C3M and splat browser layers without any macOS/iOS Simulator step.

**Status:** Textures and ECEF transforms: native-free DONE. Original polygon mesh / UV / splat generation: native-free NOT DONE. Existing full-feature viewer continues to work with its earlier iOS-decoded Tokyo assets. Do not state the Hawaii geometry is already decoded natively.
