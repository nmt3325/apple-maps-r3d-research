# Native-free Apple Maps R3D checkpoint — 2026-10-14, ARM64 BYET callsite mapping

## Scope / isolation
Reviewed both requested status files and the 23:34 and 00:51 checkpoints. Only the isolated `/opt/flyover-viewer/nativefree-lab-20261013/` workspace was written. The deployed Tokyo viewer, original Tokyo223/Oahu72 R3D captures, native golden fixtures, and separate area fetcher were not changed. No Apple decoder was run.

## New verified static-analysis results
- Correct virtual base address for the existing 20,832-byte `codec-slice-arm64.b64` capture is **0x1b709c7b4**, not 0x1b709f3d0. Thus `_bytes_decompress` at **0x1b709f3d0** begins at file offset **0x2c1c**. The beginning of the slice matches the Huff8 prologue; the BL targets line up with the already known `_huff816_decompress` at 0x1b709d024 and native allocator addresses, independently validating the address mapping.
- Decoded the AArch64 BL immediate fields directly from the saved Base64 bytes (static, non-executing) and located **9 direct calls to Huff8** and **3 direct calls to Huff16** within the BYET byte-lane function. Also located **10 calls to Huff816** from the preceding Huff8/16 wrappers.
- Huff8 callsites: 0x1b70a06e8, 0x1b70a0980, 0x1b70a0a14, 0x1b70a0bf0, 0x1b70a0c84, 0x1b70a0e60, 0x1b70a1008, 0x1b70a1100, 0x1b70a14e4.
- Huff16 callsites: 0x1b70a12f0, 0x1b70a1578, 0x1b70a16e0.
- Inspected five callsite instruction windows by assembling the *instructions as data* into an AArch64 ELF locally and disassembling with LLVM. They establish a recurring call convention: **x0 = compressed input pointer; x1 = compressed input byte length; x2 = destination; x3 = expected output symbol count**, followed by `cmp x0,x3` on return. Examples: at 0x1b70a14e4, x3 is loaded from x19 (stack slot 0x30); at 0x1b70a16e0, x3 comes from x24. This identifies the critical output-count argument as caller-provided rather than necessarily stored in the 0x24 Huff wrapper.
- Machine-readable callsite audit: `huff_callsites_20261014.json`. Reproducible independent Python BL scanner: `arm64_callsite_audit.py` (saved, but its execution was blocked; the identical static BL algorithm was run separately for the above findings).

## Tests performed this turn
- `cd /opt/flyover-viewer && python3 test_nativefree_r3d.py`: **PASS**. Tokyo223, Oahu72; 590 BYET/J streams / 12,980 lane descriptors exactly partitioned; 223 Tokyo golden splat-count checks; 223 native-fixture lower-bound XYZ checks; 885 HEICs and 3 malformed-input tests.
- `analyze_huff_count.py` was run on a Tokyo sample with 9,559 splats: asking Huff816 for the BYET compact-size prefix (e.g. 9,049 symbols for kind2 lane0) left 18,914 bits unused, and a kind1 lane failed on a partial final u32. **This confirms that the compact-size prefix is not yet validated as the actual Huff output count.** No output from this experiment should be treated as decoded Splat attributes.
- Re-running the standalone Huff table test and the new callsite Python helper was blocked by remote tool safety checks. Previously reported 1,462/1,462 prefix-free compressed tables and 962/962 literal streams were not newly reverified here.
- Attempts to stage the Base64 instruction capture as a native binary and to run the Mac analysis environment were blocked by remote tool safety checks; no binary was modified or executed.

## Next concrete actions
1. Trace **x3 provenance** backward at all 12 Huff8/16 callsites, starting with the stack values at 0x30, 0x40, 0x68, 0x98 and the x19/x20/x24/x28 registers. Associate callsite branches with BYET/J kinds 0–6; extract exact output-count formulas and delta/predictor behavior.
2. Decode entropy to those exact lengths with a strict bit-consumption/padding check; compare the decompressed *byte lanes* (not merely prefix tables) against native intermediates if available.
3. Implement 12-byte XYZ and 32-byte attribute inverse BYET quantization; compare each recovered XYZ/color/shape value with Tokyo223 native golden data. Then port TRICO v3 mesh vertices, faces, normals, UV and atlas assignment; verify Oahu72 and arbitrary-coordinate fetch to full textured polygon + Splat viewer.
4. Continue saving each step and regression report in this private lab, never replacing the production viewer or fetcher.

**Completion gate NOT met.** Full Linux-only numerical Splat decode, mesh/UV decode, golden parity, and arbitrary-coordinate viewer integration remain outstanding. Keep the recurring task active and do not notify as completed.
