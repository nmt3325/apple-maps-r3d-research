"""Read-only 0x24 Huff envelope corpus audit (Tokyo223 + Oahu72)."""
import json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, "/opt/flyover-viewer")
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from huff816_envelope import split_envelope

tokyo = sorted(Path("/opt/flyover-viewer/native-r3d").glob("*.r3d"))
oahu = sorted(Path("/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20").rglob("*.r3d"))
counts = Counter()
errors = []
for path in tokyo + oahu:
    raw = path.read_bytes()
    splat = dissect(raw)["splatStream"]
    for frame in splat["blocks"]:
        byet = frame["byet"]
        start = splat["offset"] + byet["compressedPayloadRelativeOffset"]
        j = raw[start:start + byet["compressedPayloadBytes"]]
        lanes = split_j(j, 12 if frame["index"] == 0 else 32)["descriptors"]
        for d in lanes:
            n = d["compressedBytes"]
            lane = j[d["compressedOffset"]:d["compressedOffset"]+n]
            if n < 20 or lane[4:8] != bytes.fromhex("00000024"):
                continue
            try:
                segments = split_envelope(lane, offset=4)
                counts["segmented" if segments[0].symbol_count is not None else "single"] += 1
                counts["segments"] += len(segments)
            except Exception as exc:
                counts["errors"] += 1
                if len(errors) < 8:
                    errors.append([path.name, frame["index"], d["lane"], str(exc)])
print(json.dumps({"tokyo":len(tokyo),"oahu":len(oahu),
                  "counts":dict(counts),"examples":errors},indent=2))
