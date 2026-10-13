# Apple R3D native-free decoder — Huff816 and BYET kind-0 research stage

This bundle adds a clean-room Python decoder for the captured Huff816 `0x61` table format and common `0x24` wrapper. It decodes the compressed Huffman byte stage and handles the observed `0xe1000002` literal path. It does not reconstruct BYET/J lanes, quantized XYZ, material channels, mesh topology, UVs, or the rendered splat model.

The standalone `huff816_nativefree.py` uses only the Python standard library. Its self-test covers a synthetic two-symbol Huff816 stream, the 0x24 wrapper, literal dispatch, and malformed inputs:

```bash
python3 huff816_nativefree.py
```

`audit_huff816_nativefree.py` repeats the corpus check on the user's CT104 capture layout. It depends on the existing read-only R3D framing modules under `/opt/flyover-viewer` and takes one or more `.r3d` directories. Example:

```bash
python3 audit_huff816_nativefree.py /opt/flyover-viewer/native-r3d /path/to/oahu/area_z20 --report huff816-nativefree-report.json
```

`audit_byet_kind0.py` checks a narrow BYET/J case against the saved native Tokyo outputs:

```bash
python3 audit_byet_kind0.py /opt/flyover-viewer/native-r3d /opt/flyover-viewer/decoded-native/all-223 --report byet-kind0-native-golden-report.json
```

Across 223 Tokyo tiles, 21 active kind-0 XYZ lanes each contain exactly three bytes per Splat. Their first N bytes match the low byte of the corresponding native-decoded quantized coordinate on 20 lanes, covering 3,732 of 4,029 point-byte comparisons. The sole mismatch is one Z lane with a constant +1 byte difference for all 297 points; it uses a sparse origin header whose current sign-extension interpretation is unresolved. This confirms only the first N-byte segment in this observed case. The remaining 2N bytes and all other BYET/J kinds are still open.

The audited corpora contain Tokyo 223 tiles and Hilton Oahu 72 tiles. The decoder passed all 2,659 compressed-frame trials with zero Huff816 decode rejections, producing 739,702 bytes. It also identified 1,437 literal Huff816 lanes. The kind-0 result is a native-golden comparison of one byte segment, not a full numeric decode. Remaining headerless/unclassified lanes and all other BYET/J and TRICO stages remain open; Huff816 output bytes have not been matched against Apple's private intermediate buffers.

CT104 copy: `/root/.desktop-mcp/linux-4ebec5ed/work/apple-r3d-independent-audit-20261013/`
